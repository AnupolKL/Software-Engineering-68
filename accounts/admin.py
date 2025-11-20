from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # ถ้ามีฟิลด์ custom เช่น is_barber ให้ใส่เพิ่ม
    fieldsets = BaseUserAdmin.fieldsets + (
        ("CUTCAMP", {"fields": ("is_barber",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("CUTCAMP", {"fields": ("is_barber",)}),
    )
    list_display = ("id", "username", "email", "is_barber", "is_staff", "is_superuser")
    search_fields = ("username", "email")
    ordering = ("id",)