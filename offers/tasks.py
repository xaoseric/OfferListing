from celery import task
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from offers.models import Comment, Offer


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

@task()
def send_comment_mail(comment_pk):
    if not Comment.objects.filter(pk=comment_pk).exists():
        return

    comment = Comment.objects.get(pk=comment_pk)
    context = {"comment": comment}

    if settings.SITE_URL.endswith('/'):
        site_url = 'http://' + settings.SITE_URL[:-1]
    else:
        site_url = 'http://' + settings.SITE_URL

    context.update({"site_url": site_url})

    message = render_to_string('offers/email/comment_reply.html', context)
    message_plain = render_to_string('offers/email/comment_reply_plain.txt', context)

    send_mail(
        subject='New reply to your comment',
        message=message,
        message_plain=message_plain,
        to=comment.reply_to.commenter.email
    )

@task()
def send_new_comment_followers_mail(comment_pk):
    if not Comment.objects.filter(pk=comment_pk).exists():
        return

    comment = Comment.objects.get(pk=comment_pk)
    context = {"comment": comment}

    if settings.SITE_URL.endswith('/'):
        site_url = 'http://' + settings.SITE_URL[:-1]
    else:
        site_url = 'http://' + settings.SITE_URL

    context.update({"site_url": site_url})

    for countdown, user in enumerate(comment.offer.followers.all()):
        new_context = context
        new_context.update({"email_user": user})

        message = render_to_string('offers/email/comment_new.html', new_context)
        message_plain = render_to_string('offers/email/comment_new_plain.txt', new_context)

        send_mail.s(
            subject='New reply to your comment',
            message=message,
            message_plain=message_plain,
            to=comment.commenter.email
        ).apply_async(countdown=countdown)


@task()
def publish_latest_offer():
    offers = Offer.objects.filter(status=Offer.UNPUBLISHED, is_request=True, is_ready=True).order_by('created_at')
    if not offers.exists():
        return

    offer = offers[0]
    offer.is_request = False
    offer.status = Offer.PUBLISHED

    offer.save()
