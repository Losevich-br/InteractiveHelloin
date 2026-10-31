"""Создаёт (или обновляет) администратора-ведущего из переменных окружения.

Нужно для бесплатного тарифа Render, где нет Shell и нельзя выполнить
`createsuperuser` вручную. Команда вызывается из build.sh при каждом деплое.

Переменные:
    DJANGO_SUPERUSER_USERNAME — логин ведущего
    DJANGO_SUPERUSER_PASSWORD — пароль ведущего
    DJANGO_SUPERUSER_EMAIL    — почта (необязательно)

Если переменные не заданы, команда ничего не делает.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создать или обновить суперпользователя из переменных окружения"

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()

        if not username or not password:
            self.stdout.write("DJANGO_SUPERUSER_USERNAME/PASSWORD не заданы — пропускаю создание админа.")
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={"email": email})
        user.is_staff = True
        user.is_superuser = True
        if email:
            user.email = email
        # Пароль синхронизируем с переменной окружения: поменяли её в Render — поменялся пароль.
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(
            f"Суперпользователь «{username}» {'создан' if created else 'обновлён'}."
        ))
