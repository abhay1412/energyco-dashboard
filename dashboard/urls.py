from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet,
    CountryViewSet,
    RegionViewSet,
    StationViewSet,
    DashboardMetricViewSet,
    AuditLogViewSet,
    current_user_profile_view  # Import the new view
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', UserProfileViewSet, basename='userprofile')
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'regions', RegionViewSet, basename='region')
router.register(r'stations', StationViewSet, basename='station')
router.register(r'metrics', DashboardMetricViewSet, basename='dashboardmetric')
router.register(r'auditlog', AuditLogViewSet, basename='auditlog')

# The API URLs are now determined automatically by the router.
# We add the custom URL for the current user profile manually.
urlpatterns = [
    # This line creates the /api/users/me/ endpoint
    path('users/me/', current_user_profile_view, name='current-user-profile'),
    
    # This includes all the URLs from the router (e.g., /api/users/, /api/stations/, etc.)
    path('', include(router.urls)),
]
