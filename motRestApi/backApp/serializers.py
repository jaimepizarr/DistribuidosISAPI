from django.db import models
from django.db.models.query import Prefetch
from rest_framework import fields
from rest_framework.serializers import ModelSerializer
from backApp.models import ColorVehicle, Location, TypeVehicle, User, Motorizado, Vehicle, ModelsVehicle


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