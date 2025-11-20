from django import forms
from django.contrib.auth import get_user_model
from services.models import Service

User = get_user_model()

class OnlineBookingSearchForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True).order_by("name"),
        widget=forms.Select(attrs={"class":"border rounded p-2 w-full"}),
        label="บริการ"
    )
    barber = forms.ModelChoiceField(
        queryset=User.objects.filter(is_barber=True, is_active=True).order_by("username"),
        widget=forms.Select(attrs={"class":"border rounded p-2 w-full"}),
        label="ช่าง"
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type":"date","class":"border rounded p-2 w-full"}),
        label="เลือกวัน"
    )


class OnlineBookingConfirmForm(forms.Form):
    # ฟอร์มยืนยันจะซ่อนค่าที่เลือกไว้แล้ว + เวลาที่ลูกค้าเลือก
    service_id = forms.IntegerField(widget=forms.HiddenInput)
    barber_id  = forms.IntegerField(widget=forms.HiddenInput)
    date       = forms.DateField(widget=forms.HiddenInput)
    start_at   = forms.DateTimeField(widget=forms.HiddenInput)
    notes      = forms.CharField(required=False, widget=forms.TextInput(attrs={"class":"border rounded p-2 w-full"}), label="หมายเหตุ (ถ้ามี)")

    #แก้ไขข้อมูลการจองตัวเอง
class BookingEditConfirmForm(forms.Form):
    booking_id = forms.IntegerField(widget=forms.HiddenInput)
    service_id = forms.IntegerField(widget=forms.HiddenInput)
    barber_id = forms.IntegerField(widget=forms.HiddenInput)
    date = forms.DateField(widget=forms.HiddenInput)
    start_at = forms.DateTimeField(widget=forms.HiddenInput)
