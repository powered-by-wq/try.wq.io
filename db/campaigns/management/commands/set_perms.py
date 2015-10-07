from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from vera.models import ReportStatus


class Command(BaseCommand):
    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(
            name=settings.DEFAULT_AUTH_GROUP
        )
        group.permissions = Permission.objects.filter(codename__in=[
            'add_campaign', 'change_campaign', 'add_report',
        ])

        ReportStatus(
            pk=1,
            slug='valid',
            name='Valid',
            is_valid=True
        ).save()

