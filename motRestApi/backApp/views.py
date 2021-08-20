from rest_framework_simplejwt import authentication
from backApp.permissions import OperadorAuthenticated
from django.forms.forms import Form
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from backApp.models import ColorVehicle, User,Motorizado, Vehicle, TypeVehicle,ModelsVehicle,Order
from backApp.serializers import LocalLoginSerializer, LocalRegistrationSerializer, LocationSerializer, ModelsVehicleSerializer, OrderSerializer, UserSerializer, MotSerializer, VehicleSerializer, ColorVehicleSerializer, TypeVehicleSerializer
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from django.core import serializers
import json

class UserSignUp(APIView):
    parser_classes= [MultiPartParser, FormParser]
    def post(self,request,format=None):
        location = LocationSerializer(data = request.data)
        location.is_valid(raise_exception=True)
        location.save()
        id_location = location.data.get("id")
        request.data.setdefault("home_loc",id_location)
        user = UserSerializer(data=request.data)
        user.is_valid(raise_exception=True)
        user.save()
        return Response(status=status.HTTP_200_OK, data=user.data)

class LocalRegistrationView(APIView):
    parser_classes= [MultiPartParser, FormParser]

    def post(self,request,format=None):
        
        location = LocationSerializer(data = request.data)
        location.is_valid(raise_exception=True)
        location.save()
        id_location = location.data.get("id")
        

        request.data.setdefault("location_id",id_location)
        local = LocalRegistrationSerializer(data = request.data)
        local.is_valid(raise_exception=True)
        
        local.save()

        return Response(data=local.data, status=status.HTTP_201_CREATED)


class LocalLoginView(APIView):

    def post(self,request):
        local = LocalLoginSerializer(data= request.data)
        local.is_valid(raise_exception=True)

        return Response(local.data,status=status.HTTP_200_OK)

class MotorizadoView(APIView):
    parser_classes= [MultiPartParser, FormParser]
    def post(self,request):
        motorizado = MotSerializer(data = request.data)
        motorizado.is_valid(raise_exception=True)
        motorizado.save()
        id_mot = motorizado.data.get("user_id")
        request.data.setdefault("motorizado",id_mot)
        vehicle = VehicleSerializer(data=request.data)
        vehicle.is_valid(raise_exception=True)
        vehicle.save()
        return Response(status = status.HTTP_200_OK, data=motorizado.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def upd_mot(request, id):
    motorizado = Motorizado.objects.get(user_id=id)

    serializer = MotSerializer(motorizado, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_200_OK,data=serializer.data)

    return Response(status=status.HTTP_400_BAD_REQUEST)    

@api_view(['GET'])
def get_colors(request):
    colors=ColorVehicle.objects.all()
    colors_serializer = ColorVehicleSerializer(colors, many=True)
    return JsonResponse(colors_serializer.data, safe=False)

@api_view(['GET'])
def get_type(request):
    type_vehicle=TypeVehicle.objects.all()
    type_vehicle_serializer = TypeVehicleSerializer(type_vehicle, many=True)
    return JsonResponse(type_vehicle_serializer.data, safe=False)

@api_view(['GET'])
def get_models(request):
    model_vehicle=ModelsVehicle.objects.all()
    type_vehicle=request.query_params.get('type_vehicle')
    if type_vehicle is not None:
        model_vehicle=model_vehicle.filter(type_vehicle=type_vehicle)

    model_vehicle_serializer = ModelsVehicleSerializer(model_vehicle, many=True)
    return JsonResponse(model_vehicle_serializer.data, safe=False)

@api_view(['GET'])
def get_motorizados(request):
    motorizados=Motorizado.objects.all()
    qs = MotSerializer.setup_eager_loading(motorizados)
    motorizados_serializer=MotSerializer(qs, many=True)
    return JsonResponse(motorizados_serializer.data, safe=False)

@api_view(['PUT'])
def update_motorizado(request):
    motorizado = User.objects.filter(id=request.data['id']).first()
    serializer = UserSerializer(motorizado, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_200_OK,data=serializer.data)

    return Response(status=status.HTTP_400_BAD_REQUEST)    

@api_view(['GET'])
def get_orders(request):
    orders=Order.objects.all()
    qs = OrderSerializer.setup_eager_loading(orders)
    orders_serializer=OrderSerializer(qs, many=True)
    return JsonResponse(orders_serializer.data, safe=False)

