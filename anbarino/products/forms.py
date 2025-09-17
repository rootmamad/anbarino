from django import forms
from .models import Product
from django.contrib.auth import get_user_model

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'image', 'price', 'quantity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام محصول'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'قیمت'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'موجودی'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ProductForm2(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "price", "quantity", "image"]