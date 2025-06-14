from django.shortcuts import render
from .models import Product

# Create your views here.
def view(request):
    products = Product.objects.all()
    ctx = {
        'best_selling_products': Product.objects.order_by('-purchased_quantity')[:10],
        'new_products': Product.objects.order_by('-created_at')[:10],
        'low_stock_products': Product.objects.filter(quantity__lt=10)[:10],
        'bulk_products': Product.objects.filter(quantity__gte=100)[:10],
    }

    return render(request, 'products/index.html', ctx)#{'products': products})
