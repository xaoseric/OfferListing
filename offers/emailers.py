from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_simple_mail(subject, message, to):

    msg = EmailMultiAlternatives(subject, message, from_email=settings.DEFAULT_FROM_EMAIL, to=[to])
    msg.attach_alternative(message, "text/html")
    msg.send()


def send_comment_reply(comment):
    if not comment.is_reply():
        return

    message = render_to_string('offers/email/comment_reply.html', {"comment": comment})
    send_simple_mail('New reply to your comment', message, comment.reply_to.commenter.email)
