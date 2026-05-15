from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_articleauditlog"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="article",
            index=models.Index(
                fields=["author", "-created_at"],
                name="main_art_author_created_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="article",
            index=models.Index(
                fields=["category", "-created_at"],
                name="main_art_category_created_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="article",
            index=models.Index(fields=["-created_at"], name="main_art_created_idx"),
        ),
    ]
