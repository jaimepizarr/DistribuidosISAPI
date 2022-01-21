from datetime import datetime, timedelta
from functools import partial
import re
from typing import Dict
from django.db.models import query
from drf_yasg import openapi
from rest_framework.utils.serializer_helpers import ReturnDict
from backApp.permissions import LocalAuthenticated
from django.http.response import HttpResponse, JsonResponse
from django.http import QueryDict
from django.shortcuts import render
from rest_framework.views import APIView
from backApp.models import ColorVehicle, Local, User, Motorizado, Vehicle, TypeVehicle, ModelsVehicle, Order, Client, Location, MotDeviceRegister, OrderComments, ClientLocation
from backApp.serializers import *
from rest_framework.response import Response
from rest_framework import mixins, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from django.core import serializers
from rest_framework import viewsets
import json
from django.conf import settings
import requests
import firebase_admin
from firebase_admin import credentials, firestore, messaging
import ast
from drf_yasg.utils import swagger_auto_schema



class SuperUser(APIView):

    def post(self, request):
        superuser = SuperUserSerializer(data=request.data)
        if superuser.is_valid():
            superuser.save()
            return Response(superuser.data, status=status.HTTP_201_CREATED)
        return Response(superuser.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSignUp(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        profile_pic = dict((request.data).lists())["profile_pic"][0]
        # Create Location
        request = QueryDict.copy(request.POST)
        request.setdefault("profile_pic", profile_pic)
        location = LocationSerializer(data=request)
        location.is_valid(raise_exception=True)
        location.save()
        id_location = location.data.get("id")
        request.setdefault("home_loc", id_location)
        # Create user
        request.setdefault("is_active", True)
        user = UserSerializer(data=request)
        user.is_valid(raise_exception=True)
        user.save()
        # Create Phone
        ph_number = request.get("phone_number")
        phone = PhoneSerializer(data={"pho_number": ph_number})
        phone.is_valid(raise_exception=True)
        phone.save()
        # Join Phone and USer
        print(user.data)
        phone_user_dict = {
            "idPhone": phone.data.get("id"),
            "user": user.data.get("id")
        }
        phone_user = PhoneUserSerializer(data=phone_user_dict)
        phone_user.is_valid(raise_exception=True)
        phone_user.save()
        return Response(status=status.HTTP_200_OK, data={"user": user.data, "phone": phone.data})

    def patch(self, request, id):
        user = User.objects.get(id=id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class UserComments(APIView):
    def post(self, request, id):
        db = firestore.client()
        data = request.data
        db.collection('mot_data_comments').document(str(id)).set(data)
        return Response(status=status.HTTP_200_OK)
    
    def get(self, request, id):
        db = firestore.client()
        data = db.collection('mot_data_comments').document(str(id)).get().to_dict()
        return Response(status=status.HTTP_200_OK, data=data)
    


@api_view(['POST'])
def register_motdevice(request):
    motDeviceRegister = MotDeviceRegister.objects.filter(
        idDevice=request.data.get("idDevice"))
    if motDeviceRegister:
        return Response(status=status.HTTP_200_OK, data={"message": "Device already registered"})
    else:
        deviceRegister = MotDeviceRegisterSerializer(data=request.data)
        if deviceRegister.is_valid():
            deviceRegister.save()
            return Response(deviceRegister.data, status=status.HTTP_201_CREATED)
        return Response(deviceRegister.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveView(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserRetrieveSerializer


class OperadorRetrieveView(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True, is_operador=True)
    serializer_class = UserRetrieveSerializer


class LocalRegistrationView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        req = QueryDict.copy(request.POST)
        req["logo_img"] = request.data.get("logo_img")
        location = LocationSerializer(data=req)
        location.is_valid(raise_exception=True)
        location.save()
        id_location = location.data.get("id")

        req.setdefault("location_id", id_location)
        local = LocalRegistrationSerializer(data=req)
        local.is_valid(raise_exception=True)

        local.save()

        return Response(data=local.data, status=status.HTTP_201_CREATED)

    def get(self, request, format=None, id=None):
        if id:
            local = Local.objects.get(id=id)
            local_ser = LocalSerializer(local)
            local_ser.is_valid(raise_exception=True)
        else:
            locales = Local.objects.all()
            local_ser = LocalSerializer(locales, many=True)
        return Response(status=status.HTTP_200_OK, data=local_ser.data)


class LocalLoginView(APIView):
    def post(self, request):
        local = LocalLoginSerializer(data=request.data)
        local.is_valid(raise_exception=True)

        return Response(local.data, status=status.HTTP_200_OK)


class MotorizadoView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        motorizado = MotSerializer(data=request.data)
        motorizado.is_valid(raise_exception=True)
        motorizado.save()
        id_mot = motorizado.data.get("user_id")
        request.data.setdefault("motorizado", id_mot)
        vehicle = VehicleSerializer(data=request.data)
        vehicle.is_valid(raise_exception=True)
        vehicle.save()
        return Response(status=status.HTTP_200_OK, data=motorizado.data)


class MotorizadoUserView(viewsets.ReadOnlyModelViewSet):
    users = User.objects.filter(is_active=True)
    queryset = Motorizado.objects.filter(user_id__in=users)
    serializer_class = MotUserSerializer


class MotToAssignView(viewsets.ReadOnlyModelViewSet):
    queryset = Motorizado.objects.filter(user_id__is_motorizado=0,
                                         user_id__is_operador=0,
                                         user_id__is_staff=0,
                                         user_id__is_active=1).all()
    serializer_class = MotUserSerializer


@api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
def upd_mot(request, id):
    motorizado = Motorizado.objects.get(user_id=id)
    serializer = MotSerializer(motorizado, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    return Response(status=status.HTTP_400_BAD_REQUEST)

def change_active_mode(id, is_active):
    motorizado = User.objects.get(id=id)
    data_ser = {"is_active": is_active}
    serializer = UserSerializer(motorizado, data=data_ser, partial=True)
    if serializer.is_valid():
        serializer.save()
        if is_active:
            return Response(status=status.HTTP_200_OK, data={"message": "Motorizado activado"})
        return Response(status=status.HTTP_200_OK, data={"message": "Motorizado desactivado"})

    return Response(status=status.HTTP_400_BAD_REQUEST, data=[])

@api_view(['PATCH'])
def unactivate_user(request, id):
    return change_active_mode(id, False)

@api_view(['PATCH'])
def activate_user(request, id):
    return change_active_mode(id, True)

@api_view(['GET'])
def get_motorizados(request):
    # motorizados=Motorizado.objects.all()
    # qs = MotSerializer.setup_eager_loading(motorizados)
    # motorizados_serializer=MotSerializer(qs, many=True)
    qs = Motorizado.objects.all().select_related("user_id")
    motorizados_serializer = MotSerializer(qs)
    return Response(data=motorizados_serializer.data, status=status.HTTP_200_OK)


class OrderRetrieveView(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderAllSerializer


class OrderCommentsView(viewsets.ModelViewSet):
    queryset = OrderComments.objects.all()
    serializer_class = OrderCommentsSerializer
    lookup_field = 'idOrder'


@api_view(['GET'])
def get_colors(request):
    colors = ColorVehicle.objects.all()
    colors_serializer = ColorVehicleSerializer(colors, many=True)
    return JsonResponse(colors_serializer.data, safe=False)


@api_view(['GET'])
def get_type(request):
    type_vehicle = TypeVehicle.objects.all()
    type_vehicle_serializer = TypeVehicleSerializer(type_vehicle, many=True)
    return JsonResponse(type_vehicle_serializer.data, safe=False)


@api_view(['GET'])
def get_models(request):
    model_vehicle = ModelsVehicle.objects.all()
    type_vehicle = request.query_params.get('type_vehicle')
    if type_vehicle is not None:
        model_vehicle = model_vehicle.filter(type_vehicle=type_vehicle)

    model_vehicle_serializer = ModelsVehicleSerializer(
        model_vehicle, many=True)
    return JsonResponse(model_vehicle_serializer.data, safe=False)


@api_view(["GET"])
def getvehiclesbymot(request):
    motorizado = request.GET.get("motorizado", None)
    if motorizado == None:
        raise NameError
    vehicles = Vehicle.objects.get(motorizado=motorizado)
    serializer = VehicleRetrieveSerializer(vehicles)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


# @api_view(['Patch'])
# def update_motorizado(request):
#     print(request.data)
#     motorizado = User.objects.filter(id=request.data['id']).first()
#     serializer = UserSerializer(motorizado, data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(status=status.HTTP_200_OK,data=serializer.data)

#     return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_orders(request):
    orders = Order.objects.all()
    orders_serializer = OrderAllSerializer(orders, many=True)
    return JsonResponse(orders_serializer.data, safe=False)


@api_view(["POST"])
# permission_classes([LocalAuthenticated])
def post_order(request):
    req = dict.copy(request.data)
    req_client = req.get("client")
    client = Client.objects.get_or_create(
        id_number=req_client.get("id_number"), defaults=req_client)
    req_location = req.get("destiny_loc")
    destiny = Location.objects.get_or_create(latitude=req_location["latitude"],
                                             longitude=req_location["longitude"],
                                             reference=req_location["reference"],
                                             defaults=req_location)[0]
    ClientLocation.objects.get_or_create(client = client[0], location = destiny)

    req["client"] = client[0].id
    req["destiny_loc"] = destiny.id
    req["state"] = 1
    order = OrderSerializer(data=req)
    order.is_valid(raise_exception=True)
    order.save()
    # print(order.data)
    return Response(data=order.data, status=status.HTTP_201_CREATED)


def sendPushNotification(title, message, code, idOrder, tokens):
    dataObject = {
        'idOrder': idOrder,
        'code': code
    }
    notifSend = messaging.Notification(title=title, body=message)
    sendMes = messaging.MulticastMessage(
        notification=notifSend,
        data={'title': 'Objeto', 'body': json.dumps(
            dataObject, separators=(',', ':'))},
        tokens=tokens,
    )

    respues = messaging.send_multicast(sendMes)
    print("repsuesta", respues)


@api_view(["PATCH"])
def assign_order(request, id):
    order = Order.objects.get(id=id)
    # The following code is how the distance and duration should be gotten from google api
    req = request.data.copy()
    queue = Order.objects.filter(state__in=[2, 3, 4, 5], motorizado=req["motorizado"]).order_by("-mot_assigned_time")
    if len(queue) > 0:
        last_order = queue[0]
        start_time = last_order.arriv_estimated_time
        last_location  = last_order.destiny_loc
        origin = (last_location.latitude, last_location.longitude)
        print("Si hay cola",origin)
    else:
        start_time = datetime.now()
        motorizado = order.motorizado
        
        db = firestore.client()
        ruc = req["motorizado"]
        print(ruc)
        origin = db.collection("motorizados").document(
            str(ruc)).get()
        print(origin.exists)
        print(origin.to_dict())
        if origin.exists:
            origin = origin.to_dict()
            origin  = (origin.get("lat"), origin.get("lng")) 
        print("No hay cola",origin)
    local = order.local
    print(local.name)
    local_location = local.location_id.latitude, local.location_id.longitude
    print(f"Local_location {local_location[0]}, {local_location[1]}")

    destination = (order.destiny_loc.latitude, order.destiny_loc.longitude)
    
    first_dist_matrix = getDistance(origin, local_location)
    print(first_dist_matrix)
    if first_dist_matrix["rows"][0]["elements"][0]["status"] == "ZERO_RESULTS":
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": f"No se pudo calcular la distancia entre el origen:{origin} y el local:{local_location} "})
    first_distance = first_dist_matrix["rows"][0]["elements"][0]["distance"]["value"]
    first_duration = first_dist_matrix["rows"][0]["elements"][0]["duration"]["value"]
    second_dist_matrix = getDistance(local_location, destination)
    if second_dist_matrix["rows"][0]["elements"][0]["status"] == "ZERO_RESULTS":
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": f"No se pudo calcular la distancia entre el local:{local_location} y su destino:{destination}"})
    print(second_dist_matrix)
    second_distance = second_dist_matrix["rows"][0]["elements"][0]["distance"]["value"]
    second_duration = second_dist_matrix["rows"][0]["elements"][0]["duration"]["value"]

    total_duration = first_duration + second_duration
    estimated_arriv_time = start_time + timedelta(seconds=total_duration) + timedelta(minutes=3)

    req["arriv_estimated_time"] = estimated_arriv_time.isoformat()
    req["mot_assigned_time"] = datetime.now().isoformat()
    print(req["arriv_estimated_time"])
    motorizado = Motorizado.objects.get(user_id=req["motorizado"])
    mot_serializer = MotSerializer(
        motorizado, data={"is_busy": True}, partial=True)
    mot_serializer.is_valid(raise_exception=True)
    mot_serializer.save()
    req["state"] = 2
    serializer = OrderSerializer(order, data=req, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    devices = MotDeviceRegister.objects.filter(idMot=req["motorizado"])
    lista_regis = []
    for device in devices:
        lista_regis.append(device.idDevice)
    # # lista_regis=['fr5MWLf3TrW1Q0XR2Oij8R:APA91bGkGZsB3JEaaxS_xmJ1uOQi8hvVt2Mltparpym2PvO2tXZeaeIqt7JAVT3ImC9__Capcck9pRxfTRDOJdXnlYhAzhF_iXqFiJdB7e37rYympmlQXZR8AaeHQiRTkxI56f1t_00e','egqWrJv4Tg-qLWfxVTs-97:APA91bF14OiLvQzvLwZdyoZ5ccgKYvjNNaIKgKHlMxp6tyMwoThRuRV911lnQgqcDkD9VGDKKUbpWiiMMDgLRcI6FRXmCVMqE3cZGnLDNdZsPffPPp0K5BrGHXTWAC_6IsMXAKdypAhE']
    # # dataSended = {
    # #     'message': 'Se ha asignado una nueva orden',
    # #     'code': 1
    # # }
    # # notif=messaging.Notification(title='Nueva orden',body=json.dumps(dataSended, separators=(',',':')))
    # # prueba =messaging.MulticastMessage(
    # #     notification=notif,
    # #     data={
    # #         'title': 'Nueva orden',
    # #         'body': json.dumps(dataSended, separators=(',',':')),
    # #     },
    # #     tokens=lista_regis,
    # # )
    # # respues=messaging.send_multicast(prueba)
    # # print ("repsuesta",respues)

    # # print(serializer.data)
    sendPushNotification(
        'Nueva orden', 'Se le ha asignado una nueva orden', 1, id, lista_regis)
    returnSerializer = OrderAssignReturnSerializer(order)
    return Response(status=status.HTTP_200_OK, data=returnSerializer.data)


def getDistance(origin, destination):
    google_key = settings.GOOGLE_API_KEY
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={},{}&destinations={},{}&key={}".format(
        origin[0], origin[1], destination[0], destination[1], google_key)
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)

    return response.json()

# Empresa necesita conocer el motorizado de un pedido
# @permission_classes([LocalAuthenticated])


@api_view(["GET"])
def get_motorizado_order(request):
    order_id = request.query_params["id"]
    order_obj = Order.objects.get(id=order_id)
    motorizado_id = order_obj.motorizado
    motorizado_obj = Motorizado.objects.get(user_id=motorizado_id)

    motorizado = MotUserSerializer(motorizado_obj)
    return Response(data=motorizado.data)


@api_view(["PATCH"])
def change_data_order(request, id):
    order = Order.objects.get(id=id)

    serializer = OrderSerializer(order, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status=status.HTTP_200_OK, data=serializer.data)


@api_view(["PATCH"])
def revoke_order(request, id):
    order = Order.objects.get(id=id)
    motorizado = order.motorizado
    data = {"motorizado": None,
            "state": 1, }
    serializer = OrderSerializer(order, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    dataSended = {
        'message': 'Se ha revocado su orden',
        'code': 2
    }
    # lista_regis=['fr5MWLf3TrW1Q0XR2Oij8R:APA91bGkGZsB3JEaaxS_xmJ1uOQi8hvVt2Mltparpym2PvO2tXZeaeIqt7JAVT3ImC9__Capcck9pRxfTRDOJdXnlYhAzhF_iXqFiJdB7e37rYympmlQXZR8AaeHQiRTkxI56f1t_00e','egqWrJv4Tg-qLWfxVTs-97:APA91bF14OiLvQzvLwZdyoZ5ccgKYvjNNaIKgKHlMxp6tyMwoThRuRV911lnQgqcDkD9VGDKKUbpWiiMMDgLRcI6FRXmCVMqE3cZGnLDNdZsPffPPp0K5BrGHXTWAC_6IsMXAKdypAhE']
    devices = MotDeviceRegister.objects.filter(idMot=motorizado)
    lista_regis = []
    for device in devices:
        lista_regis.append(device.idDevice)
    sendPushNotification(
        'Orden revocada', 'Se le ha revocado una orden', 2, id, lista_regis)
    # prueba =messaging.MulticastMessage(
    #     data={
    #         'title': 'Orden revocada',
    #         'body': json.dumps(dataSended, separators=(',',':')),
    #     },
    #     tokens=lista_regis
    # )
    # prueba =messaging.MulticastMessage(
    #     tokens=lista_regis,
    #     notification=messaging.Notification(
    #         data={
    #         'title': 'Orden revocada',
    #         'body': json.dumps(dataSended, separators=(',',':')),
    #     }
    # ))
    # messa=messaging.Message(
    #     # data={
    #     #     'title': 'Orden revocada',
    #     #     'body': json.dumps(dataSended, separators=(',',':')),
    #     # },
    #     notification=messaging.Notification(
    #         title='Orden revocada',
    #         body='Orden revocada',
    #         icon='https://goo.gl/Fz9nrQ',
    #         click_action='https://goo.gl/Fz9nrQ'
    #     ),
    #     android=messaging.AndroidConfig(
    #     ttl=datetime.timedelta(seconds=3600),
    #     priority='normal',
    #     notification=messaging.AndroidNotification(
    #         icon='stock_ticker_update',
    #         color='#f45342',
    #         priority='high',
    #     ),
    # ),
    # apns=messaging.APNSConfig(
    #     payload=messaging.APNSPayload(
    #         aps=messaging.Aps(badge=42),
    #     ),
    # ),
    #     token='fr5MWLf3TrW1Q0XR2Oij8R:APA91bGkGZsB3JEaaxS_xmJ1uOQi8hvVt2Mltparpym2PvO2tXZeaeIqt7JAVT3ImC9__Capcck9pRxfTRDOJdXnlYhAzhF_iXqFiJdB7e37rYympmlQXZR8AaeHQiRTkxI56f1t_00e'
    # )
    # response = messaging.send(messa)
    # print(response)
    # return Response(status=status.HTTP_200_OK, data = serializer.data)
    # respues=messaging.send_multicast(prueba)
    # print ("repsuesta",respues)
    return Response(status=status.HTTP_200_OK, data=serializer.data)


@api_view(["GET"])
def user_exists(request):
    email = request.query_params.get("email")
    try:
        user = User.objects.get(email=email)
    except:
        return Response(status=status.HTTP_200_OK, data={"exists": False})
    return Response(status=status.HTTP_200_OK, data={"exists": True})


@api_view(["GET"])
def get_order_state(request):
    id = request.query_params.get("id")
    equivalencia = Order.state_eq
    order = Order.objects.get(id=id)
    state_id = order.state
    state_descrip = equivalencia.get(state_id)
    return Response(status=status.HTTP_200_OK, data={"state": state_descrip})


@api_view(["GET"])
def get_mot_orders(request, id):
    motorizado = Motorizado.objects.get(user_id=id)
    orders = Order.objects.filter(motorizado=motorizado)
    if len(orders):
        serializer = OrderAllSerializer(orders, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    return Response(status=status.HTTP_204_NO_CONTENT, data=[])


@api_view(["GET"])
def get_mot_orders_active(request, id):
    motorizado = Motorizado.objects.filter(user_id=id, user_id__is_active=True)[0]
    orders = Order.objects.filter(
        motorizado=motorizado).filter(state__in=[3, 4, 5])
    if len(orders):
        serializer = OrderAllSerializer(orders, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    return Response(status=status.HTTP_204_NO_CONTENT, data=[])


@api_view(["GET"])
def get_mot_orders_assigned(request, id):
    motorizado = Motorizado.objects.filter(user_id=id, user_id__is_active=True)[0]
    orders = Order.objects.filter(motorizado=motorizado).filter(
        state__in=[2, 3, 4, 5])  # Retornar 2,3,4,5
    if len(orders):
        serializer = OrderAllSerializer(orders, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    return Response(status=status.HTTP_204_NO_CONTENT, data=[])


@api_view(["GET"])
def get_mot_orders_finished(request, id):
    motorizado = Motorizado.objects.get(user_id=id)
    orders = Order.objects.filter(motorizado=motorizado).filter(state=6)
    if len(orders):
        serializer = OrderAllSerializer(orders, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    return Response(status=status.HTTP_204_NO_CONTENT, data=[])


@api_view(["PATCH"])
def accept_order(request, id):
    order = Order.objects.get(id=id)
    data = {"state": 3}
    serializer = OrderSerializer(order, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status=status.HTTP_200_OK, data=serializer.data)


@api_view(["PATCH"])
def reject_order(request, id):
    order = Order.objects.get(id=id)
    motorizado = order.motorizado
    data = {"state": 1,
            "mot_assigned_time": None,
            "motorizado": None, }
    serializer = OrderSerializer(order, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return_data = dict(serializer.data).update({"rejected_by": motorizado})
    return Response(status=status.HTTP_200_OK, data=return_data)


@api_view(["GET"])
def count_by_mot(request, id):
    motorizado = Motorizado.objects.get(user_id=id)
    orders = Order.objects.filter(motorizado=motorizado).filter(state=6)
    return Response(status=status.HTTP_200_OK, data={"count": len(orders)})


@api_view(["GET"])
def orders_by_dates(request):
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")
    motorizado = request.query_params.get("motorizado")
    if start_date or end_date:
        if(start_date and end_date):
            orders = Order.objects.filter(motorizado=motorizado).filter(
                start_time__range=[start_date, end_date])
        elif (start_date):
            orders_all = Order.objects.filter(motorizado=motorizado)
            orders = []
            for order in orders_all:
                if str(datetime.date(order.start_time)) == start_date:
                    orders.append(order.id)
            orders = Order.objects.filter(id__in=orders)
        serializer = OrderAllSerializer(orders, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST, data=[])


@api_view(["GET"])
def get_mot_location(request, id):
    order = Order.objects.get(id=id)
    if order.state == 1:
        return Response(status=status.HTTP_204_NO_CONTENT, data={"description": "La orden está en espera de ser asignada"})
    if order.state in (2, 3):
        return Response(status=status.HTTP_204_NO_CONTENT, data={"description": "La orden aún no está siendo recogida"})
    if order.state in (4, 5):
        motorizado = order.motorizado
        mot_ser = MotSerializer(motorizado)
        db = firestore.client()
        location = db.collection("motorizados").document(
            str(mot_ser.data.get("user_id"))).get()
        if location.exists:
            location = location.to_dict()
            return Response(status=status.HTTP_200_OK, data=location)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=[])
    if order.state == 6:
        return Response(status=status.HTTP_204_NO_CONTENT, data={"description": "La orden ya ha terminado"})


class LocalKmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LocalKM.objects.all()
    serializer_class = LocalKmRetrieveSerializer
    lookup_field = 'local'


@api_view(["POST"])
def postLocalKm(request):
    serializer = LocalKmSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


@api_view(["PATCH"])
def updateLocalKm(request, id):
    localkm_obj = LocalKM.objects.all().get(local=id)
    serializer = LocalKmSerializer(
        localkm_obj, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

# class LocalSectorViewSet(viewsets.ModelViewSet):
#     queryset = LocalSector.objects.all()
#     serializer_class = LocalSectorSerializer
#     lookup_field = 'local'


def saveNombreMapa(ruc):
    local = Local.objects.get(ruc=ruc)
    nombre = local.name
    mapa = "Mapa_"+nombre
    local_serializer = LocalSerializer(
        local, data={"nombre_mapa": mapa}, partial=True)
    local_serializer.is_valid(raise_exception=True)
    local_serializer.save()
    print(local_serializer.data)


def createSector(sector_new, coordenadas_new, ruc, price):
    data_sector = {"sector_name": sector_new,
                   "limits": str(coordenadas_new)}
    serializer = SectorSerializer(data=data_sector)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    id_sector = serializer.data.get("id")
    data_local_sector = {"local": ruc, "sector": id_sector, "price": price}
    serializer_local_sector = LocalSectorSerializer(data=data_local_sector)
    serializer_local_sector.is_valid(raise_exception=True)
    serializer_local_sector.save()


class MapView(APIView):

    def post(self, request, format=None):
        entry = request.data
        ruc = entry.get("ruc")
        d_sectores = entry.get("sectores")
        if type(d_sectores) == str:
            d_sectores = ast.literal_eval(d_sectores)
        for sector_new, d_sector in d_sectores.items():
            price = d_sector.get("price")
            limits_new = d_sector.get("limits")
            coordenadas_new = [(i["latitude"], i["longitude"])
                               for i in limits_new]
            sectors_all = Sector.objects.all()
            if len(sectors_all) == 0:
                createSector(sector_new, coordenadas_new, ruc, price)
                saveNombreMapa(ruc)
            else:
                sector_exist = False
                for existing_sec in sectors_all:
                    limits = ast.literal_eval(existing_sec.limits)
                    print(set(coordenadas_new), set(limits))
                    if set(coordenadas_new) == set(limits) and existing_sec.sector_name == sector_new:
                        id_sector = Sector.objects.get(
                            limits=existing_sec.limits,).id
                        data_local_sector = {
                            "local": ruc, "sector": id_sector, "price": price}
                        serializer_local_sector = LocalSectorSerializer(
                            data=data_local_sector)
                        serializer_local_sector.is_valid(raise_exception=True)
                        serializer_local_sector.save()
                        saveNombreMapa(ruc)
                        sector_exist = True
                if not sector_exist:
                    createSector(sector_new, coordenadas_new, ruc, price)
                    saveNombreMapa(ruc)
        return Response(status=status.HTTP_201_CREATED, data=request.data)

    def get(self, request, format=None):
        local_sector = LocalSector.objects.all()
        serializer = LocalSectorRetrieveSerializer(local_sector, many=True)
        L_sectores = serializer.data
        d_mapas = {}
        for d_sectores in L_sectores:
            l_limites = ast.literal_eval(
                d_sectores.get("sector").get("limits"))
            l_limites = [{"latitude": i[0], "longitude":i[1]}
                         for i in l_limites]
            local = d_sectores.get("local")
            nombre_mapa = local.get("nombre_mapa")
            ruc = local.get("ruc")
            sector = d_sectores["sector"]
            price = d_sectores["price"]
            d_mapas.setdefault(nombre_mapa, {})
            d_mapas[nombre_mapa].setdefault("ruc", ruc)
            d_mapas[nombre_mapa].setdefault("sectores", {})
            d_mapas[nombre_mapa]["sectores"][sector["sector_name"]] = {
                "limits": l_limites, "price": price, "id": sector["id"]}

        return Response(status=status.HTTP_200_OK, data=d_mapas)
    
@api_view(["GET"])
def getSectorByLocal(request, id):
    local_sector = LocalSector.objects.filter(local=id)
    serializer = LocalSectorRetrieveSerializer(local_sector, many=True)
    L_sectores = serializer.data
    d_mapas = {}
    for d_sectores in L_sectores:
        l_limites = ast.literal_eval(
            d_sectores.get("sector").get("limits"))
        l_limites = [{"latitude": i[0], "longitude":i[1]}
                        for i in l_limites]
        local = d_sectores.get("local")
        nombre_mapa = local.get("nombre_mapa")
        ruc = local.get("ruc")
        sector = d_sectores["sector"]
        price = d_sectores["price"]
        d_mapas.setdefault(nombre_mapa, {})
        d_mapas[nombre_mapa].setdefault("ruc", ruc)
        d_mapas[nombre_mapa].setdefault("sectores", {})
        d_mapas[nombre_mapa]["sectores"][sector["sector_name"]] = {
            "limits": l_limites, "price": price, "id": sector["id"]}

    return Response(status=status.HTTP_200_OK, data=d_mapas)  


@api_view(["DELETE"])
#body: {"local": ruc
#       "sector": id}
def deleteSector(request):
    localsector = LocalSector.objects.filter(local=request.data.get("local"), sector=request.data.get("sector"))
    print(localsector)
    if localsector:
        return Response(status=status.HTTP_200_OK, data={"message": "Sector eliminado"})
    else:
        return Response(status=status.HTTP_404_NOT_FOUND, data={"message": "Sector no encontrado, revise el id del local y/o sector"})

class ClientApiView(APIView):

    def get(self, request, format=None):
        client = Client.objects.all()
        serializer = ClientRetrieveSerializer(client, many=True)
        return Response(status=status.HTTP_200_OK, data = serializer.data)

    def post(self, request, format=None):
        serializer = ClienteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)
# Al momento de asignar, sacar el tiempo estimado
# Modificar el create order

# {
#     "id": 20,
#     "sector": {
#       "id": 24,
#       "sector_name": "sector_name1",
#       "limits": "[(-2.06764, -79.915628), (-2.073837, -79.925853)]"
#     },
#     "local": {
#       "ruc": "09814457754001",
#       "nombre_mapa": null
#     },
#     "price": 0
#   },


# locations_param = openapi.Parameter(
#     'origin', in_=openapi.IN_QUERY, description="Origin location", type=openapi.TYPE_STRING)
# @api_view(["GET"])
# @swagger_auto_schema(manual_parameters=[locations_param])
# def get_distance(request):
#     origin = request.GET.get("origin")
#     print(request.GET)
#     print(origin)
#     destination = request.GET.get("destination")
#     origin = origin.split(",")
#     destination = destination.split(",")
#     origin = (origin[0], origin[1])
#     destination = (destination[0], destination[1])
#     distance_matrix = json.dumps(getDistance(origin, destination))
#     return JsonResponse(distance_matrix, safe=False)
