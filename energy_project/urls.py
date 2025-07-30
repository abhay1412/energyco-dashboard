from django.contrib import admin
from django.urls import path, include
from dashboard import views as dashboard_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # This is the crucial line. It tells Django that any URL starting
    # with 'api/' should be handled by the urls.py file inside your
    # 'dashboard' app. This is how it finds '/api/users/me/'.
    path('api/', include('dashboard.urls')),

    # Authentication URLs provided by Django (for login, logout, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Frontend Page URLs
    path('dashboard/', dashboard_views.dashboard_view, name='dashboard'),

    # Root URL redirect
    # This should be the last pattern
    path('', dashboard_views.root_view, name='root'),
]
