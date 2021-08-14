from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser, BaseUserManager
from django.db.models.base import Model
from django.db.models.fields import DateTimeField
from django.utils.translation import ugettext_lazy as _


# Create your models here.

class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    reference = models.TextField()


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    USERNAME_FIELD = 'email'

    email = models.EmailField(_('email address'), unique=True)
    # ordering = ('email',)

    REQUIRED_FIELDS = []
    number_id = models.CharField(max_length=10)
    is_operador = models.BooleanField('Es un operador', default=False)
    is_motorizado = models.BooleanField('Es un motorizado', default=False)
    profile_pic = models.ImageField(
        blank=True, null=True, upload_to="images/profiles/")
    birth_date = models.DateField(null=True)
    gender = models.CharField(max_length=4, null=True)
    home_loc = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True)

    # is_registered


class Motorizado(models.Model):
    user_id = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name='motorizado')
    isOnline = models.BooleanField("", default=False)
    id_front_photo = models.ImageField(
        "Front photo of id", upload_to="images/ids/")
    id_back_photo = models.ImageField(
        "Back photo of id", upload_to="images/ids/")
    license_front_photo = models.ImageField(
        "Front license photo", upload_to="images/licenses/")
    license_back_photo = models.ImageField(
        "Back license photo", upload_to="images/licenses/")
    #admin = models.ForeignKey(User,on_delete=models.CASCADE, related_name="Admin")


class MotValidation(models.Model):
    motorizado = models.ForeignKey(
        Motorizado, on_delete=models.SET_NULL, related_name="Motorizado", null=True)
    operador = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="Operador", null=True)


class RegErrorType(models.Model):
    nombre = models.CharField("Error type", max_length=50)


class MotRegistComments(models.Model):
    comment = models.TextField("Comment about the error in register")
    validation = models.ForeignKey(MotValidation, on_delete=models.CASCADE)
    error = models.ForeignKey(RegErrorType, null=True,
                              on_delete=models.SET_NULL)


class Map(models.Model):
    map_name = models.CharField("Name of the table map.", max_length=15)


class Sector(models.Model):
    sector_name = models.CharField("Name of the sector", max_length=15)
    limits = models.TextField("Coordinates defining the limits of this sector")
    map_id = models.ForeignKey(Map, on_delete=models.CASCADE)


class Local(models.Model):
    ruc = models.CharField("Local RUC", max_length=15, primary_key=True)
    location_id = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
    name = models.CharField("Local name", max_length=20)
    email = models.EmailField("Local email", max_length=254)
    logo_img = models.ImageField(
        "Logo image", upload_to="images/Locals/logos", null=True, blank=True)
    reg_date = models.DateField(auto_now_add=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)


class LocalSector(models.Model):
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    price = models.FloatField("Price set by the Local for the Sector")


class LocalKM(models.Model):
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    km_max = models.FloatField("Maximum Kilometer of delivery")
    price_km = models.FloatField("Price per km")
    km_min = models.FloatField("Maximum Kilometer of delivery")
    price_min = models.FloatField("Min price to charge")


class ColorVehicle(models.Model):
    color = models.CharField("Color of car", max_length=15,unique=True)


class TypeVehicle(models.Model):
    type_vehicle = models.CharField("Type of vehicle", max_length=15,unique=True)


class ModelsVehicle(models.Model):
    model = models.CharField("Model of vehicle", max_length=15,unique=True)
    type_vehicle = models.ForeignKey(TypeVehicle, on_delete=models.CASCADE)


class Vehicle(models.Model):
    year = models.IntegerField("Year of bought")
    color = models.CharField("Color of car", max_length=15)
    plate_number = models.CharField("Number of the car plate", max_length=10)
    plate_photo = models.ImageField("Plate photo", upload_to="images/plates")
    right_photo = models.ImageField(
        "Right photo of the vehicle", upload_to="images/vehicles/")
    left_photo = models.ImageField(
        "Left photo of the vehicle", upload_to="images/vehicles/")
    front_photo = models.ImageField(
        "Front photo of the vehicle", upload_to="images/vehicles/")
    back_photo = models.ImageField(
        "Back photo of the vehicle", upload_to="images/vehicles/")
    front_regis_photo = models.ImageField(
        "Registration Front Photo", upload_to="images/registrations/")
    back_regis_photo = models.ImageField(
        "Registration back Photo", upload_to="images/registrations/")
    veh_model = models.ForeignKey(ModelsVehicle, on_delete=models.CASCADE)
    motorizado = models.ForeignKey(Motorizado, on_delete=models.CASCADE)
    color = models.ForeignKey(ColorVehicle, on_delete=models.CASCADE)
    type_vehicle = models.ForeignKey(TypeVehicle, on_delete=models.CASCADE)


class Client(models.Model):
    id_number = models.CharField("id number of Client", max_length=10)
    name = models.CharField("Client name", max_length=50)
    apellido = models.CharField("Client last name", max_length=50)
    email = models.EmailField("Client email", max_length=254, null=True)


class Phone(models.Model):
    pho_number = models.CharField(max_length=11)


class PhoneLocal(models.Model):
    idPhone = models.ForeignKey(Phone, on_delete=models.CASCADE)
    local = models.ForeignKey(Local, on_delete=models.CASCADE)


class PhoneClient(models.Model):
    idPhone = models.ForeignKey(Phone, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)


class Payment(models.Model):
    payment_type = models.CharField("Type of payment", max_length=50)


class Order(models.Model):
    details = models.CharField("Details of the order", max_length=100)
    price = models.FloatField("Order price")
    delivery_price = models.FloatField("Delivery price")
    start_time = models.DateTimeField(
        "Date and hour that the order is received by us", auto_now_add=True)
    mot_assigned_time = models.DateTimeField(
        "Time the order has been assigned to a motorizado", auto_now=False, auto_now_add=False)
    deliv_start_time = models.DateTimeField(
        "Time the order begins its delivery")
    arriv_estimated_time = models.DateTimeField(
        "Arrival Estimated Time", auto_now=False, auto_now_add=False)
    real_arriv_time = models.DateTimeField(
        "Real arrival time", auto_now=False, auto_now_add=False)
    motorizado = models.ForeignKey(
        Motorizado, on_delete=models.SET_NULL, null=True, related_name="OrderMotorizado")
    operador = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="OrderOperador")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    destiny_loc = models.ForeignKey(
        Location,  on_delete=models.SET_NULL, null=True)
    local = models.ForeignKey(Local, on_delete=models.SET_NULL, null=True)


class OrderComments(models.Model):
    comment = models.TextField("Comments about the delivery of the order")
    grade = models.FloatField("Delivery grading")
    idOrder = models.ForeignKey(Order, on_delete=models.CASCADE)
