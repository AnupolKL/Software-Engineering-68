from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class BarberForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class":"border rounded w-full p-2"}),
        help_text="ปล่อยว่างหากไม่ต้องการเปลี่ยนรหัสผ่าน"
    )

    class Meta:
        model = User
        fields = ("username", "email", "is_active", "password", "avatar")
        widgets = {
            "username": forms.TextInput(attrs={"class":"border rounded w-full p-2"}),
            "email": forms.EmailInput(attrs={"class":"border rounded w-full p-2"}),
            "is_active": forms.CheckboxInput(attrs={"class":"h-4 w-4"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # บังคับเป็นช่าง
        user.is_barber = True
        # ตั้งรหัสผ่านถ้ามีกรอก
        pwd = self.cleaned_data.get("password")
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user
