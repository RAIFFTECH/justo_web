from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from usuarios_app.models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Crear automáticamente un perfil asociado al usuario
        UserProfile.objects.create(user=instance)
