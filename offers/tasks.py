from celery import task
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


@task()
def send_mail(subject, message, message_plain, to):
    msg = EmailMultiAlternatives(
        subject,
        message_plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to]
    )
    msg.attach_alternative(
        message,
        "text/html"
    )
    msg.send()
