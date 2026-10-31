import game.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Participant",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                    ("nickname", models.CharField(max_length=32, verbose_name="Никнейм")),
                    ("created_at", models.DateTimeField(auto_now_add=True)),
                    ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="participant", to=settings.AUTH_USER_MODEL))],
        ),
        migrations.CreateModel(
            name="Event",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                    ("title", models.CharField(max_length=120, verbose_name="Название")),
                    ("join_code", models.CharField(default=game.models.make_join_code, max_length=6, unique=True, verbose_name="Код подключения")),
                    ("is_active", models.BooleanField(default=True, verbose_name="Приём участников открыт")),
                    ("is_finished", models.BooleanField(default=False, verbose_name="Завершено")),
                    ("created_at", models.DateTimeField(auto_now_add=True)),
                    ("host", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="hosted_events", to=settings.AUTH_USER_MODEL)),
                    ("participants", models.ManyToManyField(blank=True, related_name="events", to="game.participant"))],
        ),
        migrations.CreateModel(
            name="Activity",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                    ("title", models.CharField(max_length=120, verbose_name="Название интерактива")),
                    ("description", models.TextField(blank=True, verbose_name="Описание")),
                    ("created_at", models.DateTimeField(auto_now_add=True)),
                    ("event", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="activities", to="game.event"))],
            options={"ordering": ["created_at"]},
        ),
        migrations.CreateModel(
            name="ScoreEntry",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                    ("points", models.PositiveIntegerField(verbose_name="Очки")),
                    ("awarded_at", models.DateTimeField(auto_now_add=True)),
                    ("activity", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scores", to="game.activity")),
                    ("awarded_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="awarded_scores", to=settings.AUTH_USER_MODEL)),
                    ("participant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="score_entries", to="game.participant"))],
            options={"ordering": ["-awarded_at"]},
        ),
    ]
