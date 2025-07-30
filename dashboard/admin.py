from django.contrib import admin

# Register your models here.
from dashboard.models import Country, Region, Station, UserProfile, DashboardMetric, AuditLog

# Register your models here.
admin.site.register(Country)
admin.site.register(Region)
admin.site.register(Station)
admin.site.register(UserProfile)
admin.site.register(DashboardMetric)
admin.site.register(AuditLog)
