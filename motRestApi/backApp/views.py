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
from backApp.models import ColorVehicle, Local, User,Motorizado, Vehicle, TypeVehicle,ModelsVehicle,Order,Client,Location, MotDeviceRegister, OrderComments
from backApp.serializers import *
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
import firebase_admin
from firebase_admin import credentials, firestore, messaging

class SuperUser(APIView):

    def post(self,request):
        superuser = SuperUserSerializer(data=request.data)
        if superuser.is_valid():
            superuser.save()
            return Response(superuser.data, status=status.HTTP_201_CREATED)
        return Response(superuser.errors, status=status.HTTP_400_BAD_REQUEST)

class UserSignUp(APIView):
    parser_classes= [MultiPartParser, FormParser]
    def post(self,request,format=None):
        profile_pic = dict((request.data).lists())["profile_pic"][0]
        #Create Location
        request = QueryDict.copy(request.POST)
        request.setdefault("profile_pic",profile_pic)
        location = LocationSerializer(data = request)
        location.is_valid(raise_exception=True)
        location.save()
        id_location = location.data.get("id")
        request.setdefault("home_loc",id_location)
        #Create user
        request.setdefault("is_active",True)
        user = UserSerializer(data=request)
        user.is_valid(raise_exception=True)
        user.save()
        #Create Phone
        ph_number = request.get("phone_number")
        phone = PhoneSerializer(data = {"pho_number":ph_number})
        phone.is_valid(raise_exception=True)
        phone.save()
        #Join Phone and USer
        print(user.data)
        phone_user_dict = {
            "idPhone":phone.data.get("id"),
            "user": user.data.get("id")
            }
        phone_user = PhoneUserSerializer(data = phone_user_dict)
        phone_user.is_valid(raise_exception=True)
        phone_user.save()
        return Response(status=status.HTTP_200_OK, data={"user":user.data, "phone":phone.data})

    def patch(self,request,id):
        user = User.objects.get(id = id)
        serializer = UserSerializer(user, data = request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data = serializer.data)

