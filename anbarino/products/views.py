from django.shortcuts import render , redirect
from .models import Product
from transaction.models import Transaction ,UserBalance
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages

from django.db.models import Sum
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
def returned_view(request):
    cart_items = Transaction.objects.filter(
        user=request.user,
        transaction_type=Transaction.RETURNED,
        is_approved=False
    ).select_related('product')
    return render(request, 'products/returned.html', {
        'cart_items': cart_items
    })


@login_required
def damaged_view(request):
    cart_items = Transaction.objects.filter(
        user=request.user,
        transaction_type=Transaction.DAMAGED,
        is_approved=False
    ).select_related('product')
    return render(request, 'products/damaged.html', {
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
        transaction_type = Transaction.PURCHASE
        referer = request.headers.get('Referer','')
        print("123456")
        if '/cart' in referer:
            transaction_type = Transaction.PURCHASE
        elif '/returned' in referer:
            transaction_type = Transaction.RETURNED
        elif '/damaged' in referer:
            transaction_type = Transaction.DAMAGED
        transaction = Transaction.objects.filter(
            user=request.user,
            product__id=product_id,
            transaction_type=transaction_type,
            is_approved=False
        )
        transaction.delete()
        return JsonResponse({'status': 'ok'})
    except Transaction.DoesNotExist:
        print("transaction does not exist")
        return JsonResponse({'status': 'not_found'}, status=404)




@login_required
def damaged_finalize(request):
    if request.method != 'POST':
        return redirect('damaged_view')

    cart_items = Transaction.objects.filter(
        user=request.user,
        transaction_type=Transaction.DAMAGED,
        is_approved=False
    ).select_related('product')

    errors = {}

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

        # بررسی آیا خرید تأییدشده‌ای از این محصول وجود دارد
        total_purchased = Transaction.objects.filter(
            user=request.user,
            product=item.product,
            transaction_type=Transaction.PURCHASE,
            is_approved=True
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0

        if total_purchased == 0:
            errors[item.id] = f"شما محصول «{item.product.name}» را قبلاً نخریده‌اید."
        elif new_quantity > total_purchased:
            errors[item.id] = f"تعداد خرابی برای «{item.product.name}» از تعداد خریداری‌شده بیشتر است."

    # اگر خطایی بود، نمایش مجدد فرم
    if errors:
        return render(request, 'products/damaged.html', {
            'cart_items': cart_items,
            'error_map': errors,
        })

    # ثبت نهایی
    for item in cart_items:
        new_quantity = int(request.POST.get(f'quantities_{item.id}'))
        item.quantity = new_quantity
        item.is_approved = True
        item.save()

    messages.success(request, "خرابی‌ها با موفقیت ثبت شدند.")
    return redirect('damaged_view')


@login_required
def orders_view(request):
    # فقط تراکنش‌های تاییدشده
    approved_transactions = Transaction.objects.filter(
        user=request.user,
        is_approved=True
    ).select_related('product')

    # گروه‌بندی بر اساس کالا و نوع تراکنش
    order_summary = {}

    for trans in approved_transactions:
        pid = trans.product.id
        if pid not in order_summary:
            order_summary[pid] = {
                'product': trans.product,
                'purchase': 0,
                'damaged': 0,
                'returned': 0,
            }
        if trans.transaction_type == Transaction.PURCHASE:
            order_summary[pid]['purchase'] += trans.quantity
        elif trans.transaction_type == Transaction.DAMAGED:
            order_summary[pid]['damaged'] += trans.quantity
        elif trans.transaction_type == Transaction.RETURNED:
            order_summary[pid]['returned'] += trans.quantity

    # محاسبات نهایی:
    for item in order_summary.values():
        item['can_return'] = item['purchase'] - item['returned']
        item['can_damage'] = item['purchase'] - item['damaged']

    return render(request, 'products/orders.html', {
        'orders': order_summary.values()
    })



@login_required
def returned_finalize(request):
    if request.method != 'POST':
        return redirect('returned_view')  # ← مطمئن شو همچین view وجود داره

    cart_items = Transaction.objects.filter(
        user=request.user,
        transaction_type=Transaction.RETURNED,
        is_approved=False
    ).select_related('product')

    errors = {}

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

        # بررسی اینکه کاربر این محصول رو قبلاً خریده باشه (تأیید شده)
        total_purchased = Transaction.objects.filter(
            user=request.user,
            product=item.product,
            transaction_type=Transaction.PURCHASE,
            is_approved=True
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0

        if total_purchased == 0:
            errors[item.id] = f"شما محصول «{item.product.name}» را قبلاً نخریده‌اید."
        elif new_quantity > total_purchased:
            errors[item.id] = f"تعداد مرجوعی برای «{item.product.name}» از مقدار خریداری‌شده بیشتر است."

    if errors:
        return render(request, 'products/returned.html', {
            'cart_items': cart_items,
            'error_map': errors,
        })

    for item in cart_items:
        new_quantity = int(request.POST.get(f'quantities_{item.id}'))
        item.quantity = new_quantity
        item.is_approved = True  # ← تیک تایید مرجوعی
        item.save()

    messages.success(request, "کالاهای مرجوعی با موفقیت ثبت شدند.")
    return redirect('returned_view')


@require_POST
@login_required
def start_returned_request(request):
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')

    try:
        product = Product.objects.get(id=product_id)
        quantity = int(quantity)

        # بررسی تعداد معتبر
        if quantity <= 0:
            raise ValueError("Invalid quantity")

        Transaction.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            transaction_type=Transaction.RETURNED,
            is_approved=False
        )
        messages.success(request, f"{quantity} عدد از «{product.name}» برای مرجوعی ثبت شد.")
    except Exception as e:
        messages.error(request, f"خطا در ثبت مرجوعی: {str(e)}")

    return redirect('orders_view')


@require_POST
@login_required
def start_damaged_request(request):
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')

    try:
        product = Product.objects.get(id=product_id)
        quantity = int(quantity)

        if quantity <= 0:
            raise ValueError("Invalid quantity")

        Transaction.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            transaction_type=Transaction.DAMAGED,
            is_approved=False
        )
        messages.success(request, f"{quantity} عدد از «{product.name}» برای خرابی ثبت شد.")
    except Exception as e:
        messages.error(request, f"خطا در ثبت خرابی: {str(e)}")

    return redirect('orders_view')
