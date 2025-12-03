from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm, ProfileEditForm, CustomPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
def register_view(request):
    #กันไม่ให้ผู้ใช้ที่ล็อกอินแล้วเข้าถึงหน้าลงทะเบียน
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"].lower()
            user.save()
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})

class LoginPage(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class LogoutPage(LogoutView):
    next_page = reverse_lazy("home")

@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=user)
        password_form = CustomPasswordChangeForm(user, request.POST)

        # กดปุ่มอัปเดตโปรไฟล์
        if "update_profile" in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                return redirect("edit_profile")

        # กดปุ่มเปลี่ยนรหัสผ่าน
        elif "change_password" in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "เปลี่ยนรหัสผ่านสำเร็จ")
                return redirect("edit_profile")
            else:
                for field, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, str(error))

    else:
        profile_form = ProfileEditForm(instance=user)
        password_form = CustomPasswordChangeForm(user)

    return render(request, "accounts/edit_profile.html", {
        "profile_form": profile_form,
        "password_form": password_form,
    })