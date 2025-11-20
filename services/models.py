from django.db import models
from django.utils.text import slugify

# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    duration_min = models.PositiveIntegerField()      # ระยะเวลา (นาที)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True) #เอาไว้เปิด/ปิดการให้บริการ เพื่อไม่ให้กระทบกับข้อมูลการจองหรือประวัติการใช้บริการ
    image = models.ImageField(upload_to="services/", null=True, blank=True)

    def __str__(self):
        return self.name