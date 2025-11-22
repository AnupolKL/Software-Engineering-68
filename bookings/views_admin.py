from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .models import Booking
from services.models import Service
from django.contrib.auth import get_user_model
from .forms import WalkinBookingForm
from .models import Booking, BookingAddon
from .forms_admin import BookingAddonForm

User = get_user_model()

AUTO_COMPLETE_GRACE_MIN = 10  #10 นาที แล้วค่อยเปลี่ยนสถานะเป็น completed

@staff_member_required
def booking_admin_list(request):
    now = timezone.now()
    cutoff = now - timedelta(minutes=AUTO_COMPLETE_GRACE_MIN)
    if hasattr(Booking, "status"):
        (Booking.objects
            .filter(status="confirmed", end_at__lte=cutoff)
            .update(status="completed"))
        
    q = request.GET.get("q", "")
    status = request.GET.get("status", "")
    bookings = Booking.objects.select_related("service", "barber", "customer").all()

    if q:
        bookings = bookings.filter(
            Q(service__name__icontains=q) |
            Q(barber__username__icontains=q) |
            Q(customer__username__icontains=q) |
            Q(notes__icontains=q)
        )
    if status:
        bookings = bookings.filter(status=status)

    bookings = bookings.order_by("-start_at")[:300]  # limit แสดง 300 รายการล่าสุด

    return render(request, "adminx/booking_list.html", {"bookings": bookings, "q": q, "status": status, "now": timezone.now(),})

@staff_member_required
def booking_admin_walkin_create(request):
    if request.method == "POST":
        form = WalkinBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.source = "walkin"
            booking.status = "confirmed"
            booking.customer = None
            booking.save()
            messages.success(request, "บันทึกคิว Walk-in เรียบร้อย")
            return redirect("admin_booking_list")
    else:
        form = WalkinBookingForm()
    return render(request, "adminx/booking_form.html", {"form": form, "mode": "walkin"})

@staff_member_required
def booking_admin_cancel(request, pk):
    bk = get_object_or_404(Booking, pk=pk)

    if hasattr(Booking, "status"):
        from datetime import timedelta
        #ห้ามยกเลิกถ้าเลย 10 นาที หรือเสร็จสิ้นแล้ว
        if bk.status in ["completed", "canceled"] or timezone.now() > bk.end_at + timedelta(minutes=AUTO_COMPLETE_GRACE_MIN):
            messages.error(request, "ไม่สามารถยกเลิกคิวนี้ได้ (เกินเวลาที่กำหนด/คิวเสร็จสิ้นแล้ว)")
            return redirect("admin_booking_list")

    bk.status = "canceled"
    bk.save()
    messages.warning(request, "ยกเลิกคิวแล้ว")
    return redirect("admin_booking_list")

@staff_member_required
def dashboard_home(request):
    now = timezone.now()
    status_cancel = False
    start_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_day = start_day + timezone.timedelta(days=1)

    stats = {
        "bookings_today": Booking.objects.filter(start_at__gte=start_day, start_at__lt=end_day).count(),
        "walkins_today": Booking.objects.filter(
            start_at__gte=start_day, start_at__lt=end_day, source="walkin"
        ).count(),
        "services_active": Service.objects.filter(is_active=True).count(),
        "barbers": User.objects.filter(is_barber=True, is_active=True).count(),
        "bookings_total": Booking.objects.all().count(),
        "bookings_canceled": Booking.objects.filter(status="canceled").count(),
        "bookings_completed": Booking.objects.filter(status="completed").count(),
    }

    latest = Booking.objects.select_related("service", "barber", "customer").order_by("-start_at")[:10]

    return render(request, "adminx/dashboard.html", {
        "stats": stats,
        "latest": latest,
    })

@staff_member_required
def booking_admin_addon(request, pk):
    booking = get_object_or_404(Booking.objects.select_related("service","barber","customer"), pk=pk)

    if hasattr(Booking, "status"):
        from datetime import timedelta
        if booking.status in ["completed", "canceled"] or timezone.now() > booking.end_at + timedelta(minutes=AUTO_COMPLETE_GRACE_MIN):
            messages.error(request, "ไม่สามารถเพิ่มบริการเสริมได้ (คิวนี้เสร็จสิ้น/เกินเวลาที่กำหนด)")
            return redirect("admin_booking_list")

    if request.method == "POST":
        form = BookingAddonForm(request.POST)
        if form.is_valid():
            svc = form.cleaned_data["service"]
            qty = form.cleaned_data["quantity"]

            # สร้างแถว addon
            addon = BookingAddon.objects.create(
                booking=booking,
                service=svc,
                name=svc.name,
                price=svc.price,
                duration_min=svc.duration_min,
                quantity=qty,
                added_by=request.user,
            )

            # เซฟ booking เพื่อคำนวณ end_at ใหม่ + (ถ้ามี total_price)
            try:
                booking.save()  # save() ของคุณเรียก compute_end() อยู่แล้ว
            except Exception as e:
                # ถ้ามีคิวชนจะ raise จาก clean() → rollback โดยลบ addon ที่เพิ่งเพิ่ม
                addon.delete()
                messages.error(request, f"เพิ่มบริการเสริมไม่สำเร็จ: {e}")
                return redirect("admin_booking_list")

            messages.success(request, "เพิ่มบริการเสริมแล้ว และอัปเดตเวลาสิ้นสุดเรียบร้อย")
            return redirect("admin_booking_detail", pk=booking.pk) if "admin_booking_detail" in request.resolver_match.namespace else redirect("admin_booking_list")
    else:
        form = BookingAddonForm()

    return render(request, "adminx/booking_addon_form.html", {
        "booking": booking,
        "form": form
    })