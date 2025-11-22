from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from django.utils import timezone

from bookings.models import Booking
from .models import Review
from accounts.models import User
from .forms import ReviewForm, ReviewCreateForm
from services.models import Service


@login_required
def create_review_from_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, customer=request.user)

    # ต้องเป็นคิวที่เสร็จสิ้นเท่านั้น
    if hasattr(booking, "status"):
        if booking.status != "completed":
            messages.error(request, "สามารถรีวิวได้หลังจากใช้บริการเสร็จสิ้นเท่านั้น")
            return redirect("my_bookings")

    # ถ้ามี review อยู่แล้ว
    if hasattr(booking, "review") and booking.review is not None:
        messages.error(request, "คุณได้รีวิวการจองนี้แล้ว")
        return redirect("my_bookings")

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.service = booking.service
            review.booking = booking
            review.save()
            messages.success(request, "ขอบคุณสำหรับการรีวิว!")
            return redirect("my_bookings")
    else:
        form = ReviewForm()

    return render(request, "reviews/review_form.html", {
        "form": form,
        "booking": booking,
    })

def reviews_page(request):
    # filter ตามบริการถ้ามี query ?service=ID
    service_id = request.GET.get("service")
    reviews = Review.objects.filter(is_public=True).select_related("customer", "service")

    if service_id:
        reviews = reviews.filter(service_id=service_id)

    reviews = reviews.order_by("-created_at")

    top_barbers = (
    User.objects
    .filter(is_barber=True, is_active=True)
    .annotate(
        avg_rating=Avg("barber_bookings__review__rating"),
        review_count=Count("barber_bookings__review", distinct=True),
    )
    .filter(review_count__gt=0)   # ต้องมีรีวิวอย่างน้อย 1
    .order_by("-avg_rating", "-review_count")[:5]
    )

    # ฟอร์มเขียนรีวิว (เฉพาะคนล็อกอิน)
    form = None
    if request.user.is_authenticated:
        if request.method == "POST":
            form = ReviewCreateForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.customer = request.user
                review.save()
                messages.success(request, "ขอบคุณสำหรับการรีวิว!")
                # redirect กลับหน้ารวม (จะได้ไม่ส่งฟอร์มซ้ำเวลา refresh)
                return redirect("reviews_page")
        else:
            form = ReviewCreateForm()

    services = Service.objects.filter(is_active=True).order_by("name")

    return render(request, "reviews/reviews_page.html", {
        "reviews": reviews,
        "form": form,
        "services": services,
        "selected_service_id": int(service_id) if service_id else None,
        "top_barbers": top_barbers,
    })
