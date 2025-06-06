from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.exceptions import ValidationError

# Create your models here.

class UserBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0)

    def deduct_balance(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False






class Transaction(models.Model):
    PURCHASE = 'purchase'
    RETURNED = 'returned'
    DAMAGED = 'damaged'

    TRANSACTION_TYPES = [
        (PURCHASE, 'Purchase'),
        (RETURNED, 'Returned'),
        (DAMAGED, 'Damaged'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



    def clean(self):

        user_balance = UserBalance.objects.get(user=self.user)
        total_cost = self.quantity * self.product.price





        if self.transaction_type == self.PURCHASE:
            if total_cost > user_balance.balance:
                raise ValidationError(f"{self.user.username} موجودی کافی برای خرید ندارد!")

            if self.quantity > self.product.quantity:
                raise ValidationError(f"موجودی محصول {self.product.name} کافی نیست! فقط {self.product.quantity} عدد موجود است.")

        if self.transaction_type in [self.RETURNED, self.DAMAGED]:
            total_purchased = Transaction.objects.filter(
                user=self.user, product=self.product, transaction_type=self.PURCHASE
            ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0


            if total_purchased == 0 or self.quantity > total_purchased:
                raise ValidationError(f"{self.user.username} این محصول را نخریده یا تعداد وارد شده بیشتر از مقدار خریداری‌شده است!")

    def save(self, *args, **kwargs):
        self.clean()

        super().save(*args, **kwargs)


    def __str__(self):
        return  f"{self.product} {self.transaction_type} توسط {self.user}"