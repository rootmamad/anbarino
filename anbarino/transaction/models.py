from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.exceptions import ValidationError

# Create your models here.








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
    created_at = models.DateTimeField(auto_now_add=True)



    def clean(self):
        #  بررسی تعداد خرید و موجودی محصول
        if self.transaction_type == self.PURCHASE:
            if self.quantity > self.product.quantity:
                raise ValidationError(f"موجودی محصول {self.product.name} کافی نیست! فقط {self.product.quantity} عدد موجود است.")

        # بررسی اینکه اگر تراکنش مرجوعی یا خرابی بود، کاربر باید قبلاً این محصول را خریده باشد و تعداد بیش از خریداری‌شده نباشد
        if self.transaction_type in [self.RETURNED, self.DAMAGED]:
            total_purchased = Transaction.objects.filter(
                user=self.user, product=self.product, transaction_type=self.PURCHASE
            ).aggregate(models.Sum('quantity'))['quantity__sum'] or 0


            if total_purchased == 0 or self.quantity > total_purchased:
                raise ValidationError(f"{self.user.username} این محصول را نخریده یا تعداد وارد شده بیشتر از مقدار خریداری‌شده است!")

    def save(self, *args, **kwargs):
        self.clean()  # اعتبارسنجی قبل از ذخیره‌سازی
        super().save(*args, **kwargs)


    def __str__(self):
        return  f"{self.product} {self.transaction_type} توسط {self.user}"