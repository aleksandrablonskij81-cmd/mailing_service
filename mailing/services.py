from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Mailing, Attempt


def send_mailing(mailing_id):
    """
    Сервисная функция отправки рассылки.
    Возвращает (success: bool, message: str).
    """
    try:
        mailing = Mailing.objects.get(pk=mailing_id)
    except Mailing.DoesNotExist:
        return False, 'Рассылка не найдена.'

    now = timezone.now()

    # Проверка времени
    if now < mailing.start_time:
        return False, f'Рассылка ещё не началась. Начало: {mailing.start_time:%d.%m.%Y %H:%M}'
    if now > mailing.end_time:
        return False, f'Рассылка уже завершена. Окончание: {mailing.end_time:%d.%m.%Y %H:%M}'

    recipients = mailing.recipients.all()
    if not recipients.exists():
        return False, 'У рассылки нет получателей.'

    # Собираем данные для batch-создания Attempt
    attempts_to_create = []
    success_count = 0
    failed_count = 0

    for recipient in recipients:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            attempts_to_create.append(
                Attempt(
                    mailing=mailing,
                    status=Attempt.STATUS_SUCCESS,
                    server_response='OK'
                )
            )
            success_count += 1
        except Exception as e:
            attempts_to_create.append(
                Attempt(
                    mailing=mailing,
                    status=Attempt.STATUS_FAILED,
                    server_response=str(e)
                )
            )
            failed_count += 1

    # BATCH-создание попыток
    if attempts_to_create:
        Attempt.objects.bulk_create(attempts_to_create)

    # Обновляем статус рассылки
    mailing.update_status()

    return True, f'Отправлено: {success_count}, ошибок: {failed_count}'