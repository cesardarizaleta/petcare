from rest_framework import serializers
from apps.owners.models import Owner
from apps.patients.models import Patient
from apps.users.models import User
import datetime


class UserSerializer(serializers.ModelSerializer):
    """Serializer de solo lectura para los datos del usuario embebidos en el perfil del propietario."""

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')
        read_only_fields = fields


class OwnerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura para el perfil completo del propietario.
    Incluye los datos del User anidado.
    Usado en: GET /owners/me/  y  GET /owners/{id}/  y  GET /owners/
    """

    id = serializers.UUIDField(source='user_id', read_only=True)
    user = UserSerializer(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    address = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Owner
        fields = ('id', 'user', 'phone', 'address', 'created_at')
        read_only_fields = fields

    def get_created_at(self, obj):
        return datetime.datetime.now().isoformat()

    def get_phone(self, obj):
        if obj.natural_person:
            return obj.natural_person.phone
        return None

    def get_address(self, obj):
        if obj.natural_person:
            return obj.natural_person.address
        return None


class OwnerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualización parcial del perfil del propietario.
    Permite editar campos propios (phone, address) y campos del User (first_name, last_name).
    Usado en: PATCH /owners/me/
    """

    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    address = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'phone', 'address')

    def update(self, instance, validated_data):
        # Extraer datos de phone y address
        phone = validated_data.pop('phone', None)
        address = validated_data.pop('address', None)

        # Extraer datos anidados del User antes de actualizar Owner
        user_data = validated_data.pop('user', {})

        # Actualizar campos del Owner
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar campos del User si se enviaron
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Actualizar o crear NaturalPerson para guardar phone y address
        if phone is not None or address is not None:
            natural_person = instance.natural_person
            if not natural_person:
                from apps.users.models import NaturalPerson
                natural_person = NaturalPerson.objects.create(user=instance.user)
                instance.natural_person = natural_person
                instance.save()
            
            if phone is not None:
                natural_person.phone = phone
            if address is not None:
                natural_person.address = address
            natural_person.save()

        return instance


class PetSerializer(serializers.ModelSerializer):
    """
    Serializer para listar y crear mascotas (adaptado a Patient en la base de datos).
    Mapea campos como species/breed, sex, weight_kg a Patient.
    """
    owner_id = serializers.UUIDField(source='owner.user_id', read_only=True)
    species = serializers.CharField(required=True, write_only=True)
    breed = serializers.CharField(required=False, allow_blank=True, default='', write_only=True)
    date_of_birth = serializers.DateField(source='birth_date', required=True)
    sex = serializers.ChoiceField(choices=[('M', 'Macho'), ('F', 'Hembra')], required=True, write_only=True)
    weight_kg = serializers.FloatField(source='current_weight', required=True)
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Patient
        fields = (
            'id',
            'owner_id',
            'name',
            'species',
            'breed',
            'date_of_birth',
            'sex',
            'weight_kg',
            'created_at',
        )
        read_only_fields = ('id', 'owner_id', 'created_at')

    def get_created_at(self, obj):
        return datetime.datetime.now().isoformat()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Desglosar species_breed
        species_breed = instance.species_breed or ''
        parts = species_breed.split(" - ")
        ret['species'] = parts[0] if len(parts) > 0 else species_breed
        ret['breed'] = parts[1] if len(parts) > 1 else ''
        
        # Mapear gender a sex
        gender = instance.gender or ''
        if gender.upper() in ['M', 'MACHO']:
            ret['sex'] = 'M'
        elif gender.upper() in ['F', 'HEMBRA']:
            ret['sex'] = 'F'
        else:
            ret['sex'] = 'M'
            
        return ret

    def create(self, validated_data):
        species = validated_data.pop('species', '')
        breed = validated_data.pop('breed', '')
        species_breed = f"{species} - {breed}".strip() if breed else species
        
        sex = validated_data.pop('sex', 'M')
        gender = 'Macho' if sex == 'M' else 'Hembra'

        patient = Patient.objects.create(
            species_breed=species_breed,
            gender=gender,
            physical_marks='',
            microchip_id='',
            reproductive_status='Unknown',
            **validated_data
        )
        return patient
