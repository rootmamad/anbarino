from django.shortcuts import render , redirect
from .models import Product
from transaction.models import Transaction ,UserBalance
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods

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


@login_required
def cart_view(request):
    cart_items = Transaction.objects.filter(
        user=request.user,
        transaction_type=Transaction.PURCHASE,
        is_approved=False
    ).select_related('product')

    return render(request, 'products/cart.html', {
        'cart_items': cart_items
    })

@login_required
def cart_finalize(request):
    if request.method != 'POST':
        return redirect('cart_view')

    cart_items = Transaction.objects.filter(
        user=request.user, transaction_type='purchase', is_approved=False
    ).select_related('product')

    errors = {}
    user_balance = UserBalance.objects.get(user=request.user)
    total_cost_all = 0

    # مرحله اول: اعتبارسنجی همه آیتم‌ها
    for item in cart_items:
        quantity_str = request.POST.get(f'quantities_{item.id}')
        try:
            new_quantity = int(quantity_str)
        except (TypeError, ValueError):
            errors[item.id] = "تعداد نامعتبر وارد شده."
            continue

        if new_quantity <= 0:
            errors[item.id] = "تعداد باید بیشتر از صفر باشد."
            continue

        product = item.product
        cost = new_quantity * product.price

        if new_quantity > product.quantity:
            errors[item.id] = f"موجودی کافی برای «{product.name}» نیست (حداکثر {product.quantity} عدد موجود است)."
        elif cost > user_balance.balance:
            errors[item.id] = f"اعتبار شما برای خرید «{product.name}» کافی نیست."
        else:
            total_cost_all += cost

    # اگر خطایی وجود داشت، برگرد به صفحه با پیام
    if errors:
        return render(request, 'products/cart.html', {
            'cart_items': cart_items,
            'error_map': errors,
        })

    # مرحله دوم: اعمال خرید برای آیتم‌های معتبر
    for item in cart_items:
        new_quantity = int(request.POST.get(f'quantities_{item.id}'))
        item.quantity = new_quantity
        item.is_approved = True
        item.save()  # سیگنال مربوطه هم فعال می‌شود

    messages.success(request, "خرید با موفقیت انجام شد.")
    return redirect('cart_view')

@require_POST
def remove_from_cart(request, product_id):
    try:
        transaction = Transaction.objects.filter(
            user=request.user,
            product__id=product_id,
            transaction_type=Transaction.PURCHASE,
            is_approved=False
        )
        transaction.delete()
        return JsonResponse({'status': 'ok'})
    except Transaction.DoesNotExist:
        print("transaction does not exist")
        return JsonResponse({'status': 'not_found'}, status=404)