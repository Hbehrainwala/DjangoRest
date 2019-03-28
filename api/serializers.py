from rest_framework import serializers

from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'customer', 'provider', 'courier')

class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name','password', 'customer', 'provider', 'courier')

    def validate(self, attrs):
        if not User.objects.filter(email=attrs.get('email')).exists():
            return attrs
        raise serializers.ValidationError({"email": "This email is taken already."})