from datetime import datetime, timedelta, time as dtime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse

from services.models import Service
from .models import Booking
from .forms_public import OnlineBookingSearchForm, OnlineBookingConfirmForm, BookingEditConfirmForm

User = get_user_model()

@login_required
def booking_step1(request):
    services = Service.objects.filter(is_active=True)
    return render(request, "bookings/step1_service.html", {"services": services})

@login_required
def booking_step2(request, service_id):
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    barbers = User.objects.filter(is_barber=True, is_active=True)
    return render(request, "bookings/step2_barber.html", {
        "service": service,
        "barbers": barbers,
    })


# ตั้งค่าชั่วโมงทำการต่อวัน
OPEN_TIME  = dtime(hour=10, minute=0)  # เปิด 10:00
CLOSE_TIME = dtime(hour=18, minute=0)  # ปิด 18:00
BUFFER_MIN = 20                         # เผื่อ buffer ต่อคิว

def _overlap(a_start, a_end, b_start, b_end) -> bool:
    # ซ้อนช่วงเวลา ถ้า start < b_end และ end > b_start
    return a_start < b_end and a_end > b_start

def _generate_slots(service, day_dt, barber):
    """
    คืนรายการ slot (datetime เริ่ม) ที่ "ว่าง" สำหรับวันนั้นของช่างที่เลือก
    ใช้ความยาวคิวจาก service.duration_min และชั่วโมงทำการ
    """
    tz = timezone.get_current_timezone()
    start_day = timezone.make_aware(datetime.combine(day_dt, OPEN_TIME), tz)
    end_day   = timezone.make_aware(datetime.combine(day_dt, CLOSE_TIME), tz)

    step = timedelta(minutes=service.duration_min + BUFFER_MIN)

    # ดึงคิวของช่างในวันนั้น
    qs = Booking.objects.filter(
        barber=barber,
        start_at__lt=end_day,
        end_at__gt=start_day,
    )
    # ถ้ามีฟิลด์ status และต้องการกรองเฉพาะที่ยังใช้งาน:
    if hasattr(Booking, "status"):
        qs = qs.filter(status__in=["confirmed", "completed"])

    busy = [(b.start_at, b.end_at) for b in qs]

    slots = []
    cursor = start_day
    dur = timedelta(minutes=service.duration_min)

    while cursor + dur <= end_day:
        conflict = any(_overlap(cursor, cursor + dur, b0, b1) for (b0, b1) in busy)
        if not conflict and cursor >= timezone.now():
            slots.append(cursor)
        cursor += step

    return slots

def _generate_slots_for_edit(service, day_dt, barber, booking_to_ignore: Booking):
    """
    สร้าง slot ว่าง สำหรับแก้ไขคิว:
    - กันชนกับคิวอื่นของช่างคนเดียวกัน
    - ไม่ถือว่าคิวเดิมของตัวมันเองเป็นชน
    """
    tz = timezone.get_current_timezone()
    start_day = timezone.make_aware(datetime.combine(day_dt, OPEN_TIME), tz)
    end_day = timezone.make_aware(datetime.combine(day_dt, CLOSE_TIME), tz)

    dur = timedelta(minutes=service.duration_min)
    step = dur

    # เอาคิวของช่างในวันนั้น (ยกเว้น booking ตัวที่กำลังแก้)
    qs = Booking.objects.filter(
        barber=barber,
        start_at__lt=end_day,
        end_at__gt=start_day,
    ).exclude(pk=booking_to_ignore.pk)

    if hasattr(Booking, "status"):
        qs = qs.exclude(status__in=["canceled"])

    busy = [(b.start_at, b.end_at) for b in qs]

    slots = []
    cursor = start_day
    now = timezone.now()

    while cursor + dur <= end_day:
        conflict = any(_overlap(cursor, cursor + dur, b0, b1) for (b0, b1) in busy)
        if not conflict and cursor >= now:
            slots.append(cursor)
        cursor += step

    return slots

@login_required
def booking_step3(request, service_id, barber_id):
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    barber  = get_object_or_404(User, pk=barber_id, is_barber=True, is_active=True)

    slots = None
    date  = None

    if request.method == "POST":
        date_str = request.POST.get("date")
        if date_str:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            slots = _generate_slots(service, date, barber)

    return render(request, "bookings/step3_datetime.html", {
        "service": service,
        "barber": barber,
        "date": date,
        "slots": slots,
    })

@login_required
def booking_confirm(request, service_id, barber_id):
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    barber  = get_object_or_404(User, pk=barber_id, is_barber=True, is_active=True)

    if request.method == "POST":
        start_at = request.POST.get("start_at")
        if start_at:
            start_at = datetime.fromisoformat(start_at)
            booking = Booking.objects.create(
                customer=request.user,
                service=service,
                barber=barber,
                start_at=start_at,
                source="online"
            )
            messages.success(request, "จองคิวเรียบร้อย!")
            return redirect("booking_online_success")

    return redirect("booking_step3", service.id, barber.id)

@login_required
def booking_online_success(request):
    return render(request, "bookings/online_success.html")

