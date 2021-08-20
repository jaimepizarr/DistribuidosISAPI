from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LocalLoginView, LocalRegistrationView, MotorizadoView, UserSignUp

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
    path('vehicle/models', views.get_models),
    path('motorizado/all', views.get_motorizados),
    path('motorizado/update', views.update_motorizado),
    path('local',LocalRegistrationView.as_view()),
    path('local/login',LocalLoginView.as_view()),
    path('order/all', views.get_orders),
]
