from django.contrib.auth.models import User
from django.db import models

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    can_manage_inventory = models.BooleanField(default=True)
    can_view_reports = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - Admin"