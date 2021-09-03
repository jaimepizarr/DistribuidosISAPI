from datetime import datetime
from functools import partial
import re
from typing import Dict
from django.db.models import query
from backApp.permissions import LocalAuthenticated
from django.http.response import HttpResponse, JsonResponse
from django.http import QueryDict
from django.shortcuts import render
from rest_framework.views import APIView
from backApp.models import ColorVehicle, Local, User,Motorizado, Vehicle, TypeVehicle,ModelsVehicle,Order,Client,Location
from backApp.serializers import LocalLoginSerializer, LocalRegistrationSerializer, LocationSerializer, ModelsVehicleSerializer, OrderAllSerializer, UserSerializer, MotSerializer, VehicleSerializer, ColorVehicleSerializer, TypeVehicleSerializer, MotUserSerializer, OrderSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from django.core import serializers
from rest_framework import viewsets
import json
from django.conf import settings
import requests

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

    def patch(self,request,id):
        user = User.objects.get(id = id)
        serializer = UserSerializer(user, data = request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data = serializer.data)

class LocalRegistrationView(APIView):
    parser_classes= [MultiPartParser, FormParser]

    def post(self,request,format=None):
        req = QueryDict.copy(request.POST)
        req["logo_img"] = request.data.get("logo_img")
        location = LocationSerializer(data = req)
        location.is_valid(raise_exception=True)
        location.save()
        id_location = location.data.get("id")

        req.setdefault("location_id",id_location)
        local = LocalRegistrationSerializer(data = req)
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


class MotorizadoUserView(viewsets.ModelViewSet):
    queryset = Motorizado.objects.all()
    serializer_class = MotUserSerializer


class MotToAssignView(viewsets.ReadOnlyModelViewSet):
    queryset = Motorizado.objects.filter(user_id__is_motorizado=0,
                                        user_id__is_operador=0,
                                        user_id__is_staff = 0).all()
    serializer_class = MotUserSerializer

class OrderRetrieveView(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderAllSerializer

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
    # motorizados=Motorizado.objects.all()
    # qs = MotSerializer.setup_eager_loading(motorizados)
    # motorizados_serializer=MotSerializer(qs, many=True)
    qs = Motorizado.objects.all().select_related("user_id")
    motorizados_serializer=MotSerializer(qs)
    return Response(data = motorizados_serializer.data, status = status.HTTP_200_OK)

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
    orders_serializer=OrderAllSerializer(orders, many=True)
    return JsonResponse(orders_serializer.data, safe=False)

@api_view(["POST"])
@permission_classes([LocalAuthenticated])
def post_order(request):
    req = dict.copy(request.data)
    req_client = req.get("client")
    client = Client.objects.get_or_create(id_number=req_client.get("id_number"),defaults=req_client)
    req_location = req.get("destiny_loc")
    destiny = Location.objects.get_or_create(latitude=req_location["latitude"],
                                            longitude=req_location["longitude"],
                                            reference=req_location["reference"],
                                            defaults=req_location)
    #The following code is how the distance and duration should be gotten from google api

    # local = Local.objects.get(ruc=req.get("local"))
    # local_location = local.location_id
    #origin = local_location.longitude, local_location.latitude
    #destination = destiny.longitude, destiny.latitude
    # distance_matrix = json.load(getDistance(origin,destination)) 
    # distance = distance_matrix["rows"][0]["elements"][0]["distance"]
    # duration = distance_matrix["rows"][0]["elements"][0]["duration"]

    req["client"] = client[0].id
    req["destiny_loc"] = destiny[0].id
    order = OrderSerializer(data = req)
    order.is_valid(raise_exception=True)
    order.save()
    return Response(data=order.data)

@api_view(["PATCH"])
def assign_order(request, id):
    order = Order.objects.get(id = id)
    req = request.data.copy()
    req["mot_assigned_time"] = datetime.now()
    serializer = OrderSerializer(order, data = req,partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status=status.HTTP_200_OK, data = serializer.data)


def getDistance(origin,destination):
    google_key = settings.GOOGLE_API_KEY
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={},{}&destinations={},{}&key={}".format(origin[0],origin[1],destination[0],destination[1],google_key)
    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()
