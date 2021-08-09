from rest_framework.serializers import ModelSerializer
from backApp.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username","email","password","number_id","gender"]

    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