@login_required
def my_bookings(request):
    qs = (Booking.objects
          .select_related("service", "barber")
          .filter(customer=request.user)
          .order_by("-created_at", "-start_at"))

    today = timezone.localdate()  # วันที่ปัจจุบัน (ตาม TZ ของ Django)

    for b in qs:
        # ถ้ามี status เสร็จสิ้น/ยกเลิกแล้ว ห้ามแก้
        if hasattr(b, "status") and b.status in ["completed", "canceled"]:
            b.can_modify = False
            continue

        # วันที่ของคิว (แปลง start_at -> localtime -> date)
        start_date = timezone.localtime(b.start_at).date()

        # แก้ไข/ยกเลิกได้เฉพาะ "ก่อนวันคิว"
        b.can_modify = start_date > today

    return render(request, "bookings/my_bookings.html", {
        "bookings": qs,
        "today": today,
    })

@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)

    # ห้ามแก้ถ้าสถานะไม่เหมาะสม
    if hasattr(Booking, "status") and booking.status in ["completed", "canceled"]:
        messages.error(request, "ไม่สามารถแก้ไขคิวนี้ได้")
        return redirect("my_bookings")

    # ห้ามแก้ในวันคิว หรือหลังวันคิว
    today = timezone.localdate()
    start_date = timezone.localtime(booking.start_at).date()
    if start_date <= today:
        messages.error(request, "ไม่สามารถแก้ไขการจองในวันคิวหรือหลังวันคิวได้")
        return redirect("my_bookings")

    # ถ้าเป็นการยืนยันเลือก slot
    if request.method == "POST" and "start_at" in request.POST:
        confirm_form = BookingEditConfirmForm(request.POST)
        if confirm_form.is_valid():
            service = get_object_or_404(Service, pk=confirm_form.cleaned_data["service_id"], is_active=True)
            barber = get_object_or_404(User, pk=confirm_form.cleaned_data["barber_id"], is_barber=True, is_active=True)
            date = confirm_form.cleaned_data["date"]
            start_at = confirm_form.cleaned_data["start_at"]

            # กันเปลี่ยนใกล้เวลาเกินไปอีกครั้ง เผื่อเวลาผ่านไประหว่างเลือก
            new_start_date = timezone.localtime(start_at).date()
            if new_start_date <= today:
                messages.error(request, "เวลาใหม่ต้องเป็นวันถัดไปจากวันนี้เท่านั้น")
                return redirect("my_bookings")

            # อัปเดต booking เดิม
            booking.service = service
            booking.barber = barber
            booking.start_at = start_at
            # ให้ save() ของ Booking ไปคำนวณ end_at และเช็คชนคิวเอง
            try:
                booking.save()
            except Exception as e:
                messages.error(request, f"ไม่สามารถเปลี่ยนแปลงได้: {e}")
                return redirect("booking_edit", pk=booking.pk)

            messages.success(request, "แก้ไขการจองเรียบร้อยแล้ว")
            return redirect("my_bookings")
        else:
            messages.error(request, "ข้อมูลไม่ถูกต้อง กรุณาลองใหม่")
            return redirect("booking_edit", pk=booking.pk)

    # เลือกบริการ/ช่าง/วัน แล้วแสดง slot
    initial = {
        "service": booking.service,
        "barber": booking.barber,
        "date": booking.start_at.date(),
    }
    form = OnlineBookingSearchForm(request.POST or None, initial=initial)

    context = {
        "booking": booking,
        "form": form,
        "slots": None,
        "service": booking.service,
        "barber": booking.barber,
        "date": booking.start_at.date(),
    }

    if request.method == "POST" and "start_at" not in request.POST and form.is_valid():
        service = form.cleaned_data["service"]
        barber = form.cleaned_data["barber"]
        date = form.cleaned_data["date"]

        slots = _generate_slots_for_edit(service, date, barber, booking)
        context["slots"] = slots
        context["service"] = service
        context["barber"] = barber
        context["date"] = date

        # เตรียมฟอร์มยืนยันให้แต่ละ slot ใช้
        context["confirm_form"] = BookingEditConfirmForm(initial={
            "booking_id": booking.pk,
            "service_id": service.pk,
            "barber_id": barber.pk,
            "date": date,
        })

    return render(request, "bookings/booking_edit.html", context)

@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)

    # ห้ามถ้าสถานะไม่เหมาะสม
    if booking.status in ["completed", "canceled"]:
        messages.error(request, "ไม่สามารถยกเลิกคิวนี้ได้")
        return redirect("my_bookings")

    today = timezone.localdate()
    start_date = timezone.localtime(booking.start_at).date()

    # ห้ามยกเลิกถ้าเป็นวันคิว หรือหลังวันคิว
    if start_date <= today:
        messages.error(request, "ไม่สามารถยกเลิกการจองในวันคิวหรือหลังวันคิวได้")
        return redirect("my_bookings")

    booking.status = "canceled"
    booking.save()

    messages.success(request, "ยกเลิกการจองเรียบร้อยแล้ว")
    return redirect("my_bookings")
