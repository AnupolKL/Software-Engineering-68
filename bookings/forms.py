from django import forms
from django.contrib.auth import get_user_model
from .models import Booking
from services.models import Service

User = get_user_model()

class WalkinBookingForm(forms.ModelForm):
    start_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "border rounded w-full p-2"})
    )

    class Meta:
        model = Booking
        fields = ("barber", "service", "start_at", "notes")  # source/status ใน view
        widgets = {
            "barber": forms.Select(attrs={"class":"border rounded w-full p-2"}),
            "service": forms.Select(attrs={"class":"border rounded w-full p-2"}),
            "notes": forms.TextInput(attrs={"class":"border rounded w-full p-2"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ให้เลือกเฉพาะ user ที่เป็นช่าง
        self.fields["barber"].queryset = User.objects.filter(is_barber=True, is_active=True).order_by("username")
        self.fields["service"].queryset = Service.objects.filter(is_active=True).order_by("name")
