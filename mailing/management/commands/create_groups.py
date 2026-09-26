from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Recipient, Message, Mailing, Attempt


class Command(BaseCommand):
    help = 'Создаёт группу "Менеджер" с нужными правами'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Менеджер')

        if created:
            self.stdout.write(self.style.SUCCESS('✅ Группа "Менеджер" создана'))
        else:
            self.stdout.write('ℹ️ Группа "Менеджер" уже существует')

        models = [Recipient, Message, Mailing, Attempt]
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            permissions = Permission.objects.filter(
                content_type=content_type,
                codename__startswith='view_'
            )
            group.permissions.add(*permissions)

        self.stdout.write(self.style.SUCCESS('✅ Права на просмотр назначены'))