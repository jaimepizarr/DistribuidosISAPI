from django.conf.urls import url
from django.views.generic.base import TemplateView
from frontend.views import *

urlpatterns = [
url(r'^.*', TemplateView.as_view(template_name="frontend/home.html"), name="home")]