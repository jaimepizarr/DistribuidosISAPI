from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import MotorizadoView, UserSignUp

from .views import UserSignUp, get_models
from backApp import views
urlpatterns = [
    path('user/register',UserSignUp.as_view()),
    path('motorizado',MotorizadoView.as_view()),
    path('motorizado/<int:id>',views.upd_mot),
    path('user/login',TokenObtainPairView.as_view()),
    path('user/refresh',TokenRefreshView.as_view()),
    path('vehicle/colors', views.get_colors),
    path('vehicle/type', views.get_type),
    path('vehicle/models', views.get_models)
]