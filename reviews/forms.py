from django import forms
from .models import Review
from services.models import Service

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
            "comment": forms.Textarea(attrs={"class": "border rounded p-2 w-full", "rows": 3}),
        }
        labels = {
            "rating": "ให้คะแนน",
            "comment": "ความคิดเห็นเพิ่มเติม",
        }

class ReviewCreateForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True).order_by("name"),
        label="เลือกบริการ",
        widget=forms.Select(attrs={"class": "border rounded p-2 w-full"})
    )

    class Meta:
        model = Review
        fields = ["service", "rating", "comment"]
        widgets = {
            "rating": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
            "comment": forms.Textarea(attrs={"class": "border rounded p-2 w-full", "rows": 3}),
        }
        labels = {
            "rating": "ให้คะแนน",
            "comment": "ความคิดเห็นเพิ่มเติม",
        }