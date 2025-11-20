from django import forms

class HairAIForm(forms.Form):
    image = forms.ImageField(
        label="อัปโหลดรูปใบหน้าของคุณ",
        widget=forms.ClearableFileInput(attrs={"class": "border rounded p-2 w-full bg-white"})
    )
