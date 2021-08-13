from rest_framework.serializers import ModelSerializer
from backApp.models import Order

class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order

        fields = [""]