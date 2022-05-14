from django.core.management.base import BaseCommand, CommandError
from django.db import OperationalError

class Command(BaseCommand):
    requires_migrations_checks = True
    help = 'Populate Group table with Data: NGO, Staff, General'

    def handle(self, *args, **options):        
        from django.contrib.auth.models import Group
        if Group.objects.exists():
            Group.objects.all().delete()
        Group.objects.bulk_create([
            Group(name='Staff'),
            Group(name='NGO'),
            Group(name='General'),
        ])
        self.stdout.write(self.style.SUCCESS('Successfully populated groups!'))
        