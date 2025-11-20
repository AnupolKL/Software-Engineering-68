from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import get_user_model
from bookings.models import Booking

from .forms_admin import BarberForm

User = get_user_model()

@staff_member_required
def barber_list(request):
    q = request.GET.get("q", "")
    qs = User.objects.filter(is_barber=True).order_by("username")
    if q:
        qs = qs.filter(username__icontains=q) | qs.filter(email__icontains=q)
    return render(request, "adminx/barber_list.html", {"barbers": qs, "q": q})

@staff_member_required
def barber_create(request):
    if request.method == "POST":
        form = BarberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "เพิ่มช่างเรียบร้อย")
            return redirect("admin_barber_list")
    else:
        form = BarberForm()
    return render(request, "adminx/barber_form.html", {"form": form, "mode": "create"})

@staff_member_required
def barber_edit(request, pk):
    obj = get_object_or_404(User, pk=pk, is_barber=True)
    if request.method == "POST":
        form = BarberForm(request.POST,request.FILES, instance=obj,)
        if form.is_valid():
            form.save()
            messages.success(request, "บันทึกข้อมูลช่างแล้ว")
            return redirect("admin_barber_list")
    else:
        form = BarberForm(instance=obj)
    return render(request, "adminx/barber_form.html", {"form": form, "mode": "edit", "obj": obj})

@staff_member_required
def barber_delete(request, pk):
    obj = get_object_or_404(User, pk=pk, is_barber=True)
    bookings_count = Booking.objects.filter(barber=obj).count()

    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, "ลบช่างเรียบร้อย")
            return redirect("admin_barber_list")
        except ProtectedError:
            # ถ้าลบไม่ได้เพราะมีข้อมูลอ้างอิง ให้ปิดการใช้งานแทน
            obj.is_active = False
            obj.save()
            messages.error(
                request,
                "ลบไม่ได้เพราะมีการจองที่อ้างถึงช่างคนนี้อยู่ ระบบได้ 'ปิดการใช้งาน' ช่างแทนแล้ว"
            )
            return redirect("admin_barber_list")

    return render(request, "adminx/barber_confirm_delete.html", {
        "obj": obj,
        "bookings_count": bookings_count,
    })