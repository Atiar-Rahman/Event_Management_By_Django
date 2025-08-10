from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Event

@receiver(m2m_changed, sender=Event.participants.through)
def send_rsvp_email(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for user_id in pk_set:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                continue
            if user.email:
                send_mail(
                    'RSVP Confirmation',
                    f'You have RSVP’d to "{instance.name}" on {instance.date}.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True
                )
