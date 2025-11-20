from django.db import models
from django.conf import settings

from services.models import Service
from bookings.models import Booking


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1–5 ดาว

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    booking = models.OneToOneField(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="review",
        help_text="รีวิวนี้ผูกกับการจองไหน (ถ้ามี)",
    )

    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.service.name} • {self.customer.username} • {self.rating} ดาว"
