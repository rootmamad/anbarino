from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product


@receiver(post_save, sender=Product)
def create_qr_code(sender, instance, created, **kwargs):
    if created and not instance.qr_code:
        instance.generate_qr_code()
        instance.save()