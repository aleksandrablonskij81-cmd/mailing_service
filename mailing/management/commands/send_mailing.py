from django.core.management.base import BaseCommand
from mailing.models import Mailing
from mailing.services import send_mailing


class Command(BaseCommand):
    help = 'Запускает рассылку по ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        self.stdout.write(f'Запуск рассылки #{mailing_id}...')

        success, message = send_mailing(mailing_id)

        if success:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.ERROR(message))