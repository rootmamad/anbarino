from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from transaction.models import UserBalance
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from .forms import EditUserForm
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Staff
from django.views.decorators.csrf import csrf_exempt
import json

refer = []
def signup_view(request):
    if request.method == 'POST':

            data = request.POST
            user = User.objects.create_user(
                username=data['username'],
               password=data['password'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
            )

            login(request,user)
            UserBalance.objects.create(user=user,balance=0)
            return redirect("/")
    else:
        refer.append( request.META.get('HTTP_REFERER'))

    return render(request, 'accounts/signup.html')



def forgot_password_view(request):
    password = None
    if request.method == 'POST':
        username = request.POST['username']
        national_id = request.POST['national_id']
        try:
            user = User.objects.get(username=username, national_id=national_id)
            password = user.password
        except User.DoesNotExist:
            messages.error(request, 'کاربری با این مشخصات یافت نشد.')
    return render(request, 'accounts/forgot_password.html', {'password': password})

@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return redirect('/')


def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        user = authenticate(request, username=username_or_email, password=password)

        if user is None:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            return redirect(refer[-1])
        else:
            messages.error(request, "نام کاربری یا رمز عبور اشتباه است.")
            return render(request, 'accounts/login.html')
    else:
        refer.append(request.META.get('HTTP_REFERER'))
        return render(request, 'accounts/login.html')



def password_reset_view(request):
    context = {
        "show_password_fields": False,
        "username": "",
        "email": "",
    }

    if request.method == "POST":
        if "password" not in request.POST:
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip()

            context["username"] = username
            context["email"] = email

            if not username or not email:
                messages.error(request, "لطفا همه فیلدها را پر کنید.")
            else:
                try:
                    user = User.objects.get(username=username, email=email)
                    context["show_password_fields"] = True
                    messages.success(request, "کاربر یافت شد. لطفا رمز جدید را وارد کنید.")
                except User.DoesNotExist:
                    messages.error(request, "نام کاربری و ایمیل مطابقت ندارند.")

        else:
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "")
            confirm_password = request.POST.get("confirm_password", "")

            context["username"] = username
            context["email"] = email
            context["show_password_fields"] = True

            if not password or not confirm_password:
                messages.error(request, "لطفا هر دو فیلد رمز را پر کنید.")
            elif len(password) < 8:
                messages.error(request, "رمز عبور باید حداقل ۸ کاراکتر باشد.")
            elif password != confirm_password:
                messages.error(request, "رمز عبور با تکرار آن مطابقت ندارد.")
            else:
                try:
                    user = User.objects.get(username=username, email=email)
                    user.password = make_password(password)
                    user.save()
                    login(request, user)
                    return redirect('/')
                except User.DoesNotExist:
                    messages.error(request, "کاربر یافت نشد.")

    return render(request, "accounts/password_reset.html", context)



@login_required
def edit_user_view(request):
    if request.method == "POST":
        form = EditUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "status": "success",
                "message": "اطلاعات شما با موفقیت بروزرسانی شد."
            })
        else:
            return JsonResponse({
                "status": "error",
                "errors": form.errors
            })
    else:
        form = EditUserForm(instance=request.user)
        return render(request, "accounts/edit_user.html", {"form": form})


def staff_list(request):
    staff_list_ = Staff.objects.all()
    return render(request, "accounts/staff_list.html", {"staff_list": staff_list_})

def add_staff(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        national_code = request.POST.get("national_code")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        role = request.POST.get("role")

        is_staff_val = True if role == "manager" or role == "cashier" else False

        staff = Staff.objects.create(
            full_name=full_name,
            national_code=national_code,
            email=email,
            phone=phone,
            is_staff=is_staff_val,
        )
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request"})

@csrf_exempt
def edit_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == "POST":
        data = json.loads(request.body)
        staff.full_name = data.get("full_name", staff.full_name)
        staff.national_code = data.get("national_code", staff.national_code)
        staff.phone = data.get("phone", staff.phone)
        staff.email = data.get("email", staff.email)
        staff.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"})

@csrf_exempt
def delete_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == "POST":
        staff.delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"})

@csrf_exempt
def change_role(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == "POST":
        action = json.loads(request.body).get("action")
        if action == "promote":
            staff.is_staff = True
        elif action == "demote":
            staff.is_staff = False
        staff.save()
        return JsonResponse({"status": "success", "new_role": staff.role})
    return JsonResponse({"status": "error"})