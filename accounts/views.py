from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required

# Create your views here.
def register_view(request):
    # กันผู้ใช้ที่ล็อกอินอยู่ไม่ให้มาสมัครซ้ำ
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"].lower()
            user.save()
            login(request, user)   # สมัครเสร็จ ล็อกอินให้เลย
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


class LoginPage(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class LogoutPage(LogoutView):
    next_page = reverse_lazy("home")