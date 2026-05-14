from django.test import TransactionTestCase
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.apps import apps


class TestNormalizeSlugsMigration(TransactionTestCase):
    """Integration test: apply the normalize_slugs data migration and verify output."""

    migrate_from = [("main", "0003_merge_0002_alter_reaction_type_0002_bookmark_and_more")]
    migrate_to = [("main", "0004_normalize_slugs")]

    def setUp(self):
        # Migrate down to the state before our migration and create test data
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        state = executor.loader.project_state(self.migrate_from).apps
        Article = state.get_model("main", "Article")
        Category = state.get_model("main", "Category")
        Tag = state.get_model("main", "Tag")

        # create test records that will require normalization/unique-fixing
        Category.objects.create(name="ТестКатегория", slug="")
        Category.objects.create(name="ТестКатегория", slug="")
        Tag.objects.create(name="ТестТег", slug="")
        # two articles with same title
        Article.objects.create(title="Тестовая статья", slug="")
        Article.objects.create(title="Тестовая статья", slug="")

    def test_apply_migration_and_idempotency(self):
        executor = MigrationExecutor(connection)
        # apply the migration under test
        executor.migrate(self.migrate_to)

        # get current models and verify
        Article = apps.get_model("main", "Article")
        Category = apps.get_model("main", "Category")
        Tag = apps.get_model("main", "Tag")

        # all slugs should be non-empty
        articles = list(Article.objects.all())
        assert articles, "No articles created in migration test setup"
        article_slugs = [a.slug for a in articles]
        assert all(s and s.strip() for s in article_slugs)
        assert len(article_slugs) == len(set(article_slugs)), "Article slugs must be unique"

        # categories/tags also
        cat_slugs = [c.slug for c in Category.objects.all()]
        tag_slugs = [t.slug for t in Tag.objects.all()]
        assert all(s and s.strip() for s in cat_slugs)
        assert len(cat_slugs) == len(set(cat_slugs))
        assert all(s and s.strip() for s in tag_slugs)

        # idempotency: applying migration again should not change slugs
        before = {"articles": article_slugs}
        executor.migrate(self.migrate_to)
        after_articles = [a.slug for a in Article.objects.all()]
        assert before["articles"] == after_articles
