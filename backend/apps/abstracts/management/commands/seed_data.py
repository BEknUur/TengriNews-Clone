# third-part imports
import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction
from faker import Faker

# project imports
from apps.accounts.models import CustomUser
from apps.main.models import Category, Tag, Article, Comment, Reaction

fake = Faker("ru_RU")


class Command(BaseCommand):
    help = "Seed the database "

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=10)
        parser.add_argument("--categories", type=int, default=6)
        parser.add_argument("--tags", type=int, default=12)
        parser.add_argument("--articles", type=int, default=20)
        parser.add_argument("--comments", type=int, default=40)
        parser.add_argument("--clear", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            self._clear()

        users = self._seed_users(options["users"])
        categories = self._seed_categories(options["categories"])
        tags = self._seed_tags(options["tags"])
        articles = self._seed_articles(options["articles"], users, categories, tags)
        self._seed_comments(options["comments"], articles, users)
        self._seed_reactions(articles, users)

        self.stdout.write(self.style.SUCCESS("\nSeed complete!"))

    def _clear(self):
        Reaction.objects.all().delete()
        Comment.objects.all().delete()
        Article.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()

    def _seed_users(self, count: int) -> list[CustomUser]:

        users = []

        admin, _ = CustomUser.objects.get_or_create(
            email="admin@tengri.kz",
            defaults={
                "first_name": "Admin",
                "last_name": "Tengri",
                "role": CustomUser.ADMIN,
                "is_staff": True,
                "is_active": True,
            },
        )
        admin.set_password("admin123")
        admin.save()

        for _ in range(count):
            email = fake.unique.email()
            role = random.choice([CustomUser.USER, CustomUser.USER, CustomUser.EDITOR])
            user = CustomUser.objects.create(
                email=email,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=role,
                is_active=True,
            )
            user.set_password("password123")
            user.save()
            users.append(user)

        self.stdout.write(self.style.SUCCESS(f"  {count + 1} users created"))
        return users

    def _seed_categories(self, count: int) -> list[Category]:
        self.stdout.write("Creating categories...")
        base_names = [
            "Политика",
            "Экономика",
            "Спорт",
            "Технологии",
            "Общество",
            "Культура",
            "Наука",
            "Бизнес",
        ]
        categories = []

        for name in base_names[:count]:
            slug = slugify(name) or fake.slug()
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
            categories.append(cat)

        if len(categories) >= 2:
            child_names = ["Футбол", "IT-новости", "Финансы"]
            for child_name in child_names:
                slug = slugify(child_name) or fake.slug()
                child, _ = Category.objects.get_or_create(
                    slug=slug,
                    defaults={"name": child_name, "parent": random.choice(categories)},
                )
                categories.append(child)

        self.stdout.write(self.style.SUCCESS(f"  {len(categories)} categories created"))
        return categories

    def _seed_tags(self, count: int) -> list[Tag]:
        self.stdout.write("Creating tags...")
        tag_names = set()
        while len(tag_names) < count:
            tag_names.add(fake.word().capitalize())

        tags = []
        for name in tag_names:
            slug = slugify(name) or fake.slug()
            tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
            tags.append(tag)

        self.stdout.write(self.style.SUCCESS(f"  {len(tags)} tags created"))
        return tags

    def _seed_articles(
        self,
        count: int,
        users: list[CustomUser],
        categories: list[Category],
        tags: list[Tag],
    ) -> list[Article]:
        self.stdout.write("Creating articles...")
        articles = []

        for _ in range(count):
            title = fake.sentence(nb_words=6).rstrip(".")
            slug = slugify(title)
            if not slug or Article.objects.filter(slug=slug).exists():
                slug = f"{slug}-{fake.uuid4()[:8]}"

            is_published = random.random() > 0.2

            article = Article.objects.create(
                title=title,
                slug=slug,
                excerpt=fake.paragraph(nb_sentences=2),
                content="\n\n".join(fake.paragraphs(nb=5)),
                author=random.choice(users),
                category=random.choice(categories + [None]),
                is_published=is_published,
                view_count=random.randint(0, 5000),
            )
            article.tags.set(
                random.sample(tags, k=random.randint(1, min(4, len(tags))))
            )
            articles.append(article)

        self.stdout.write(self.style.SUCCESS(f"  {count} articles created"))
        return articles

    def _seed_comments(
        self,
        count: int,
        articles: list[Article],
        users: list[CustomUser],
    ) -> None:
        self.stdout.write("Creating comments...")
        published = [a for a in articles if a.is_published]
        if not published:
            return

        top_comments = []
        created = 0

        for _ in range(count):
            article = random.choice(published)
            parent = random.choice(top_comments + [None]) if top_comments else None

            if parent and parent.article != article:
                parent = None

            comment = Comment.objects.create(
                article=article,
                user=random.choice(users),
                parent=parent,
                content=fake.sentence(nb_words=random.randint(5, 20)),
            )
            if parent is None:
                top_comments.append(comment)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"  {created} comments created"))

    def _seed_reactions(
        self,
        articles: list[Article],
        users: list[CustomUser],
    ) -> None:
        self.stdout.write("Creating reactions...")
        types = [Reaction.LIKE, Reaction.DISLIKE, Reaction.LOVE, Reaction.LAUGH]
        published = [a for a in articles if a.is_published]
        created = 0

        for article in published:
            reactors = random.sample(users, k=random.randint(1, min(5, len(users))))
            for user in reactors:
                _, ok = Reaction.objects.get_or_create(
                    user=user, article=article, defaults={"type": random.choice(types)}
                )
                if ok:
                    created += 1

        self.stdout.write(self.style.SUCCESS(f"  {created} reactions created"))
