from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail

@receiver(post_save, sender=User)
def send_activation_user(sender, instance, created, **kwargs):
    if created:
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{instance.id}/{token}/"
        subject = 'Activate your account'
        message = (
            f"Hi {instance.username},\n\n"
            f"Please click the link to activate your account:\n{activation_url}\n\n"
            "If you did not sign up, ignore this email."
        )
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email], fail_silently=True)
        except Exception as e:
            print(f"Activation email failed to {instance.email}: {e}")

@receiver(post_save, sender=User)
def ensure_default_group(sender, instance, created, **kwargs):
    if created:
        grp, _ = Group.objects.get_or_create(name='participant')
        instance.groups.add(grp)
