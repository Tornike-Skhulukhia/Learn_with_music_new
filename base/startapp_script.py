"""
Here you can create some other initial objects in database
if you need them (probably more useful in development)
"""
# flake8: noqa
import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base.settings")
django.setup()

from django.contrib.auth.models import User


def run_migrations():
    # run migrations
    os.system("python3 manage.py makemigrations")
    os.system("python3 manage.py migrate")

    # add more calls like that with specific apps, if for some reason it does not work


def make_sure_test_user_exists():
    try:
        # create testing user
        user = User.objects.create_user("admin", password="1")
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print("Test User created")
    except Exception:
        print("Can not recreate test user")


# GO
run_migrations()
make_sure_test_user_exists()