@api_view(['POST'])
def register_motdevice(request):
    motDeviceRegister = MotDeviceRegister.objects.filter(idDevice = request.data.get("idDevice"))
    if motDeviceRegister:
        return Response(status=status.HTTP_200_OK, data={"message":"Device already registered"})
    else:
        deviceRegister = MotDeviceRegisterSerializer(data = request.data)
        if deviceRegister.is_valid():
            deviceRegister.save()
            return Response(deviceRegister.data, status=status.HTTP_201_CREATED)
        return Response(deviceRegister.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRetrieveView(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRetrieveSerializer

class OperadorRetrieveView(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True,is_operador=True)
    serializer_class = UserRetrieveSerializer

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

    def get(self, request, format=None, id =None):
        if id:
            local = Local.objects.get(id = id)
            local_ser = LocalSerializer(local)
            local_ser.is_valid(raise_exception= True)
        else:
            locales = Local.objects.all()
            local_ser = LocalSerializer(locales, many=True)
        return Response(status = status.HTTP_200_OK, data = local_ser.data)


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


class MotorizadoUserView(viewsets.ReadOnlyModelViewSet):
    queryset = Motorizado.objects.all()
    serializer_class = MotUserSerializer


class MotToAssignView(viewsets.ReadOnlyModelViewSet):
    queryset = Motorizado.objects.filter(user_id__is_motorizado=0,
                                        user_id__is_operador=0,
                                        user_id__is_staff = 0).all()
    serializer_class = MotUserSerializer

@api_view(['PATCH'])
#@permission_classes([IsAuthenticated])
def upd_mot(request, id):
    motorizado = Motorizado.objects.get(user_id=id)
    serializer = MotSerializer(motorizado, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_200_OK,data=serializer.data)

    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_motorizados(request):
    # motorizados=Motorizado.objects.all()
    # qs = MotSerializer.setup_eager_loading(motorizados)
    # motorizados_serializer=MotSerializer(qs, many=True)
    qs = Motorizado.objects.all().select_related("user_id")
    motorizados_serializer=MotSerializer(qs)
    return Response(data = motorizados_serializer.data, status = status.HTTP_200_OK)

class OrderRetrieveView(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderAllSerializer

class OrderCommentsView(viewsets.ModelViewSet):
    queryset = OrderComments.objects.all()
    serializer_class = OrderCommentsSerializer


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

@api_view(["GET"])
def getvehiclesbymot(request):
    motorizado = request.GET.get("motorizado",None)
    if motorizado== None:
        raise NameError
    vehicles = Vehicle.objects.get(motorizado = motorizado)
    serializer = VehicleRetrieveSerializer(vehicles)
    return Response(data = serializer.data, status= status.HTTP_200_OK)


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
    orders=Order.objects.all()
    orders_serializer=OrderAllSerializer(orders, many=True)
    return JsonResponse(orders_serializer.data, safe=False)

@api_view(["POST"])
#permission_classes([LocalAuthenticated])
def post_order(request):
    req = dict.copy(request.data)
    req_client = req.get("client")
    client = Client.objects.get_or_create(id_number=req_client.get("id_number"),defaults=req_client)
    req_location = req.get("destiny_loc")
    destiny = Location.objects.get_or_create(latitude=req_location["latitude"],
                                            longitude=req_location["longitude"],
                                            reference=req_location["reference"],
                                            defaults=req_location)[0]
    #The following code is how the distance and duration should be gotten from google api

    local = Local.objects.get(ruc=req.get("local"))
    local_location = local.location_id
    # origin = local_location.longitude, local_location.latitude
    # destination = destiny.longitude, destiny.latitude
    # distance_matrix = getDistance(origin,destination)
    # distance = distance_matrix["rows"][0]["elements"][0]["distance"]["text"]
    # duration = distance_matrix["rows"][0]["elements"][0]["duration"]["text"]
    # print(distance,duration)

    req["client"] = client[0].id
    req["destiny_loc"] = destiny.id
    req["state"] = 1
    order = OrderSerializer(data = req)
    order.is_valid(raise_exception=True)
    order.save()
    # print(order.data)
    return Response(data=order.data, status=status.HTTP_201_CREATED)

def sendPushNotification(title,message,code,idOrder,tokens):
    dataObject={
            'idOrder': idOrder,
            'code':code
        }
    notifSend=messaging.Notification(title=title,body=message)
    sendMes =messaging.MulticastMessage(
        notification=notifSend,
        data={'title':'Objeto','body':json.dumps(dataObject, separators=(',',':'))},
        tokens=tokens,
        )

    respues=messaging.send_multicast(sendMes)
    print ("repsuesta",respues)

@api_view(["PATCH"])
def assign_order(request, id):
    order = Order.objects.get(id = id)
    req = request.data.copy()
    req["mot_assigned_time"] = datetime.now()
    motorizado = Motorizado.objects.get(user_id = req["motorizado"])
    mot_serializer = MotSerializer(motorizado, data={"is_busy":True}, partial=True)
    mot_serializer.is_valid(raise_exception=True)
    mot_serializer.save()
    req["state"] = 2
    serializer = OrderSerializer(order, data = req,partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    devices = MotDeviceRegister.objects.filter(idMot = req["motorizado"])
    lista_regis = []
    for device in devices:
        lista_regis.append(device.idDevice)
    #lista_regis=['fr5MWLf3TrW1Q0XR2Oij8R:APA91bGkGZsB3JEaaxS_xmJ1uOQi8hvVt2Mltparpym2PvO2tXZeaeIqt7JAVT3ImC9__Capcck9pRxfTRDOJdXnlYhAzhF_iXqFiJdB7e37rYympmlQXZR8AaeHQiRTkxI56f1t_00e','egqWrJv4Tg-qLWfxVTs-97:APA91bF14OiLvQzvLwZdyoZ5ccgKYvjNNaIKgKHlMxp6tyMwoThRuRV911lnQgqcDkD9VGDKKUbpWiiMMDgLRcI6FRXmCVMqE3cZGnLDNdZsPffPPp0K5BrGHXTWAC_6IsMXAKdypAhE']
    # dataSended = {
    #     'message': 'Se ha asignado una nueva orden',
    #     'code': 1
    # }
    # notif=messaging.Notification(title='Nueva orden',body=json.dumps(dataSended, separators=(',',':')))
    # prueba =messaging.MulticastMessage(
    #     notification=notif,
    #     data={
    #         'title': 'Nueva orden',
    #         'body': json.dumps(dataSended, separators=(',',':')),
    #     },
    #     tokens=lista_regis,
    # )
    # respues=messaging.send_multicast(prueba)
    # print ("repsuesta",respues)

    # print(serializer.data)
    sendPushNotification('Nueva orden','Se le ha asignado una nueva orden',1,id,lista_regis)
    return Response(status=status.HTTP_200_OK, data = serializer.data)

@api_view(["GET"])
def get_distance(request):
    origin = request.GET.get("origin")
    print(request.GET)
    print(origin)
    destination = request.GET.get("destination")
    origin = origin.split(",")
    destination = destination.split(",")
    origin = (origin[0],origin[1])
    destination = (destination[0],destination[1])
    distance_matrix = json.dumps(getDistance(origin,destination))
    return JsonResponse(distance_matrix, safe=False)

def getDistance(origin,destination):
    google_key = settings.GOOGLE_API_KEY
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={},{}&destinations={},{}&key={}".format(origin[0],origin[1],destination[0],destination[1],google_key)
    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)

    return response.json()

#Empresa necesita conocer el motorizado de un pedido
#@permission_classes([LocalAuthenticated])
@api_view(["GET"])
def get_motorizado_order(request):
    order_id = request.query_params["id"]
    order_obj = Order.objects.get(id=order_id)
    motorizado_id = order_obj.motorizado
    motorizado_obj = Motorizado.objects.get(user_id = motorizado_id)

    motorizado = MotUserSerializer(motorizado_obj)
    return Response(data=motorizado.data)

@api_view(["PATCH"])
def change_data_order(request, id):
    order = Order.objects.get(id = id)

    serializer = OrderSerializer(order, data = request.data,partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status=status.HTTP_200_OK, data = serializer.data)


@api_view(["PATCH"])
def revoke_order(request,id):
    order = Order.objects.get(id = id)
    motorizado = order.motorizado
    data = {"motorizado":None,
            "state":1,}
    serializer = OrderSerializer(order,data = data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    dataSended = {
        'message': 'Se ha revocado su orden',
        'code': 2
    }
    #lista_regis=['fr5MWLf3TrW1Q0XR2Oij8R:APA91bGkGZsB3JEaaxS_xmJ1uOQi8hvVt2Mltparpym2PvO2tXZeaeIqt7JAVT3ImC9__Capcck9pRxfTRDOJdXnlYhAzhF_iXqFiJdB7e37rYympmlQXZR8AaeHQiRTkxI56f1t_00e','egqWrJv4Tg-qLWfxVTs-97:APA91bF14OiLvQzvLwZdyoZ5ccgKYvjNNaIKgKHlMxp6tyMwoThRuRV911lnQgqcDkD9VGDKKUbpWiiMMDgLRcI6FRXmCVMqE3cZGnLDNdZsPffPPp0K5BrGHXTWAC_6IsMXAKdypAhE']
    devices = MotDeviceRegister.objects.filter(idMot = motorizado)
    lista_regis = []
    for device in devices:
        lista_regis.append(device.idDevice)
    sendPushNotification('Orden revocada','Se le ha revocado una orden',2,id,lista_regis)
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
    return Response(status = status.HTTP_200_OK, data = serializer.data)


@api_view(["GET"])
def user_exists(request):
    email = request.query_params.get("email")
    try:
        user = User.objects.get(email = email)
    except:
        return Response(status = status.HTTP_200_OK, data={"exists":False})
    return Response(status = status.HTTP_200_OK, data={"exists":True})


@api_view(["GET"])
def get_order_state(request):
    id  = request.query_params.get("id")
    equivalencia = Order.state_eq
    order = Order.objects.get(id=id)
    state_id = order.state
    state_descrip = equivalencia.get(state_id)
    return Response(status = status.HTTP_200_OK, data = {"state":state_descrip})

@api_view(["GET"])
def get_mot_orders(request,id):
    motorizado = Motorizado.objects.get(user_id = id)
    orders = Order.objects.filter(motorizado = motorizado)
    if len(orders):
        serializer = OrderAllSerializer(orders, many=True)
        return Response(status = status.HTTP_200_OK, data = serializer.data)
    return Response(status = status.HTTP_204_NO_CONTENT, data = [])

@api_view(["GET"])
def get_mot_orders_active(request,id):
    motorizado = Motorizado.objects.get(user_id = id)
    orders = Order.objects.filter(motorizado = motorizado).filter(state__in=[3,4,5])
    if len(orders):
        serializer = OrderAllSerializer(orders, many=True)
        return Response(status = status.HTTP_200_OK, data = serializer.data)
    return Response(status = status.HTTP_204_NO_CONTENT, data = [])

@api_view(["GET"])
def get_mot_orders_assigned(request,id):
    motorizado = Motorizado.objects.get(user_id = id)
    orders = Order.objects.filter(motorizado = motorizado).filter(state__in=[2,3,4,5]) #Retornar 2,3,4,5
    if len(orders):
        serializer = OrderAllSerializer(orders, many=True)
        return Response(status = status.HTTP_200_OK, data = serializer.data)
    return Response(status = status.HTTP_204_NO_CONTENT, data = [])

@api_view(["GET"])
def get_mot_orders_finished(request,id):
    motorizado = Motorizado.objects.get(user_id = id)
    orders = Order.objects.filter(motorizado = motorizado).filter(state=6)
    if len(orders):
        serializer = OrderAllSerializer(orders, many=True)
        return Response(status = status.HTTP_200_OK, data = serializer.data)
    return Response(status = status.HTTP_204_NO_CONTENT, data = [])

@api_view(["PATCH"])
def accept_order(request,id):
    order = Order.objects.get(id = id)
    data = {"state":3}
    serializer = OrderSerializer(order, data = data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status = status.HTTP_200_OK, data = serializer.data)

@api_view(["PATCH"])
def reject_order(request,id):
    order = Order.objects.get(id = id)
    motorizado = order.motorizado
    data = {"state":1,
            "mot_assigned_time":None,
            "motorizado":None,}
    serializer = OrderSerializer(order, data = data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return_data = dict(serializer.data).update({"rejected_by":motorizado})
    return Response(status = status.HTTP_200_OK, data = return_data)

@api_view(["GET"])
def count_by_mot(request,id):
    motorizado = Motorizado.objects.get(user_id = id)
    orders = Order.objects.filter(motorizado = motorizado).filter(state=6)
    return Response(status = status.HTTP_200_OK, data = {"count":len(orders)})

@api_view(["GET"])
def orders_by_dates(request):
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")
    motorizado = request.query_params.get("motorizado")
    if start_date or end_date:
        if(start_date and end_date):
            orders = Order.objects.filter(motorizado = motorizado).filter(start_time__range=[start_date,end_date])
        elif (start_date):
            orders_all = Order.objects.filter(motorizado = motorizado)
            orders = []
            for order in orders_all:
                if str(datetime.date(order.start_time)) == start_date:
                    orders.append(order.id)
            orders = Order.objects.filter(id__in=orders)
        serializer = OrderAllSerializer(orders, many=True)
        return Response(status = status.HTTP_200_OK, data = serializer.data)
    return Response(status = status.HTTP_400_BAD_REQUEST, data = [])

@api_view(["GET"])
def get_mot_location(request,id):
    order = Order.objects.get(id = id)
    if order.state == 1:
        return Response(status = status.HTTP_204_NO_CONTENT, data = {"description":"La orden está en espera de ser asignada"})
    if order.state in (2,3):
        return Response(status = status.HTTP_204_NO_CONTENT, data = {"description":"La orden aún no está siendo recogida"})
    if order.state in (4,5):
        motorizado = order.motorizado
        mot_ser = MotSerializer(motorizado)
        db = firestore.client()
        location = db.collection("motorizados").document(str(mot_ser.data.get("user_id"))).get()
        if location.exists:
            location = location.to_dict()
            return Response(status = status.HTTP_200_OK, data = location)
        else:
            return Response(status = status.HTTP_400_BAD_REQUEST, data = [])
    if order.state == 6:
        return Response(status = status.HTTP_204_NO_CONTENT, data = {"description":"La orden ya ha terminado"})

class LocalKmViewSet(viewsets.ModelViewSet):
    queryset = LocalKM.objects.all()
    serializer_class = LocalKmSerializer

