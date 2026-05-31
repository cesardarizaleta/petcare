from django.contrib.auth import authenticate, login as django_login
from django.db.models import F
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Supply, AuditLog
from apps.users.serializers import SupplySerializer, AuditLogSerializer
from apps.users.permissions import (
    DjangoModelPermissions,
    IsReceptionist,
    IsOwner
)


from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import NaturalPerson
from apps.owners.models import Owner

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    POST /api/v1/auth/register/
    Registrar a un nuevo propietario de mascota en el sistema.
    """
    data = request.data
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    if not email or not password:
        return Response({'error': 'Email y contraseña son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)

    dni = data.get('dni')
    if dni:
        import re
        if not re.match(r'^\d{6,10}$', str(dni)):
            return Response({'error': 'La cédula/DNI debe contener entre 6 y 10 dígitos positivos.'}, status=status.HTTP_400_BAD_REQUEST)
        
    if User.objects.filter(email=email).exists():
        return Response({'email': ['Este correo electrónico ya está registrado.']}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        # Crear User
        user = User.objects.create(
            email=email,
            username=email.split('@')[0],
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        user.set_password(password)
        user.save()
        
        # Asignar grupo Owner
        owner_group, _ = Group.objects.get_or_create(name='owner')
        user.groups.add(owner_group)
        
        # Crear Persona Natural
        np = NaturalPerson.objects.create(
            user=user,
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            dni=data.get('dni', '')
        )
        
        # Crear Propietario
        Owner.objects.create(
            user=user,
            natural_person=np,
            location=data.get('location', 'Sede Palermo'),
            emergency_contact=data.get('emergency_contact', '')
        )
        
        return Response({
            "message": "Usuario registrado exitosamente como Owner.",
            "email": email
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    POST /api/v1/auth/login/
    Autenticar a cualquier usuario y devolver tokens JWT.
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'error': 'Email y contraseña son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        user = User.objects.get(email=email)
        if not user.check_password(password):
            return Response({'detail': 'Credenciales incorrectas.'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if not user.is_active:
            return Response({'detail': 'Usuario inactivo.'}, status=status.HTTP_403_FORBIDDEN)
            
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "groups": list(user.groups.values_list('name', flat=True))
            }
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'detail': 'Credenciales incorrectas.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh(request):
    """
    POST /api/v1/auth/refresh/
    Renovar el token de acceso usando SimpleJWT.
    """
    from rest_framework_simplejwt.serializers import TokenRefreshSerializer
    serializer = TokenRefreshSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    except Exception:
        return Response({'detail': 'Token de refresco inválido o expirado.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_veterinarian(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        is_veterinarian = user.groups.filter(name='veterinarian').exists()
        if is_veterinarian:
            django_login(request, user)
            return Response(
                {"mensaje": "Bienvenido doctor, autorización exitosa"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Acceso denegado. Esta ruta es exclusiva para personal veterinario"},
                status=status.HTTP_403_FORBIDDEN
            )
    else:
        return Response(
            {"error": "Usuario o la contraseña son incorrectos"},
            status=status.HTTP_401_UNAUTHORIZED
        )


class SupplyViewSet(viewsets.ModelViewSet):
    queryset = Supply.objects.all()
    serializer_class = SupplySerializer
    permission_classes = [DjangoModelPermissions]
    
    @action(detail=True, methods=['post'])
    def deduct(self, request, pk=None):
        self.get_object()
        try:
            quantity_str = request.data.get('quantity', 0)
            quantity = int(quantity_str)
            if quantity <= 0:
                return Response({'error': 'La cantidad debe ser mayor a cero'}, status=status.HTTP_400_BAD_REQUEST)
                
            Supply.objects.filter(pk=pk).update(current_stock=F('current_stock') - quantity)
            return Response({'status': 'Stock actualizado con éxito'}, status=status.HTTP_200_OK)
        except (ValueError, TypeError):
            return Response({'error': 'Cantidad no válida'}, status=status.HTTP_400_BAD_REQUEST)


class ReceptionistTestView(APIView):
    permission_classes = [IsAuthenticated, IsReceptionist]
    
    def get(self, request):
        return Response({"mensaje": "Acceso concedido: Eres recepcionista.", "usuario": request.user.username})


class ManagerDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get(self, request):
        sensitive_data = {
            "mensaje": "Bienvenido gerente. Tienes acceso a esta informacion confidencial.",
            "usuario_actual": request.user.email,
            "rol": getattr(request.user, 'role', 'sin_rol')
        }
        return Response(sensitive_data, status=status.HTTP_200_OK)
    
    
class VerifyUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "rol": getattr(user, 'role', 'sin_rol')
        })


class LogDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        logs = AuditLog.objects.all().order_by('-timestamp')[:50]
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)
