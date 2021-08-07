from django.db import models
from django.contrib.auth.models import AbstractBaseUser,AbstractUser
from django.db.models.fields import DateTimeField
# Create your models here.


class User(AbstractUser):
    id_number = models.CharField(max_length=10, primary_key=True)
    is_operador = models.BooleanField('Es un operador',default=False)
    is_motorizado = models.BooleanField('Es un motorizado',default=False)
    #profile_pic = models.ImageField()
    birth_date = models.DateField()
    gender = models.CharField(max_length=4)


class Motorizado(User):
    pass    


