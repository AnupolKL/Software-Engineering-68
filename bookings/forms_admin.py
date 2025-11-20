from django import forms
from services.models import Service
from .models import BookingAddon

class BookingAddonForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True).order_by("name"),
        widget=forms.Select(attrs={"class":"border rounded p-2 w-full"}),
        label="เลือกบริการเสริม"
    )
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={"class":"border rounded p-2 w-full"}))

    class Meta:
        model = BookingAddon
        fields = ("service", "quantity")
