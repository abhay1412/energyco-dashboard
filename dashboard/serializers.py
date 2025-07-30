from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.models import User as AuthUser
from .models import Country, Region, Station, UserProfile, DashboardMetric, AuditLog

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    # These fields are for writing data from the frontend (create/update).
    # They are marked as write_only, so they won't appear in the API output.
    email = serializers.EmailField(write_only=True)
    name = serializers.CharField(write_only=True)
    active = serializers.BooleanField(write_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        # The fields list now only contains the necessary model fields and write-only fields.
        # The display fields will be added manually in `to_representation`.
        fields = [
            'user', 'role', 'country', 'station', # Profile fields
            'email', 'name', 'active', 'password', # Writeable fields
        ]
        read_only_fields = ['user']

    def to_representation(self, instance):
        """
        Customize the API output to match what the frontend table expects.
        This method is called when serializing the data to be sent to the frontend.
        """
        # Start with the default representation of the UserProfile (role, country, etc.)
        representation = super().to_representation(instance)
        
        # Add fields from the related User model with the correct names.
        representation['id'] = instance.user.id
        representation['name'] = instance.user.get_full_name()
        representation['email'] = instance.user.email
        representation['status'] = instance.user.is_active
        
        return representation

    def create(self, validated_data):
        # Pop the data for the User model from the validated data
        email = validated_data.pop('email')
        name = validated_data.pop('name')
        is_active = validated_data.pop('active')
        password = validated_data.pop('password', None)
        
        # The rest of validated_data is for the UserProfile model
        profile_data = validated_data

        first_name, last_name = (name.split(' ', 1) + [''])[:2]

        if not password:
            raise serializers.ValidationError({'password': 'Password is required.'})
        if AuthUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists.'})

        try:
            with transaction.atomic():
                auth_user = AuthUser.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=is_active
                )
                
                if profile_data.get('role') == 'Admin':
                    auth_user.is_staff = True
                    auth_user.is_superuser = True
                    auth_user.save()

                profile = UserProfile.objects.create(user=auth_user, **profile_data)
                return profile
        except Exception as e:
            raise serializers.ValidationError({'error': f'An unexpected error occurred: {str(e)}'})

    def update(self, instance, validated_data):
        auth_user = instance.user
        
        name = validated_data.get('name', None)
        if name:
            auth_user.first_name, auth_user.last_name = (name.split(' ', 1) + [''])[:2]

        # Use .get() for optional fields
        email = validated_data.get('email', auth_user.email)
        if email and AuthUser.objects.filter(email=email).exclude(pk=auth_user.pk).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists.'})
        auth_user.email = email
        auth_user.username = auth_user.email # Keep username in sync

        # Use 'is not None' to allow setting status to False
        is_active = validated_data.get('active', None)
        if is_active is not None:
            auth_user.is_active = is_active
        
        password = validated_data.get('password', None)
        if password:
            auth_user.set_password(password)
        
        instance.role = validated_data.get('role', instance.role)
        instance.country = validated_data.get('country', instance.country)
        instance.station = validated_data.get('station', instance.station)
        
        if instance.role == 'Admin':
            auth_user.is_staff = True
            auth_user.is_superuser = True
        else:
            auth_user.is_staff = False
            auth_user.is_superuser = False
            
        auth_user.save()
        instance.save()
        
        return instance


class DashboardMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardMetric
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'timestamp', 'user', 'user_email', 'action', 'target', 'details']
        read_only_fields = ['user_email']
