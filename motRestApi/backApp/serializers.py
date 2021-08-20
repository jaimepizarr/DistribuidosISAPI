from base64 import decode
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db import models
from rest_framework import serializers
from django.db.models.query import Prefetch
from rest_framework import fields
from rest_framework.serializers import ModelSerializer
from backApp.models import ColorVehicle, Local, Location, TypeVehicle, User, Motorizado, Vehicle, ModelsVehicle


class ColorVehicleSerializer(ModelSerializer):
    class Meta:
        model = ColorVehicle
        fields = ["id","color"]

class TypeVehicleSerializer(ModelSerializer):
    class Meta:
        model = TypeVehicle
        fields = ["id","type_vehicle"]

class ModelsVehicleSerializer(ModelSerializer):
    class Meta:
        model = ModelsVehicle
        fields = ["id","model","type_vehicle"]
class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ["id","longitude","latitude","reference"]
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id",'first_name','last_name',"email","password","number_id","gender","profile_pic","is_operador","home_loc","is_staff","is_motorizado"]

    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class MotSerializer(ModelSerializer):
    user_id=UserSerializer( many=False)
    
    # select_related_fields = ('user_id',)
    @classmethod
    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        print("INICIA")
        queryset=queryset.select_related('user_id')
        # .values('user_id_id__first_name','user_id_id__last_name','user_id_id__email','user_id_id__number_id','user_id_id__is_active')
        queryset=queryset.filter(user_id__is_motorizado=False)
        return queryset

    class Meta:
        model = Motorizado
        fields = ["user_id","id_front_photo","id_back_photo","license_front_photo","license_back_photo","isOnline"]


class VehicleSerializer(ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"

class LocalRegistrationSerializer(ModelSerializer):
    #Ensuring passwords are at least 8 characters long and at most 128 characeters,
    #and can't be read by the client (Local User)
    password = serializers.CharField(
        max_length=128,
        min_length = 8,
        write_only = True
    )

    #The token should not be able to be sent with a registration request.
    #Using read_only true will handle that for us.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = Local

        fields = ["ruc","password","location_id","name","email","logo_img","admin"]

    def create(self, validated_data):
        return Local.objects.create_local(**validated_data)

class LocalLoginSerializer(ModelSerializer):
    ruc = serializers.CharField(max_length=13)
    password = serializers.CharField(max_length=255, write_only=True)
    token = serializers.CharField(max_length=255, read_only = True)

    def validate(self,data):
        ruc = data.get("ruc",None)
        password = data.get("password",None)
        
        local = Local.objects.get(ruc=ruc)
        if not local.check_password(password):
            raise serializers.ValidationError("Credentials are incorrect")
        
        return {
            "ruc":ruc,
            "token":local.token
        }

class LocalSerializer(ModelSerializer):
    class Meta:
        model = Local
        fields = ["ruc","name","email","logo_img","location_id"]

class OrderSerializer(ModelSerializer):
    local=LocalSerializer(many=False,read_only=True)
    destiny_loc=LocalSerializer(many=False,read_only=True)
    motorizado=MotSerializer(many=False,read_only=True)

    
    # select_related_fields = ('user_id',)
    @classmethod
    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        print("INICIA")
        queryset=queryset.select_related('local', 'destiny_loc','motorizado')
        return queryset
    class Meta:
        model = Local
        fields = "__all__"