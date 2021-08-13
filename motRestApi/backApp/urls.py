from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import MotorizadoView, UserSignUp

urlpatterns = [
    path('user/register',UserSignUp.as_view()),
    path('motorizado',MotorizadoView.as_view()),
    path('user/login',TokenObtainPairView.as_view()),
    path('user/refresh',TokenRefreshView.as_view()),
]
