from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

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