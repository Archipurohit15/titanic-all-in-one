import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update the admin user from environment variables"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.environ['DJANGO_SUPERUSER_USERNAME']
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
        password = os.environ['DJANGO_SUPERUSER_PASSWORD']

        user, created = User.objects.get_or_create(username=username)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()
        self.stdout.write(f"Admin {'created' if created else 'updated'}: {username}")