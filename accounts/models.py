from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    username = models.CharField(
        validators=[MinLengthValidator(5)],
        max_length=20, unique=True)
    password = models.CharField(
        validators=[MinLengthValidator(6)],
        max_length=20)
