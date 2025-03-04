import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Create a superuser for Django Admin using environment variables'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not email or not password:
            self.stdout.write(self.style.ERROR(
                'Environment variables DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, '
                'and DJANGO_SUPERUSER_PASSWORD must be set'
            ))
            return

        try:
            # Check if the user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'User with username {username} already exists, updating...'))
                user = User.objects.get(username=username)
                user.email = email
                user.set_password(password)
                user.is_staff = True
                user.is_superuser = True
                user.save()
            else:
                # Create the superuser
                User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f'Superuser {username} created successfully'))
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error creating superuser: {e}')) 