from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="อีเมล")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "border rounded w-full p-2"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # เพิ่มคลาสให้ฟิลด์รหัสผ่าน
        self.fields["email"].widget.attrs.update({"class": "border rounded w-full p-2"})
        self.fields["password1"].widget.attrs.update({"class": "border rounded w-full p-2"})
        self.fields["password2"].widget.attrs.update({"class": "border rounded w-full p-2"})

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("อีเมลนี้ถูกใช้แล้ว")
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="ชื่อผู้ใช้",
        widget=forms.TextInput(attrs={"class": "border rounded w-full p-2"})
    )
    password = forms.CharField(
        label="รหัสผ่าน",
        widget=forms.PasswordInput(attrs={"class": "border rounded w-full p-2"})
    )

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "nickname",
            "phone",
            "email",
            "photo",
            "password1",
            "password2",
        )
        labels = {
            "username": "ชื่อผู้ใช้",
            "nickname": "ชื่อเล่น",
            "phone": "เบอร์โทร",
            "email": "อีเมล",
            "photo": "รูปโปรไฟล์",
        }

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["nickname", "phone", "email", "photo"]

class CustomPasswordChangeForm(PasswordChangeForm):
    """ทำให้ใช้ Tailwind + รวมในหน้าเดียวได้"""
    old_password = forms.CharField(
        label="รหัสผ่านปัจจุบัน",
        widget=forms.PasswordInput(attrs={"class": "form-input"})
    )
    new_password1 = forms.CharField(
        label="รหัสผ่านใหม่",
        widget=forms.PasswordInput(attrs={"class": "form-input"})
    )
    new_password2 = forms.CharField(
        label="ยืนยันรหัสผ่านใหม่",
        widget=forms.PasswordInput(attrs={"class": "form-input"})
    )