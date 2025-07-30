from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from .models import Country, Region, Station, DashboardMetric, AuditLog, UserProfile
from django.contrib.auth.models import User as AuthUser
from .serializers import (
    CountrySerializer, RegionSerializer, StationSerializer,
    UserProfileSerializer, DashboardMetricSerializer, AuditLogSerializer
)
from .permissions import IsAdminOrReadOnly

# Imports for the custom user profile view
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


# --- Root View ---
def root_view(request):
    """
    Redirects the user to the dashboard if they are logged in,
    otherwise redirects them to the login page.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


# --- Helper function to get the user's allowed stations ---
def get_allowed_stations_for_user(django_user):
    if not django_user.is_authenticated:
        return Station.objects.none()
    if django_user.is_staff:
        return Station.objects.all()
    
    try:
        profile = django_user.profile
    except UserProfile.DoesNotExist:
        return Station.objects.none()

    if profile.role == 'Country Lead' and profile.country:
        return Station.objects.filter(country=profile.country)
    if profile.role == 'Station Manager' and profile.station:
        return Station.objects.filter(id=profile.station.id)
    if profile.role == 'Viewer':
        if profile.station:
            return Station.objects.filter(id=profile.station.id)
        if profile.country:
            return Station.objects.filter(country=profile.country)
            
    return Station.objects.none()

# --- API ViewSets ---
class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserProfile.objects.all().select_related('user')
        if self.request.user.is_authenticated:
            return UserProfile.objects.filter(user=self.request.user).select_related('user')
        return UserProfile.objects.none()

    def perform_destroy(self, instance):
        user_to_delete = instance.user
        instance.delete()
        user_to_delete.delete()

class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrReadOnly]
    def get_queryset(self):
        allowed_stations = get_allowed_stations_for_user(self.request.user)
        country_ids = allowed_stations.values_list('country_id', flat=True).distinct()
        return Country.objects.filter(id__in=country_ids)

class RegionViewSet(viewsets.ModelViewSet):
    serializer_class = RegionSerializer
    permission_classes = [IsAdminOrReadOnly]
    def get_queryset(self):
        allowed_stations = get_allowed_stations_for_user(self.request.user)
        region_ids = allowed_stations.values_list('region_id', flat=True).distinct()
        return Region.objects.filter(id__in=region_ids)

class StationViewSet(viewsets.ModelViewSet):
    serializer_class = StationSerializer
    permission_classes = [IsAdminOrReadOnly]
    def get_queryset(self):
        return get_allowed_stations_for_user(self.request.user)

class DashboardMetricViewSet(viewsets.ModelViewSet):
    serializer_class = DashboardMetricSerializer
    permission_classes = [IsAdminOrReadOnly]
    def get_queryset(self):
        station_id = self.request.query_params.get('station', None)
        allowed_stations = get_allowed_stations_for_user(self.request.user)

        if station_id:
            return DashboardMetric.objects.filter(station_id=station_id, station__in=allowed_stations)
        
        return DashboardMetric.objects.filter(station__in=allowed_stations)

class AuditLogViewSet(viewsets.ModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrReadOnly]
    def get_queryset(self):
        if self.request.user.is_staff:
            return AuditLog.objects.all().select_related('user')
        return AuditLog.objects.none()

# --- Custom API View for Current User ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_profile_view(request):
    """
    Returns the profile of the currently authenticated user.
    """
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found for the logged-in user.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Frontend Template Views ---
@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html', {
        'user_is_admin': request.user.is_staff,
        'username': request.user.username,
    })

def page_not_found_view(request, exception):
    return render(request, 'dashboard/404.html', status=404)
