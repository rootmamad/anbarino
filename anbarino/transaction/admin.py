from django.contrib import admin

from .models import Transaction,UserBalance

# Register your models here.
admin.site.register(Transaction)
admin.site.register(UserBalance)