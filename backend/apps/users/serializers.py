from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Supply, AuditLog
import re

User = get_user_model()


class SupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Supply
        fields = ["id", "name", "current_stock"]
        read_only_fields = ["id"]

    def validate_current_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser un número negativo.")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("La contraseña debe incluir al menos un número.")
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("La contraseña debe incluir al menos un carácter especial.")
            
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Las credenciales proporcionadas son incorrectas.", code='authorization')
        else:
            raise serializers.ValidationError("Debe incluir el correo y la contraseña.", code='authorization')

        data['user'] = user
        return data


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True, default='Sistema')
    summary = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_name', 'action', 'path', 'timestamp', 'details', 'summary']
        read_only_fields = fields

    def get_summary(self, obj):
        usuario_str = obj.user.username if obj.user else 'Anónimo'
        return f"{obj.action} {obj.path} ({usuario_str})"
