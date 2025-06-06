from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=0)
    purchased_quantity = models.PositiveIntegerField(default=0)
    returned_quantity = models.PositiveIntegerField(default=0)
    damaged_quantity = models.PositiveIntegerField(default=0)

    def update_status(self):
        self.quantity = self.purchased_quantity - (self.returned_quantity + self.damaged_quantity)
        self.save()
    def __str__(self):
        return self.name