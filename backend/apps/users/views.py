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
    IsOwner,
    IsManager
)


from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import NaturalPerson, ClinicalStaff, Veterinarian
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
        
    phone = data.get('phone')
    if phone:
        import re
        if not re.match(r'^\+?[\d\s\-()]{7,20}$', str(phone)):
            return Response({'error': 'El teléfono debe tener un formato válido (entre 7 y 20 caracteres, permitiendo números, espacios, guiones y paréntesis).'}, status=status.HTTP_400_BAD_REQUEST)

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
            
        groups = list(user.groups.values_list('name', flat=True))
        if user.is_superuser:
            groups.append('superadmin')
            
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "groups": groups
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
    permission_classes = [IsAuthenticated, IsManager]
    
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
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        logs = AuditLog.objects.all().order_by('-timestamp')[:50]
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)


from rest_framework.permissions import BasePermission

class IsSuperAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class SuperAdminUserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsSuperAdminUser]

    def list(self, request):
        users_data = []
        for u in User.objects.all().order_by('email'):
            groups = list(u.groups.values_list('name', flat=True))
            if u.is_superuser and 'superadmin' not in groups:
                groups.append('superadmin')
            
            dni = ""
            phone = ""
            address = ""
            if hasattr(u, 'natural_person'):
                try:
                    np = u.natural_person
                    if np:
                        dni = np.dni or ""
                        phone = np.phone or ""
                        address = np.address or ""
                except Exception:
                    pass

            specialty = ""
            if hasattr(u, 'clinical_staff'):
                try:
                    cs = u.clinical_staff
                    if cs and hasattr(cs, 'veterinarian'):
                        specialty = cs.veterinarian.specialty or ""
                except Exception:
                    pass

            users_data.append({
                "id": str(u.id),
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "is_active": u.is_active,
                "roles": groups,
                "dni": dni,
                "phone": phone,
                "address": address,
                "specialty": specialty
            })
        return Response(users_data)

    def create(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        roles = data.get('roles', [])

        dni = data.get('dni', '').strip() if data.get('dni') else ''
        phone = data.get('phone', '').strip() if data.get('phone') else ''
        address = data.get('address', '').strip() if data.get('address') else ''
        specialty = data.get('specialty', '').strip() if data.get('specialty') else ''

        if not email or not password:
            return Response({'error': 'Email y contraseña son obligatorios.'}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Este correo electrónico ya está registrado.'}, status=400)

        if dni:
            import re
            if not re.match(r'^\d{6,10}$', str(dni)):
                return Response({'error': 'La cédula/DNI debe contener entre 6 y 10 dígitos positivos.'}, status=400)
        
        if phone:
            import re
            if not re.match(r'^\+?[\d\s\-()]{7,20}$', str(phone)):
                return Response({'error': 'El teléfono debe tener un formato válido (entre 7 y 20 caracteres, permitiendo números, espacios, guiones y paréntesis).'}, status=400)

        try:
            user = User.objects.create(
                email=email,
                username=email.split('@')[0],
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            user.set_password(password)
            user.save()

            for role_name in roles:
                if role_name == 'superadmin':
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                else:
                    group, _ = Group.objects.get_or_create(name=role_name)
                    user.groups.add(group)

            # Sync Profiles
            natural_person, _ = NaturalPerson.objects.get_or_create(user=user)
            natural_person.dni = dni
            natural_person.phone = phone
            natural_person.address = address
            natural_person.save()

            group_names = set(roles)
            if 'owner' in group_names:
                Owner.objects.get_or_create(
                    user=user,
                    defaults={
                        'natural_person': natural_person,
                        'location': 'Sede Palermo'
                    }
                )
            else:
                Owner.objects.filter(user=user).delete()

            staff_roles = {'veterinarian', 'receptionist', 'manager', 'technician', 'veterinary_technician', 'superadmin'}
            is_staff_role = bool(group_names & staff_roles) or user.is_staff or user.is_superuser
            
            if is_staff_role:
                clinical_staff, _ = ClinicalStaff.objects.get_or_create(
                    user=user,
                    defaults={'natural_person': natural_person}
                )
                if not clinical_staff.natural_person:
                    clinical_staff.natural_person = natural_person
                    clinical_staff.save()

                if 'veterinarian' in group_names:
                    vet, _ = Veterinarian.objects.get_or_create(
                        clinical_staff=clinical_staff,
                        defaults={'specialty': specialty or 'General'}
                    )
                    if specialty:
                        vet.specialty = specialty
                        vet.save()
                else:
                    Veterinarian.objects.filter(clinical_staff=clinical_staff).delete()
            else:
                clinical_staff = ClinicalStaff.objects.filter(user=user).first()
                if clinical_staff:
                    Veterinarian.objects.filter(clinical_staff=clinical_staff).delete()
                    clinical_staff.delete()

            return Response({
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "roles": roles,
                "message": "Usuario creado exitosamente por el Superadmin."
            }, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def update(self, request, pk=None):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)

        data = request.data
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.is_active = data.get('is_active', user.is_active)
        
        password = data.get('password')
        if password:
            user.set_password(password)
        
        user.save()

        dni = data.get('dni')
        phone = data.get('phone')
        address = data.get('address')
        specialty = data.get('specialty')

        if dni:
            import re
            if not re.match(r'^\d{6,10}$', str(dni)):
                return Response({'error': 'La cédula/DNI debe contener entre 6 y 10 dígitos positivos.'}, status=400)
        
        if phone:
            import re
            if not re.match(r'^\+?[\d\s\-()]{7,20}$', str(phone)):
                return Response({'error': 'El teléfono debe tener un formato válido (entre 7 y 20 caracteres, permitiendo números, espacios, guiones y paréntesis).'}, status=400)

        roles = data.get('roles')
        if roles is not None:
            user.groups.clear()
            user.is_superuser = False
            user.is_staff = False
            
            for role_name in roles:
                if role_name == 'superadmin':
                    user.is_superuser = True
                    user.is_staff = True
                else:
                    group, _ = Group.objects.get_or_create(name=role_name)
                    user.groups.add(group)
            user.save()

        # Sync profiles
        natural_person, _ = NaturalPerson.objects.get_or_create(user=user)
        if dni is not None:
            natural_person.dni = dni.strip()
        if phone is not None:
            natural_person.phone = phone.strip()
        if address is not None:
            natural_person.address = address.strip()
        natural_person.save()

        group_names = set(user.groups.values_list('name', flat=True))
        if user.is_superuser:
            group_names.add('superadmin')

        if 'owner' in group_names:
            Owner.objects.get_or_create(
                user=user,
                defaults={
                    'natural_person': natural_person,
                    'location': 'Sede Palermo'
                }
            )
        else:
            Owner.objects.filter(user=user).delete()

        staff_roles = {'veterinarian', 'receptionist', 'manager', 'technician', 'veterinary_technician', 'superadmin'}
        is_staff_role = bool(group_names & staff_roles) or user.is_staff or user.is_superuser
        
        if is_staff_role:
            clinical_staff, _ = ClinicalStaff.objects.get_or_create(
                user=user,
                defaults={'natural_person': natural_person}
            )
            if not clinical_staff.natural_person:
                clinical_staff.natural_person = natural_person
                clinical_staff.save()

            if 'veterinarian' in group_names:
                vet, _ = Veterinarian.objects.get_or_create(
                    clinical_staff=clinical_staff,
                    defaults={'specialty': specialty or 'General'}
                )
                if specialty is not None:
                    vet.specialty = specialty.strip() if specialty else 'General'
                    vet.save()
            else:
                Veterinarian.objects.filter(clinical_staff=clinical_staff).delete()
        else:
            clinical_staff = ClinicalStaff.objects.filter(user=user).first()
            if clinical_staff:
                Veterinarian.objects.filter(clinical_staff=clinical_staff).delete()
                clinical_staff.delete()

        groups = list(user.groups.values_list('name', flat=True))
        if user.is_superuser:
            groups.append('superadmin')

        return Response({
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "roles": groups,
            "message": "Usuario actualizado exitosamente."
        })

    def destroy(self, request, pk=None):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)

        user.is_active = False
        user.save()
        return Response({"message": "Usuario desactivado exitosamente."})
