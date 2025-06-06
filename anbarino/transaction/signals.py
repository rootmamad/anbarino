from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction, UserBalance
from django.db import models
from products.models import Product
from django.core.exceptions import ValidationError

@receiver(post_save, sender=Transaction)
def update_product_status(sender, instance, **kwargs):

    if instance.is_approved:
        product_status, created = Product.objects.get_or_create(name=instance.product)
        user_balance = UserBalance.objects.get(user=instance.user)

        if instance.transaction_type == Transaction.PURCHASE:
            product_status.purchased_quantity += instance.quantity
            product_status.quantity -= instance.quantity
            if not user_balance.deduct_balance(instance.quantity * instance.product.price):
                raise ValidationError("موجودی کاربر کافی نیست!")
        elif instance.transaction_type == Transaction.RETURNED:
            total_purchased = Transaction.objects.filter(
                user=instance.user, product=instance.product, transaction_type=Transaction.PURCHASE
            ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0

            if instance.quantity > total_purchased:
                raise ValueError(f"{instance.user.username} نمی‌تواند بیش از مقدار خریداری‌شده مرجوع کند!")

            product_status.returned_quantity += instance.quantity
            product_status.quantity += instance.quantity
            user_balance.balance += instance.quantity * instance.product.price
            user_balance.save()
        elif instance.transaction_type == Transaction.DAMAGED:
            total_purchased = Transaction.objects.filter(
                user=instance.user, product=instance.product, transaction_type=Transaction.PURCHASE
            ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0

            if instance.quantity > total_purchased:
                raise ValueError(f"{instance.user.username} نمی‌تواند بیش از مقدار خریداری‌شده خرابی ثبت کند!")

            product_status.damaged_quantity += instance.quantity
            #product_status.quantity -= instance.quantity

        product_status.save()

@receiver(post_delete, sender=Transaction)
def revert_product_status(sender, instance, **kwargs):


    product_status, created = Product.objects.get_or_create(name=instance.product)
    if instance.is_approved:
        if instance.transaction_type == Transaction.PURCHASE:
            product_status.purchased_quantity -= instance.quantity
            product_status.quantity += instance.quantity
        elif instance.transaction_type == Transaction.RETURNED:
            product_status.returned_quantity -= instance.quantity
            product_status.quantity -= instance.quantity
        elif instance.transaction_type == Transaction.DAMAGED:
            product_status.damaged_quantity -= instance.quantity
            #product_status.quantity += instance.quantity

        product_status.save()