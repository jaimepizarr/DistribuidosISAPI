from django.db import models
from django.contrib.auth.models import AbstractBaseUser,AbstractUser
from django.db.models.fields import DateTimeField
# Create your models here.


class User(AbstractUser):
    number_id = models.CharField(max_length=10)
    is_operador = models.BooleanField('Es un operador',default=False)
    is_motorizado = models.BooleanField('Es un motorizado',default=False)
    #profile_pic = models.ImageField(upload_to = "images/profiles/")
    birth_date = models.DateField(null=True)
    gender = models.CharField(max_length=4, null=True)

class Motorizado(User):
    isOnline = models.BooleanField("",default=False)



class Ubicacion(models.Model):
    latitud = models.FloatField()
    longitud = models.FloatField()
    

