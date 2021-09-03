from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LocalLoginView, LocalRegistrationView, MotToAssignView, MotorizadoUserView, MotorizadoView, UserSignUp,OrderRetrieveView

from .views import UserSignUp, get_models
from backApp import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("mot_user",MotorizadoUserView)
router.register("orders",OrderRetrieveView)
router.register("mot_to_assign",MotToAssignView)


urlpatterns = [
    path('user/register',UserSignUp.as_view()),
    path('user/<int:id>',UserSignUp.as_view()),
    path('motorizado',MotorizadoView.as_view()),
    path('motorizado/<int:id>',views.upd_mot),
    path('user/login',TokenObtainPairView.as_view()),
    path('user/refresh',TokenRefreshView.as_view()),
    path('vehicle',views.getvehiclesbymot),
    path('vehicle/colors', views.get_colors),
    path('vehicle/type', views.get_type),
    path('vehicle/models', views.get_models),
    #path('motorizado/all', views.get_motorizados),
    path('motorizado/update', views.update_motorizado),
    path('local',LocalRegistrationView.as_view()),
    path('local/login',LocalLoginView.as_view()),
    #path('order/all', views.get_orders),
    path('',include(router.urls)),
    path('order/create/',views.post_order),
    path('order/assign/<int:id>',views.assign_order)
]
