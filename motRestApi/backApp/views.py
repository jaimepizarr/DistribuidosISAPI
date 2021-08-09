from django.shortcuts import render
from rest_framework.views import APIView
from backApp.models import User
from backApp.serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status

class UserSignUp(APIView):
    def post(self,request):
        user = UserSerializer(data=request.POST)
        user.is_valid(raise_exception=True)
        user.save()
        return Response(status=status.HTTP_200_OK, data=user.data)

class MotorizadoSignUp():
    pass


        