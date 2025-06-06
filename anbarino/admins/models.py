from django.contrib.auth.models import User
from django.db import models

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # هر ادمین یک کاربر است
    can_manage_inventory = models.BooleanField(default=True)  # آیا این ادمین اجازه مدیریت انبار دارد؟
    can_view_reports = models.BooleanField(default=True)  # آیا این ادمین اجازه مشاهده‌ی گزارش‌ها را دارد؟

    def __str__(self):
        return f"{self.user.username} - Admin"