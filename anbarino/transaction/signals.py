from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction, UserBalance
from django.db import models
from products.models import Product
from django.core.exceptions import ValidationError

@receiver(post_save, sender=Transaction)
def update_product_status(sender, instance, **kwargs):
    if not instance.is_approved:
        return

    product = instance.product
    user_balance = UserBalance.objects.get(user=instance.user)

    total_purchased = Transaction.objects.filter(
        user=instance.user, product=product, transaction_type=Transaction.PURCHASE, is_approved=True
    ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0

    total_returned = Transaction.objects.filter(
        user=instance.user, product=product, transaction_type=Transaction.RETURNED, is_approved=True
    ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0

    total_damaged = Transaction.objects.filter(
        user=instance.user, product=product, transaction_type=Transaction.DAMAGED, is_approved=True
    ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0

    if instance.transaction_type == Transaction.RETURNED:
        if total_returned + instance.quantity > total_purchased - total_damaged:
            raise ValidationError("نمیتوان بیشتر از مقدار قابل برگشت مرجوع کرد.")
        product.returned_quantity += instance.quantity
        product.quantity += instance.quantity
        user_balance.balance += instance.quantity * product.price
        user_balance.save()

    elif instance.transaction_type == Transaction.DAMAGED:
        if total_damaged + instance.quantity > total_purchased - total_returned:
            raise ValidationError("نمیتوان بیشتر از مقدار قابل خرابی ثبت کرد.")
        product.damaged_quantity += instance.quantity

    elif instance.transaction_type == Transaction.PURCHASE:
        if not user_balance.deduct_balance(instance.quantity * product.price):
            raise ValidationError("موجودی کاربر کافی نیست!")
        product.purchased_quantity += instance.quantity
        product.quantity -= instance.quantity

    product.save()


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