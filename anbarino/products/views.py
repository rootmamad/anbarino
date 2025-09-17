from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from PIL import Image
from .models import Product
from .forms import ProductForm,ProductForm2
from transaction.models import Transaction ,UserBalance
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from pyzbar.pyzbar import decode
from .search_indexes import ProductDocument
from django.db.models import Sum
from elasticsearch_dsl import Q
from django.contrib.auth.decorators import user_passes_test
# Create your views here.
def view(request):
    products = list(Product.objects.all())
    ctx = {
        'best_selling_products':products[:6], #[products[i] for i in [0,1,2,3,4,5,6]],
        'new_products': products[6:12],
        'low_stock_products': products[12:18],
        'bulk_products': products[18:24],
        "last_product": products[24:30],
    }
    #ProductDocument.init()
    return render(request, 'products/index.html', ctx)#{'products': products})



@login_required
def add_balance_view(request):
    balance_obj, created = UserBalance.objects.get_or_create(user=request.user)

    if request.method == "POST":
        amount = request.POST.get("amount")
        try:
            amount = int(amount)
            if amount <= 0:
                return JsonResponse({
                    "status": "error",
                    "errors": {"amount": ["مبلغ باید بیشتر از صفر باشد."]}
                })

            balance_obj.balance += amount
            balance_obj.save()

            return JsonResponse({
                "status": "success",
                "message": f"موجودی شما {amount} تومان افزایش یافت.",
                "new_balance": balance_obj.balance
            })

        except (ValueError, TypeError):
            return JsonResponse({
                "status": "error",
                "errors": {"amount": ["مبلغ نامعتبر است."]}
            })

    return render(request, "products/add_balance.html", {
        "current_balance": balance_obj.balance
    })

@user_passes_test(lambda u: u.is_superuser)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm2(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success", "message": "تغییرات ذخیره شد"})
            return redirect("get_product", pk=product.pk)
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "errors": form.errors})
    else:
        form = ProductForm(instance=product)

    return render(request, "products/edit_product.html", {"form": form})



@login_required(login_url='/login/')
def cart_view(request):
    cart_items = Transaction.objects.filter(
        user=request.user,
        transaction_type=Transaction.PURCHASE,
        is_approved=False).select_related('product')
    if request.user.is_superuser:
        cart_items = Transaction.objects.filter(
            transaction_type=Transaction.PURCHASE,
            is_approved=True, is_approved2=False).select_related('product')
    return render(request, 'products/cart.html', {
        'cart_items': cart_items
    })


@login_required(login_url='/login/')
def returned_view(request):
    cart_items = Transaction.objects.filter(
        user=request.user,
        transaction_type=Transaction.RETURNED,
        is_approved=False).select_related('product')
    if request.user.is_superuser:
        cart_items = Transaction.objects.filter(
            transaction_type=Transaction.RETURNED,
            is_approved=True, is_approved2=False).select_related('product')
    return render(request, 'products/returned.html', {
        'cart_items': cart_items
    })


@login_required(login_url='/login/')
def damaged_view(request):
    cart_items = Transaction.objects.filter(
        user=request.user,
        transaction_type=Transaction.DAMAGED,
        is_approved=False).select_related('product')
    if  request.user.is_superuser:
        cart_items = Transaction.objects.filter(
            transaction_type=Transaction.DAMAGED,
            is_approved=True, is_approved2=False).select_related('product')



    return render(request, 'products/damaged.html', {
        'cart_items': cart_items
    })
@user_passes_test(lambda u: u.is_superuser)
def delete_product(request, pk):
    if request.method == "POST":
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return JsonResponse({
            "status": "success",
            "message": "محصول با موفقیت حذف شد."
        })
    return JsonResponse({
        "status": "error",
        "message": "درخواست نامعتبر است."
    }, status=400)

@user_passes_test(lambda u: u.is_superuser)
def admin_approvals(request):
    transactions = Transaction.objects.filter(
        transaction_type__in=[Transaction.DAMAGED, Transaction.RETURNED,Transaction.PURCHASE]
    ).order_by('-created_at')

    context = {
        "transactions": transactions
    }
    return render(request, "products/admin_approvals.html", context)

def contact(request):
    return render(request, 'products/contact-us.html')

def about(request):
    return render(request, 'products/about-us.html')

def help_(request):
    return render(request, 'products/help.html')


@user_passes_test(lambda u: u.is_superuser)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "success", "message": "محصول با موفقیت ثبت شد"})
        else:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    else:
        form = ProductForm()
    return render(request, "products/add_product.html", {"form": form})


