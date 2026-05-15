import factory
from apps.main.models import (
    Article,
    Category,
    Tag,
    Comment,
    Reaction,
    Bookmark,
    ArticleAuditLog,
)
from apps.accounts.tests.factories import UserFactory

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    name = factory.Faker("word")
    slug = factory.LazyAttribute(lambda o: o.name.lower())

class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
    name = factory.Faker("word")
    slug = factory.LazyAttribute(lambda o: o.name.lower())

class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article
    title = factory.Faker("sentence", nb_words=6)
    slug = factory.LazyAttribute(lambda o: o.title.replace(" ", "-").lower())
    excerpt = factory.Faker("paragraph", nb_sentences=2)
    content = factory.Faker("text")
    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    is_published = True
    view_count = 0

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Allow explicit `author=None` in tests: create a real object (with a temp
        # author to satisfy DB constraints) then set `author=None` on the returned
        # instance so serializers that expect a missing author can be tested.
        if "author" in kwargs and kwargs["author"] is None:
            # Provide a temporary real user for DB insertion, then set author
            # to None on the returned instance (do NOT save) so tests can
            # assert behavior for missing author without violating DB constraints.
            temp_user = UserFactory()
            kwargs["author"] = temp_user
            inst = super()._create(model_class, *args, **kwargs)
            inst.author = None
            return inst
        return super()._create(model_class, *args, **kwargs)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)
        else:
            t = TagFactory()
            self.tags.add(t)

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment
    article = factory.SubFactory(ArticleFactory)
    user = factory.SubFactory(UserFactory)
    content = factory.Faker("sentence")

class ReactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reaction
    article = factory.SubFactory(ArticleFactory)
    user = factory.SubFactory(UserFactory)
    type = Reaction.LIKE


class BookmarkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bookmark

    user = factory.SubFactory(UserFactory)
    article = factory.SubFactory(ArticleFactory)


class ArticleAuditLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ArticleAuditLog

    article = factory.SubFactory(ArticleFactory)
    actor = factory.SubFactory(UserFactory)
    action = ArticleAuditLog.Action.CREATED
    snapshot = {}