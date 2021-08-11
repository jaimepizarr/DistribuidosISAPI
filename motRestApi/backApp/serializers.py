from django.db import models
from rest_framework.serializers import ModelSerializer
from backApp.models import Location, User, Motorizado, Vehicle

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","email","password","number_id","gender","profile_pic","is_operador","home_loc"]

    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ["id","longitude","latitude","reference"]

class MotSerializer(ModelSerializer):
    class Meta:
        model = Motorizado
        fields = ["id","id_front_photo","id_back_photo","license_front_photo","license_back_photo"]

class VehicleSerializer(ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"