@user_passes_test(lambda u: u.is_superuser)
def damaged_action(request, item_id):
    transaction = get_object_or_404(Transaction, id=item_id)

    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "approve":
                transaction.is_approved2 = True
                print("vay")
                transaction.save()
                print("yes")
                return JsonResponse({"status": "approved", "message": f"{transaction.product.name} تایید شد ✅"})
            elif action == "reject":
                transaction.is_approved2 = False
                transaction.save()
                print("deleted")
                return JsonResponse({"status": "rejected", "message": f"{transaction.product.name} رد شد ❌"})
        except ValidationError as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "درخواست نامعتبر"})

@user_passes_test(lambda u: u.is_superuser)
def purchase_action(request, item_id):
    transaction = get_object_or_404(Transaction, id=item_id)

    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "approve":
                transaction.is_approved2 = True
                print("vay")
                transaction.save()
                print("yes")
                return JsonResponse({"status": "approved", "message": f"{transaction.product.name} تایید شد ✅"})
            elif action == "reject":
                transaction.is_approved2 = False
                transaction.save()
                print("deleted")
                return JsonResponse({"status": "rejected", "message": f"{transaction.product.name} رد شد ❌"})
        except ValidationError as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "درخواست نامعتبر"})


@user_passes_test(lambda u: u.is_superuser)
def return_action(request, item_id):
    transaction = get_object_or_404(Transaction, id=item_id)

    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "approve":
                transaction.is_approved2 = True
                transaction.save()
                return JsonResponse({"status": "approved", "message": f"{transaction.product.name} تایید شد ✅"})
            elif action == "reject":
                transaction.is_approved2 = False
                transaction.save()
                return JsonResponse({"status": "rejected", "message": f"{transaction.product.name} رد شد ❌"})
        except ValidationError as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "درخواست نامعتبر"})

@login_required(login_url='/login/')
def cart_finalize(request):
    if request.method != 'POST':
        return redirect('cart_view')

    cart_items = Transaction.objects.filter(
        user=request.user, transaction_type='purchase', is_approved=False
    ).select_related('product')

    errors = {}
    user_balance = UserBalance.objects.get(user=request.user)
    total_cost_all = 0

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

    if errors:
        return render(request, 'products/cart.html', {
            'cart_items': cart_items,
            'error_map': errors,
        })

    for item in cart_items:
        temp = item.quantity
        new_quantity = int(request.POST.get(f'quantities_{item.id}'))
        item.quantity = new_quantity
        item.is_approved = True
        try:
            item.save()
        except ValidationError as e:
            errors[item.id] = str(e.message)
            item.quantity = temp
            item.is_approved = False
            item.save()
    if errors:
        return render(request, 'products/cart.html', {
            'cart_items': cart_items,
            'error_map': errors,
        })
    return redirect('cart_view')

@require_POST
def remove_from_cart(request, product_id):
    try:
        transaction_type = Transaction.PURCHASE
        referer = request.headers.get('Referer','')
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




@login_required(login_url='/login/')
def damaged_finalize(request):
    if request.method != 'POST':
        return redirect('damaged_view')

    cart_items = Transaction.objects.filter(
        user=request.user,
        transaction_type=Transaction.DAMAGED,
        is_approved=False
    ).select_related('product')

    errors = {}

    # --- اول: ولیدیشن ---
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

    # اگه خطا هست → همونجا برگرد
    if errors:
        return render(request, 'products/damaged.html', {
            'cart_items': cart_items,
            'error_map': errors,
        })

    # --- دوم: ذخیره‌سازی فقط وقتی خطا نیست ---
    for item in cart_items:
        new_quantity = int(request.POST.get(f'quantities_{item.id}'))
        item.quantity = new_quantity
        item.is_approved = True
        item.save()

    return redirect('damaged_view')


