from rest_framework.serializers import ModelSerializer
from backApp.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username","email","password","number_id","gender"]


