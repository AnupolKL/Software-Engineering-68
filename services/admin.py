from django.contrib import admin
from .models import Service

# Register your models here.
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "duration_min", "is_active")
    list_editable = ("price", "duration_min", "is_active")
    fields = ("name", "description", "duration_min", "price", "is_active", "image")