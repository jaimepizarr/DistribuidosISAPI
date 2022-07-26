from base64 import decode
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db import models
from django.db.models.fields import related
from rest_framework import serializers
from django.db.models.query import Prefetch
from rest_framework import fields
from rest_framework.serializers import ModelSerializer, Serializer
from backApp.models import ColorVehicle, Local, Location, Order, TypeVehicle, User, Motorizado,Payment, Vehicle,Client, ModelsVehicle,Phone, PhoneUser,MotDeviceRegister, OrderComments, LocalKM, Sector, LocalSector, ClientLocation, PhoneClient


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

class PhoneRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Phone
        fields = ["pho_number"]


class PhoneUserRetrieveSerializer(ModelSerializer):
    idPhone = PhoneRetrieveSerializer(many = False)

    class Meta:
        model = PhoneUser
        fields = ["idPhone"]

class SuperUserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ["id","email","password","first_name","last_name","is_staff","is_superuser"]

    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id",'first_name','last_name',"email","password","number_id","gender","profile_pic","is_operador","is_staff","is_motorizado","is_active","birth_date","home_loc"]
    
    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class UserRetrieveSerializer(UserSerializer):
    home_loc=LocationSerializer(many=False,read_only = True)
    phones = PhoneUserRetrieveSerializer(read_only=True,many=True, source="phoneuser_set")
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["phones","date_joined"]
    

class VehicleSerializer(ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"

class VehicleRetrieveSerializer(VehicleSerializer):
    color = ColorVehicleSerializer(many=False)
    veh_model = ModelsVehicleSerializer(many=False)
    type_vehicle = TypeVehicleSerializer(many=False)

class MotSerializer(ModelSerializer):
    class Meta:
        model = Motorizado
        fields = ["user_id","id_front_photo","id_back_photo","license_front_photo","license_back_photo","isOnline","is_busy","connected"]


class MotUserSerializer(ModelSerializer):
    vehicles = VehicleRetrieveSerializer(read_only=True,many=True, source="vehicle_set")
    user_id = UserRetrieveSerializer(read_only=True,many=False)

    class Meta:
        model = Motorizado
        fields = ["user_id","id_front_photo","id_back_photo","license_front_photo","license_back_photo","isOnline","is_busy","vehicles","connected"]
    
    # # select_related_fields = ('user_id',)
    # @classmethod
    # def setup_eager_loading(cls, queryset):
    #     """ Perform necessary eager loading of data. """
    #     queryset=queryset.select_related('user_id')
    #     # .values('user_id_id__first_name','user_id_id__last_name','user_id_id__email','user_id_id__number_id','user_id_id__is_active')
    #     queryset=queryset.filter(user_id__is_motorizado=False)
    #     return queryset



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

        fields = ["ruc","email","name","logo_img","location_id","admin","password","token"]

    def create(self, validated_data):
        return Local.objects.create_local(**validated_data)

class LocalLoginSerializer(Serializer):
    ruc = serializers.CharField(max_length=15)
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
    location_id = LocationSerializer(many=False)
    class Meta:
        model = Local
        fields = ["ruc","name","email","logo_img","location_id","nombre_mapa","reg_date"]

class ClienteSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"

class ClientLocationSerializer(ModelSerializer):
    location = LocationSerializer(many=False)
    class Meta:
        model = ClientLocation
        fields = "__all__"

class ClientPhoneSerializer(ModelSerializer):
    idPhone = PhoneRetrieveSerializer(many=False)
    class Meta:
        model = PhoneClient
        fields = "__all__"

class ClientRetrieveSerializer(ModelSerializer):
    locations = ClientLocationSerializer(read_only=True,many=True, source="clientlocation_set")
    phones = ClientPhoneSerializer(read_only=True,many=True, source="phoneclient_set")
    class Meta:
        model = Client
        fields = ["id","id_number","name","apellido","email","locations", "phones"]

class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ["id","local","destiny_loc","motorizado","client","payment","details","price","delivery_price","state","start_time","mot_assigned_time","deliv_start_time","arriv_estimated_time","real_arriv_time","is_paid","mot_paid","operador"]
    
    # def create(self, validated_data):
    #     print("HEy")
    #     local_data = validated_data.pop("local")
    #     local = Local.objects.get(ruc=local_data)
    #     print(local)
    #     destiny_local_data = validated_data.pop("destiny_loc")
    #     destiny_local = Location.objects.get(pk=destiny_local_data)
    #     motorizado_data = validated_data.pop("motorizado")
    #     motorizado = Motorizado.objects.get(user_id = motorizado_data)
    #     client_data = validated_data.pop("client")
    #     client = Client.objects.get(pk=client_data)
    #     payment_data = validated_data.pop("payment")
    #     payment = Payment.objects.get(pk=payment_data)
    #     order = Order.objects.create(local = local,
    #                                 destiny_local=destiny_local,
    #                                 motorizado=motorizado,
    #                                 client=client,
    #                                 payment=payment,
    #                                 **validated_data)
    #     return order

class OrderAssignReturnSerializer(OrderSerializer):
    operador = UserRetrieveSerializer(many=False)

class OrderAllSerializer(OrderSerializer):
    local=LocalSerializer(many=False)
    destiny_loc=LocationSerializer(many=False)
    motorizado=MotUserSerializer(many=False)
    client=ClienteSerializer(many=False)
    payment=PaymentSerializer(many=False)
    
class PhoneSerializer(ModelSerializer):
    class Meta:
        model = Phone
        fields = "__all__"
        
class PhoneUserSerializer(ModelSerializer):
    class Meta:
        model = PhoneUser
        fields = "__all__"

class MotDeviceRegisterSerializer(ModelSerializer):
    class Meta:
        model = MotDeviceRegister
        fields = "__all__"

class OrderCommentsSerializer(ModelSerializer):
    class Meta:
        model = OrderComments
        fields = "__all__"

class LocalNameSerializer(ModelSerializer):
    class Meta:
        model = Local
        fields = ["ruc","name"]

class LocalKmSerializer(ModelSerializer):
    class Meta:
        model = LocalKM
        fields = "__all__"
        lookup_field  = "local"
class LocalKmRetrieveSerializer(LocalKmSerializer):
    local = LocalNameSerializer(many=False)


# class MapSerializer(ModelSerializer):
#     class Meta:
#         model = Map
#         fields = "__all__"

class SectorSerializer(ModelSerializer):
    class Meta:
        model = Sector
        fields = "__all__"

class LocalSectorSerializer(ModelSerializer):
    class Meta:
        model = LocalSector
        fields = "__all__"

class LocalMapNameSerializer(ModelSerializer):
    class Meta:
        model = Local
        fields = ["ruc","nombre_mapa"]

class LocalSectorRetrieveSerializer(ModelSerializer):
    sector = SectorSerializer(many=False)
    local = LocalMapNameSerializer(many=False)
    class Meta:
        model = LocalSector
        fields = "__all__"