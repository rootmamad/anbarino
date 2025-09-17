import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=0)
    purchased_quantity = models.PositiveIntegerField(default=0)
    returned_quantity = models.PositiveIntegerField(default=0)
    damaged_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def generate_qr_code(self):
        qr_data = f"Product: {self.name}"
        qr = qrcode.make(qr_data)

        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        filename = f'{self.name}_qr.png'

        self.qr_code.save(filename, File(buffer), save=False)
    def update_status(self):
        self.quantity = self.purchased_quantity + self.returned_quantity - self.purchased_quantity
        self.save()
    def __str__(self):
        return self.name