from django.db import models
from django.contrib.auth.models import User as AuthUser

# It's best practice to use Django's built-in User model for authentication
# and extend it with a profile model for additional fields.

class Country(models.Model):
    """Represents a country."""
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Region(models.Model):
    """Represents a region within a country."""
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='regions')

    def __str__(self):
        return self.name

class Station(models.Model):
    """Represents an energy station."""
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='stations')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='stations')

    def __str__(self):
        return self.name

# FIX: Renamed User to UserProfile and linked it to Django's built-in User model.
# This is the standard and most robust way to handle user profiles.
class UserProfile(models.Model):
    """Extends Django's built-in User model with role and hierarchy information."""
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Country Lead', 'Country Lead'),
        ('Station Manager', 'Station Manager'),
        ('Viewer', 'Viewer'),
    ]
    
    # This is the key change: linking the profile to the authentication user.
    # The AuthUser handles username, email, password, first_name, last_name.
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, related_name='profile', primary_key=True)
    
    # Profile-specific fields
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, blank=True)
    
    # The 'active' status is already on the AuthUser model (is_active).
    # We can access it via self.user.is_active.

    def __str__(self):
        return self.user.email

class DashboardMetric(models.Model):
    """Stores time-series metrics for each station."""
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='metrics')
    timestamp = models.DateTimeField()
    output = models.FloatField()
    temperature = models.FloatField()
    voltage = models.FloatField()
    efficiency = models.FloatField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Metrics for {self.station.name} at {self.timestamp}"

class AuditLog(models.Model):
    """Logs significant actions performed by users."""
    # FIX: Changed ForeignKey to point to the built-in AuthUser for clarity.
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=255)
    details = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.email} - {self.action}"
