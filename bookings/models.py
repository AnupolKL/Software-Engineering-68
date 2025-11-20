from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from services.models import Service
from datetime import timedelta

User = settings.AUTH_USER_MODEL
BUFFER_MIN = 0

# Create your models here.
class Booking(models.Model):
    SOURCE = [("online", "ออนไลน์"), ("walkin", "หน้าร้าน")]
    STATUS = [
        ("confirmed", "ยืนยันแล้ว"),
        ("completed", "เสร็จสิ้น"),
        ("canceled", "ยกเลิก"),
    ]

    # ลูกค้า (walk-in อนุญาตให้ว่างได้)
    customer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="customer_bookings")

    # ช่างที่ให้บริการ (ใช้ User ที่มี is_barber=True)
    barber = models.ForeignKey(User, on_delete=models.PROTECT, related_name="barber_bookings")

    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(editable=False)

    source = models.CharField(max_length=10, choices=SOURCE, default="online")
    status = models.CharField(max_length=10, choices=STATUS, default="confirmed")

    notes = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_at"]
        indexes = [
            models.Index(fields=["barber", "start_at"]),
        ]

    def __str__(self):
        who = self.customer.username if self.customer else "Walk-in"
        return f"{who} • {self.service.name} • {self.start_at:%Y-%m-%d %H:%M}"

    def compute_end(self):
        base = self.service.duration_min
        extra = 0
        # ใช้ values_list เพื่อลด query หนัก
        if self.pk:
            for dur, qty in self.addons.values_list("duration_min", "quantity"):
                extra += dur * qty
        total_min = base + extra + BUFFER_MIN
        return self.start_at + timedelta(minutes=total_min)

    def clean(self):
        if not self.start_at:
            raise ValidationError("กรุณาเลือกวันและเวลาเริ่มต้น")
        # end_at (ชั่วคราว) เพื่อเช็คชน
        end = self.compute_end()

        # กันคิวซ้อนของช่าง (ยกเว้นสถานะยกเลิก)
        conflict_qs = Booking.objects.filter(
            barber=self.barber,
            status__in=["confirmed", "completed"],
        ).exclude(pk=self.pk)

        # ซ้อนช่วงเวลา (start < end && end > start)
        conflict_qs = conflict_qs.filter(start_at__lt=end, end_at__gt=self.start_at)
        if conflict_qs.exists():
            raise ValidationError("ช่วงเวลากับช่างคนนี้ถูกจองแล้ว")

        # กันเลือกเวลาย้อนหลัง (ออปชัน)
        # if self.start_at < timezone.now():
        #     raise ValidationError("ห้ามเลือกเวลาย้อนหลัง")

    def save(self, *args, **kwargs):
        self.end_at = self.compute_end()
        self.full_clean()
        return super().save(*args, **kwargs)
    
class BookingAddon(models.Model):
    booking = models.ForeignKey("Booking", on_delete=models.CASCADE, related_name="addons")
    service  = models.ForeignKey("services.Service", on_delete=models.CASCADE)

    # snapshot fields
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_min = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)

    added_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="added_addons")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} x{self.quantity}"