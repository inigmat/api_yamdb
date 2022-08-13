import random
import string

from django.conf import settings
from django.core.mail import send_mail


def send_mail_with_code(email, confirmation_code):
    send_mail(
        subject='Confirmation code for Yamdb',
        message=f'Confirmation code: {confirmation_code}',
        from_email='from@example.com',
        recipient_list=[email],
        fail_silently=False,
    )


def generate_confirmation_code():
    return ''.join(
        random.choices(
            string.digits,
            k=settings.CONFIRMATION_CODE_LENGTH
        )
    )
