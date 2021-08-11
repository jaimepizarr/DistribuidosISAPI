from django.forms.forms import Form
from django.shortcuts import render
from rest_framework.views import APIView
from backApp.models import User,Motorizado, Vehicle
from backApp.serializers import LocationSerializer, UserSerializer, MotSerializer, VehicleSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser


class UserSignUp(APIView):
    def post(self,request,format=None):
        parser_classes= [MultiPartParser, FormParser]
        print(request.data)
        location = LocationSerializer(data = request.data)
        location.is_valid(raise_exception=True)
        location.save()
        id_location = location.data.get("id")
        request.data.setdefault("id_location",id_location)
        user = UserSerializer(data=request.data)
        user.is_valid(raise_exception=True)
        user.save()
        print(user.data)
        return Response(status=status.HTTP_200_OK, data=user.data)


class MotorizadoSignUp(APIView):
    parser_classes= [MultiPartParser, FormParser]
    def post(self,request):
        motorizado = MotSerializer(data = request.data)
        motorizado.is_valid(raise_exception=True)
        motorizado.save()
        id_mot = motorizado.data.get("id")
        request.data.setdefault("motorizado",id_mot)
        vehicle = VehicleSerializer(data=request.data)
        vehicle.is_valid(raise_exception=True)
        vehicle.save()
        return Response(status = status.HTTP_200_OK, data=motorizado.data)
    



        