def get_order_summary(user):
    approved_transactions = Transaction.objects.filter(
        user=user,
    ).select_related('product')

    order_summary = {}

    for trans in approved_transactions:
        pid = trans.product.id
        if pid not in order_summary:
            order_summary[pid] = {
                'product': trans.product,
                'purchase': 0,
                'damaged': 0,
                'returned': 0,
                'purchase_pending': 0,
                'damaged_pending': 0,
                'returned_pending': 0,
            }
        if trans.transaction_type == Transaction.PURCHASE and trans.is_approved:
            order_summary[pid]['purchase'] += trans.quantity
        elif trans.transaction_type == Transaction.PURCHASE and not trans.is_approved:
            order_summary[pid]['purchase_pending'] += trans.quantity
        elif trans.transaction_type == Transaction.DAMAGED and trans.is_approved:
            order_summary[pid]['damaged'] += trans.quantity
        elif trans.transaction_type == Transaction.DAMAGED and not  trans.is_approved:
            order_summary[pid]['damaged_pending'] += trans.quantity
        elif trans.transaction_type == Transaction.RETURNED and trans.is_approved:
            print(trans,trans.quantity ,trans.is_approved,"zanet")
            order_summary[pid]['returned'] += trans.quantity
        elif trans.transaction_type == Transaction.RETURNED and not trans.is_approved:
            order_summary[pid]['returned_pending'] += trans.quantity



    for item in order_summary.values():
        item['can_return'] = item['purchase'] - item['returned']
        item['can_damage'] = item['purchase'] - item['damaged']

    return order_summary.values()


@login_required(login_url='/login/')
def orders_view(request):
    orders = get_order_summary(request.user)
    print(orders)
    return render(request, 'products/orders.html', {
        'orders': orders
    })

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/list.html', {'products': products})

@login_required(login_url='/login/')
def returned_finalize(request):
    if request.method != 'POST':
        return redirect('returned_view')

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

        total_purchased = Transaction.objects.filter(
            user=request.user,
            product=item.product,
            transaction_type=Transaction.PURCHASE,
            is_approved=True
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0
        print(total_purchased,new_quantity,"usp")
        if total_purchased == 0:
            errors[item.id] = f"شما محصول «{item.product.name}» را قبلاً نخریده‌اید."
        elif new_quantity > total_purchased:
            print("salammm")
            errors[item.id] = f"تعداد مرجوعی برای «{item.product.name}» از مقدار خریداری‌شده بیشتر است."

    if errors:
        return render(request, 'products/returned.html', {
            'cart_items': cart_items,
            'error_map': errors,
        })

    for item in cart_items:
        new_quantity = int(request.POST.get(f'quantities_{item.id}'))
        item.quantity = new_quantity
        item.is_approved = True
        try:
            item.save()
        except ValidationError as e:
            # اگه ValidationError از سیگنال اومد
            errors[item.id] = str(e.message)
            # برگردوندن مقادیر قبل
            item.quantity = 0
            item.is_approved = False
            item.save()

    if errors:
        return render(request, 'products/returned.html', {
            'cart_items': cart_items,
            'error_map': errors,
        })

    return redirect('returned_view')





@require_POST
def start_returned_request(request):
    if not request.user.is_authenticated:
        return JsonResponse({'redirect': '/login/?next=' + request.path})
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')

    try:
        product = Product.objects.get(id=product_id)
        quantity = int(quantity)

        if quantity < 0:
            raise ValueError("Invalid quantity")

        approved_purchases = Transaction.objects.filter(user=request.user,product=product,transaction_type = Transaction.PURCHASE, is_approved=True).aggregate(Sum('quantity'))['quantity__sum'] or 0
        approved_returned = Transaction.objects.filter(user=request.user, product=product,transaction_type = Transaction.RETURNED, is_approved=True).aggregate(Sum('quantity'))['quantity__sum'] or 0
        print(approved_purchases, approved_returned,quantity,"zan")
        if approved_purchases - approved_returned < quantity:
            raise ValueError("تعداد مرجوعی بیش از موجودی است.")
        last = Transaction.objects.filter(user=request.user,product_id=product_id,transaction_type = Transaction.RETURNED, is_approved=False).order_by('-created_at').first()
        if last:
            last.delete()
        if quantity > 0:
            Transaction.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                transaction_type=Transaction.RETURNED,
                is_approved=False
        ).save()
    except ValidationError as e:
        return JsonResponse({'status': 'error', 'message': str(e.message)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'success'})


