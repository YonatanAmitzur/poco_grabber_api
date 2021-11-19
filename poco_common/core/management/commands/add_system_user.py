"""
A Django management command to add the BlueVine "system" user if it doesn't already exist.
"""

from django.core.management.base import BaseCommand
from django.db import connection

from poco_common.core.models import User


class Command(BaseCommand, object):
    """
    A Django management command to add the PoCo "system" user if it doesn't already exist.
    """
    help = """A Django management command to add the PoCo "system" user if it doesn't already exist."""

    def handle(self, *args, **options):
        """
        A Django management command to add the BlueVine "system" user if it doesn't already exist.
        """
        if User.objects.filter(pk=1).first():
            self.stdout.write("The system user already exists, so there's nothing to do.")
        else:
            if User.objects.count() < 1:
                cursor = connection.cursor()
                cursor.execute("select nextval('core_user_id_seq');")
            User.objects.create(id=1, email="system@poco.com")
            self.stdout.write("The system user was successfully created.")
