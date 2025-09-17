from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction, UserBalance
from django.db import models
from products.models import Product
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.db.models import Sum


@receiver(pre_save, sender=Transaction)
def validate_transaction(sender, instance, **kwargs):
    """
    اعتبارسنجی برای تراکنش‌های خرابی و مرجوعی
    """
    product = instance.product
    user_balance, _ = UserBalance.objects.get_or_create(user=instance.user)
    # فقط وقتی که تراکنش تایید میشه چک کن
    if not instance.is_approved:
        return

    # کل تعداد خریدهای تایید شده
    total_purchased = Transaction.objects.filter(
        user=instance.user,
        product=instance.product,
        transaction_type=Transaction.PURCHASE,
        is_approved=True
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0

    # کل خرابی‌های تایید شده (به جز رکورد فعلی اگه آپدیت میشه)
    total_damaged = Transaction.objects.filter(
        user=instance.user,
        product=instance.product,
        transaction_type=Transaction.DAMAGED,
        is_approved=True
    ).exclude(pk=instance.pk).aggregate(Sum('quantity'))['quantity__sum'] or 0

    # کل مرجوعی‌های تایید شده (به جز رکورد فعلی اگه آپدیت میشه)
    total_returned = Transaction.objects.filter(
        user=instance.user,
        product=instance.product,
        transaction_type=Transaction.RETURNED,
        is_approved=True
    ).exclude(pk=instance.pk).aggregate(Sum('quantity'))['quantity__sum'] or 0

    # مجموع قابل استفاده برای مقایسه
    if instance.transaction_type == Transaction.PURCHASE:
        product.quantity -= instance.quantity
        product.save()
        price_total = instance.quantity * product.price
        if not user_balance.deduct_balance(price_total):
            raise ValidationError("موجودی کاربر کافی نیست.")

    elif instance.transaction_type == Transaction.RETURNED:
        print("man hanooz")
        product.quantity += instance.quantity
        product.save()
        price_total = instance.quantity * product.price
        user_balance.balance += price_total
        user_balance.save()






@receiver(post_save, sender=Transaction)
def update_product_quantities(sender, instance, created, **kwargs):
    product = instance.product

    total_damaged = Transaction.objects.filter(
        product=product,
        transaction_type=Transaction.DAMAGED,
        is_approved=True
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0

    total_returned = Transaction.objects.filter(
        product=product,
        transaction_type=Transaction.RETURNED,
        is_approved=True
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0

    total_purchased = Transaction.objects.filter(
        user=instance.user,
        product=instance.product,
        transaction_type=Transaction.PURCHASE,
        is_approved=True
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0


    product.damaged_quantity = total_damaged
    product.returned_quantity = total_returned
    product.purchased_quantity = total_purchased
    product.save()
    print(product, total_damaged, total_returned,"123456789")