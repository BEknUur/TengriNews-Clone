"""Seed command with safer and idempotent behavior.

Enhancements in this version:
- production guard (requires --force to run when DEBUG is False)
- confirmation prompt for destructive `--clear` (can be bypassed with --noinput or --force)
- idempotent user creation (get_or_create)
- idempotent article creation/update (update_or_create by slug)
"""

# Python modules
import random
import sys
from typing import Any

# Django modules
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

# Third-party modules
from faker import Faker

# Project modules
from apps.accounts.models import CustomUser
from apps.main.models import Article, Category, Comment, Reaction, Tag

fake = Faker("ru_RU")


class Command(BaseCommand):
    """Command class."""

    help = "Seed the database with demo data (safe, idempotent-ish)."

    def add_arguments(self, parser: Any) -> Any:
        """Register custom CLI arguments for this management command."""
        parser.add_argument("--users", type=int, default=10)
        parser.add_argument("--categories", type=int, default=6)
        parser.add_argument("--tags", type=int, default=12)
        parser.add_argument("--articles", type=int, default=20)
        parser.add_argument("--comments", type=int, default=40)
        parser.add_argument("--clear", action="store_true", help="Clear seeded data before seeding")
        parser.add_argument("--noinput", action="store_true", help="Do not prompt for interactive confirmation")
        parser.add_argument("--force", action="store_true", help="Force run even when DEBUG is False")

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> Any:
        """Execute the management command workflow using parsed options."""
        # Production guard
        if not settings.DEBUG and not options.get("force"):
            self.stderr.write("Refusing to run seed in non-debug environment. Use --force to override.")
            sys.exit(1)

        if options.get("clear"):
            if not options.get("noinput") and not options.get("force"):
                confirm = input("This will DELETE seeded data. Type 'yes' to continue: ")
                if confirm.lower() != "yes":
                    self.stdout.write("Aborted.")
                    return
            self._clear()

        users = self._seed_users(options["users"])
        categories = self._seed_categories(options["categories"])
        tags = self._seed_tags(options["tags"])
        articles = self._seed_articles(options["articles"], users, categories, tags)
        self._seed_comments(options["comments"], articles, users)
        self._seed_reactions(articles, users)

        self.stdout.write(self.style.SUCCESS("\nSeed complete!"))

    def _clear(self) -> Any:
        """Run the internal helper that handles clear."""
        Reaction.objects.all().delete()
        Comment.objects.all().delete()
        Article.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING("Cleared seeded data (non-superusers removed)."))

    def _seed_users(self, count: int) -> list[CustomUser]:
        """Run the internal helper that handles seed users (idempotent by email)."""
        users = []

        admin, _ = CustomUser.objects.get_or_create(
            email="admin@tengri.kz",
            defaults={
                "first_name": "Admin",
                "last_name": "Tengri",
                "role": CustomUser.Role.ADMIN,
                "is_staff": True,
                "is_active": True,
            },
        )
        admin.set_password("admin123")
        admin.save()

        created = 0
        for i in range(count):
            # deterministic-ish email to avoid duplicates across runs
            email = f"seed_user_{i+1}@example.test"
            first = fake.first_name()
            last = fake.last_name()
            role = random.choice([
                CustomUser.Role.USER,
                CustomUser.Role.USER,
                CustomUser.Role.EDITOR,
            ])
            user, created_flag = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "role": role,
                    "is_active": True,
                },
            )
            if created_flag:
                user.set_password("password123")
                user.save()
                created += 1
            users.append(user)

        self.stdout.write(self.style.SUCCESS(f"  {count + 1} users ensured ({created} created)") )
        return users

    def _seed_categories(self, count: int) -> list[Category]:
        """Run the internal helper that handles seed categories."""
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
        """Run the internal helper that handles seed tags."""
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
        """Run the internal helper that handles seed articles (idempotent by slug)."""
        self.stdout.write("Creating articles...")
        articles = []

        for i in range(count):
            title = fake.sentence(nb_words=6).rstrip(".")
            base_slug = slugify(title) or f"article-{i+1}"
            # create deterministic slug to avoid random suffix on each run
            slug = f"{base_slug}-{i+1}"

            is_published = random.random() > 0.2

            defaults = {
                "title": title,
                "excerpt": fake.paragraph(nb_sentences=2),
                "content": "\n\n".join(fake.paragraphs(nb=5)),
                "author": random.choice(users),
                "category": random.choice(categories + [None]),
                "is_published": is_published,
                "view_count": random.randint(0, 5000),
            }

            article, created_flag = Article.objects.update_or_create(slug=slug, defaults=defaults)
            # ensure tags are present (idempotent)
            article.tags.set(random.sample(tags, k=random.randint(1, min(4, len(tags)))))
            articles.append(article)

        self.stdout.write(self.style.SUCCESS(f"  {count} articles ensured"))
        return articles

    def _seed_comments(
        self,
        count: int,
        articles: list[Article],
        users: list[CustomUser],
    ) -> None:
        """Run the internal helper that handles seed comments."""
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
        """Run the internal helper that handles seed reactions."""
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