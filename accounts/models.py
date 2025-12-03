from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    is_barber = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="barbers/", null=True, blank=True)
    nickname = models.CharField("ชื่อเล่น", max_length=50, blank=True)
    phone = models.CharField("เบอร์โทร", max_length=20, blank=True)
    photo = models.ImageField("รูปโปรไฟล์",upload_to="profiles/",blank=True,null=True,)

    def __str__(self):
        return self.get_full_name() or self.username
