# Generated by Django 5.1.4 on 2025-02-02 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("admin_ls", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Protein",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("sequence", models.TextField()),
                ("function", models.TextField()),
                ("source", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "category",
                    models.CharField(
                        choices=[("enzyme", "Enzyme"), ("antibody", "Antibody")],
                        default="enzyme",
                        max_length=10,
                    ),
                ),
            ],
        ),
    ]
