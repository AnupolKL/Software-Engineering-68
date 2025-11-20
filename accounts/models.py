from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    is_barber = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="barbers/", null=True, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username
