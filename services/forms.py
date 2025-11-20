from django import forms
from .models import Service

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ("name","description","duration_min","price","is_active","image")
        widgets = {
            "name": forms.TextInput(attrs={"class":"border rounded w-full p-2"}),
            "description": forms.Textarea(attrs={"class":"border rounded w-full p-2","rows":4}),
            "duration_min": forms.NumberInput(attrs={"class":"border rounded w-full p-2"}),
            "price": forms.NumberInput(attrs={"class":"border rounded w-full p-2","step":"0.01"}),
            "is_active": forms.CheckboxInput(attrs={"class":"h-4 w-4"}),
        }

    def clean_duration_min(self):
        v = self.cleaned_data["duration_min"]
        if v <= 0:
            raise forms.ValidationError("ระยะเวลาต้องมากกว่า 0 นาที")
        return v

    def clean_price(self):
        v = self.cleaned_data["price"]
        if v < 0:
            raise forms.ValidationError("ราคาต้องไม่ติดลบ")
        return v