@require_POST
@login_required(login_url='/login/')
def start_damaged_request(request):
    if not request.user.is_authenticated:
        return JsonResponse({'redirect': '/login/?next=' + request.path})
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')
    print(2)
    try:
        product = Product.objects.get(id=product_id)
        quantity = int(quantity)
        approved_purchases = Transaction.objects.filter(user=request.user,transaction_type = Transaction.PURCHASE, product=product, is_approved=True).aggregate(Sum('quantity'))[ 'quantity__sum'] or 0
        approved_damaged = Transaction.objects.filter(user=request.user, product=product,transaction_type = Transaction.DAMAGED, is_approved=True).aggregate(Sum('quantity'))[ 'quantity__sum'] or 0
        print(3)
        print(approved_purchases, approved_damaged, quantity,5)
        if approved_purchases - approved_damaged < quantity:
            print(approved_purchases,approved_damaged,quantity,"444454545")
            raise ValueError("تعداد خرابی بیش از موجودی است.")
        print(4)
        if quantity < 0:
            raise ValueError("Invalid quantity")
        last = Transaction.objects.filter(user=request.user,product_id=product_id,transaction_type = Transaction.DAMAGED, is_approved=False).order_by('-created_at').first()
        if last:
            last.delete()
        if quantity > 0:
            Transaction.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                transaction_type=Transaction.DAMAGED,
                is_approved=False
        ).save()
        print("finish")
    except ValidationError as e:
        return JsonResponse({'status': 'error', 'message': str(e.message)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'success'})

def get_product(request,pk):
    product = get_object_or_404(Product, id=pk)
    print(product.returned_quantity,"oi")
    if request.user.is_authenticated:
        orders = get_order_summary(request.user)
        order = ""
        for item in orders:
            if item["product"]==product:
                order = item
        print(order,orders,product)
        return render(request, 'products/product_detail.html', {"product":product, "order":order})
    else:
        return render(request, 'products/product_detail.html', {"product":product})


"@login_required(login_url='/login/')"
@require_POST
def start_purchase(request):
    if not request.user.is_authenticated:
        return JsonResponse({'redirect': '/login/?next=' + request.path})
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')
    print(product_id,quantity,"ooo")
    try:
        product = Product.objects.get(id=product_id)
        quantity = int(quantity)




        balance = UserBalance.objects.get(user=request.user).balance
        print(balance,quantity,product.price,"yt")
        if balance < quantity * product.price:
            print("kp")
            raise ValidationError("موجودی کافی ندارید.")

        last = Transaction.objects.filter(user=request.user, product_id=product_id,
                                          transaction_type=Transaction.PURCHASE, is_approved=False).order_by('-created_at').first()
        if last:
            last.delete()

        if quantity > 0:
            Transaction.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                transaction_type=Transaction.PURCHASE,
                is_approved=False
        ).save()
    except ValidationError as e:
        error_message = e.message if hasattr(e, 'message') else str(e)
        print("Validation error:", error_message)
        return JsonResponse({'status': 'error', 'message': error_message}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    print(request.POST)
    return JsonResponse({'status': 'success'})





def inventory_check(request):
    product = None
    searched = False

    if request.method == 'POST':
        searched = True
        name = request.POST.get('name')
        barcode_file = request.FILES.get('barcode')

        if name:
            product = Product.objects.filter(name__icontains=name)
        elif barcode_file:
            img = Image.open(barcode_file)
            decoded_objects = decode(img)
            txt =  decoded_objects[0].data.decode("utf-8")
            product = Product.objects.filter(name__icontains=txt.strip("Product: "))

    return render(request, 'products/check.html', {
        'product': product,
        'searched': searched
    })

from .models import Product

def search_results(request):
    query = request.GET.get("q", "")
    results = []

    if query:
        q = Q("match", name=query)
        s = ProductDocument.search().query(q)
        response = s.execute()

        product_ids = [r.meta.id for r in response]
        results = Product.objects.filter(id__in=product_ids)

    return render(request, "products/search.html", {
        "query": query,
        "results": results,
    })


def user_stock(request):
    if request.user.is_authenticated:
        try:
            stock = UserBalance.objects.get(user=request.user).balance
        except Exception as e :
            print(e)
        return {'user_stock': stock}
    return {}

def index_all(request):
    print("salam")
    for product in Product.objects.all():

        ProductDocument(meta={'id': product.id}, name=product.name).save()

    return JsonResponse({'status': 'all products indexed'})




def search_products(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'Query is required'}, status=400)

    q = Q("match", name=query)

    s = ProductDocument.search().query(q)
    response = s.execute()
    print(response,"456")
    results = []
    # فچ از دیتابیس واقعی بر اساس ID
    for r in response:
        try:
            product = Product.objects.get(id=r.meta.id)
            results.append({
                "id": product.id,
                "name": product.name,
                "image": product.image.url if product.image else None,
                "price": product.price,
                "quantity": product.quantity,
            })
        except Product.DoesNotExist:
            continue

    return JsonResponse({"results": results})

