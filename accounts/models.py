from django.db import models

class Staff(models.Model):
    full_name = models.CharField(max_length=150)
    national_code = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.national_code})"

