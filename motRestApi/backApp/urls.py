from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import MotorizadoSignUp, UserSignUp

urlpatterns = [
    path('user/register',UserSignUp.as_view()),
    path('motorizado/register',MotorizadoSignUp.as_view()),
    path('user/login',TokenObtainPairView.as_view()),
    path('user/refresh',TokenRefreshView.as_view()),

]
