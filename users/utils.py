from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


def send_verification_email(user, request):
    """Отправка письма с подтверждением email"""
    token = user.email  # Простой токен — потом заменим на uuid
    subject = 'Подтверждение регистрации'
    verification_url = request.build_absolute_uri(
        reverse('users:verify_email', kwargs={'token': token})
    )
    message = f'''
    Здравствуйте, {user.username}!

    Спасибо за регистрацию. Для подтверждения email перейдите по ссылке:
    {verification_url}

    Если вы не регистрировались — проигнорируйте это письмо.
    '''
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )