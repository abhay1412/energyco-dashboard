import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from dashboard.models import UserProfile, Country, Region, Station, DashboardMetric, AuditLog
from django.utils.dateparse import parse_datetime

class Command(BaseCommand):
    help = 'Loads data from JSON files into the database'

    def handle(self, *args, **kwargs):
        # Define the path to the JSON files
        # FIX: Point to the 'data' directory which is a sibling of the project folder
        data_path = os.path.join(settings.BASE_DIR.parent, 'data')

        # Clear existing data to prevent duplicates, in reverse order of dependency
        self.stdout.write('Clearing old data...')
        AuditLog.objects.all().delete()
        DashboardMetric.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()
        Station.objects.all().delete()
        Region.objects.all().delete()
        Country.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Old data cleared.'))

        # --- Load Countries ---
        self.stdout.write('Loading countries...')
        with open(os.path.join(data_path, 'countries.json')) as f:
            countries_data = json.load(f)
            for country_data in countries_data:
                Country.objects.create(**country_data)
        self.stdout.write(self.style.SUCCESS(f'{len(countries_data)} countries loaded.'))

        # --- Load Regions ---
        self.stdout.write('Loading regions...')
        with open(os.path.join(data_path, 'regions.json')) as f:
            regions_data = json.load(f)
            for region_data in regions_data:
                Region.objects.create(**region_data)
        self.stdout.write(self.style.SUCCESS(f'{len(regions_data)} regions loaded.'))

        # --- Load Stations ---
        self.stdout.write('Loading stations...')
        with open(os.path.join(data_path, 'stations.json')) as f:
            stations_data = json.load(f)
            for station_data in stations_data:
                Station.objects.create(**station_data)
        self.stdout.write(self.style.SUCCESS(f'{len(stations_data)} stations loaded.'))

        # --- Load Users and UserProfiles ---
        self.stdout.write('Loading users and profiles...')
        with open(os.path.join(data_path, 'users.json')) as f:
            users_data = json.load(f)
            for user_data in users_data:
                # Create the auth user
                auth_user = User.objects.create_user(
                    id=user_data['id'],
                    username=user_data['email'],
                    email=user_data['email'],
                    password='password123' # Set a default password
                )
                auth_user.is_active = user_data['active']
                if user_data['role'] == 'Admin':
                    auth_user.is_staff = True
                    auth_user.is_superuser = True
                auth_user.save()

                # Create the user profile
                UserProfile.objects.create(
                    user=auth_user,
                    role=user_data['role'],
                    country_id=user_data['country'],
                    region_id=user_data['region'],
                    station_id=user_data['station']
                )
        self.stdout.write(self.style.SUCCESS(f'{len(users_data)} users and profiles loaded.'))

        # --- Load Dashboard Metrics ---
        self.stdout.write('Loading dashboard metrics...')
        with open(os.path.join(data_path, 'dashboard_metrics.json')) as f:
            metrics_data = json.load(f)
            for metric_data in metrics_data:
                DashboardMetric.objects.create(
                    station_id=metric_data['station_id'],
                    timestamp=parse_datetime(metric_data['timestamp']),
                    output=metric_data['metrics']['output'],
                    temperature=metric_data['metrics']['temperature'],
                    voltage=metric_data['metrics']['voltage'],
                    efficiency=metric_data['metrics']['efficiency']
                )
        self.stdout.write(self.style.SUCCESS(f'{len(metrics_data)} metrics loaded.'))

        # --- Load Audit Logs ---
        self.stdout.write('Loading audit logs...')
        with open(os.path.join(data_path, 'audit_logs.json')) as f:
            logs_data = json.load(f)
            for log_data in logs_data:
                # Ensure the user exists before creating the log
                if User.objects.filter(id=log_data['user_id']).exists():
                    AuditLog.objects.create(
                        user_id=log_data['user_id'],
                        timestamp=parse_datetime(log_data['timestamp']),
                        action=log_data['action'],
                        target=log_data['target'],
                        details=log_data['details']
                    )
        self.stdout.write(self.style.SUCCESS(f'{len(logs_data)} audit logs loaded.'))

        self.stdout.write(self.style.SUCCESS('Data loading complete!'))
