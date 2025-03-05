import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Create a superuser for Django Admin using environment variables'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('===== STARTING SUPERUSER CREATION PROCESS ====='))
        
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        
        self.stdout.write(self.style.SUCCESS(f'Env variables found: Username: {username is not None}, Email: {email is not None}, Password: {password is not None}'))

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
                self.stdout.write(self.style.SUCCESS(f'Superuser {username} updated successfully'))
            else:
                # Create the superuser
                User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f'Superuser {username} created successfully'))
            
            # Verify the user exists
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                self.stdout.write(self.style.SUCCESS(
                    f'VERIFICATION: User exists with username: {user.username}, '
                    f'is_staff: {user.is_staff}, is_superuser: {user.is_superuser}'
                ))
            else:
                self.stdout.write(self.style.ERROR('VERIFICATION FAILED: User does not exist after creation/update attempt!'))
                
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error creating superuser: {e}'))
            
        self.stdout.write(self.style.SUCCESS('===== COMPLETED SUPERUSER CREATION PROCESS =====')) 