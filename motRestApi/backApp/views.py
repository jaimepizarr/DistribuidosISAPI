from django.forms.forms import Form
from django.http.response import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from backApp.models import ColorVehicle, User,Motorizado, Vehicle, TypeVehicle,ModelsVehicle
from backApp.serializers import LocationSerializer, ModelsVehicleSerializer, UserSerializer, MotSerializer, VehicleSerializer, ColorVehicleSerializer, TypeVehicleSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view


class UserSignUp(APIView):
    def post(self,request,format=None):
        parser_classes= [MultiPartParser, FormParser]
        location = LocationSerializer(data = request.data)
        location.is_valid(raise_exception=True)
        location.save()
        id_location = location.data.get("id")
        request.data.setdefault("id_location",id_location)
        user = UserSerializer(data=request.data)
        user.is_valid(raise_exception=True)
        user.save()
        return Response(status=status.HTTP_200_OK, data=user.data)


class MotorizadoSignUp(APIView):
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