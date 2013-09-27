from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_simple_mail(subject, message_template, message_plain_template, context, to):

    if settings.SITE_URL.endswith('/'):
        site_url = 'http://' + settings.SITE_URL[:-1]
    else:
        site_url = 'http://' + settings.SITE_URL

    context.update({"site_url": site_url})

    message = render_to_string(message_template, context)
    message_plain = render_to_string(message_plain_template, context)

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


def send_comment_reply(comment):
    if not comment.is_reply():
        return

    send_simple_mail(
        subject='New reply to your comment',
        message_template='offers/email/comment_reply.html',
        message_plain_template='offers/email/comment_reply_plain.txt',
        context={"comment": comment},
        to=comment.reply_to.commenter.email
    )
