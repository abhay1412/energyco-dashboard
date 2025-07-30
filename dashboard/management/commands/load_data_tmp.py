# dashboard/management/commands/load_data.py

import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from dashboard.models import UserProfile, Country, Region, Station, DashboardMetric, AuditLog
from django.utils.dateparse import parse_datetime
from django.db import connection

class Command(BaseCommand):
    help = 'Loads data from JSON files into the database and resets sequences'

    def handle(self, *args, **kwargs):
        # Define the path to the JSON files
        data_path = os.path.join(settings.BASE_DIR.parent, 'data')

        # Clear existing data
        self.stdout.write('Clearing old data...')
        AuditLog.objects.all().delete()
        DashboardMetric.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
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
                auth_user = User.objects.create_user(
                    id=user_data['id'],
                    username=user_data['email'],
                    email=user_data['email'],
                    password='password123'
                )
                auth_user.is_active = user_data['active']
                if user_data.get('name'):
                    first_name, last_name = (user_data['name'].split(' ', 1) + [''])[:2]
                    auth_user.first_name = first_name
                    auth_user.last_name = last_name
                if user_data['role'] == 'Admin':
                    auth_user.is_staff = True
                    auth_user.is_superuser = True
                auth_user.save()

                UserProfile.objects.create(
                    user=auth_user,
                    role=user_data['role'],
                    country_id=user_data.get('country'),
                    region_id=user_data.get('region'),
                    station_id=user_data.get('station')
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
                if User.objects.filter(id=log_data['user_id']).exists():
                    AuditLog.objects.create(
                        user_id=log_data['user_id'],
                        timestamp=parse_datetime(log_data['timestamp']),
                        action=log_data['action'],
                        target=log_data['target'],
                        details=log_data['details']
                    )
        self.stdout.write(self.style.SUCCESS(f'{len(logs_data)} audit logs loaded.'))
        
        # --- Reset primary key sequence for the User table ---
        self.stdout.write(self.style.WARNING('Resetting database sequence for User model...'))
        with connection.cursor() as cursor:
            # FIX: Only reset the sequence for auth_user, as other models use non-integer keys.
            table_name = 'auth_user'
            seq_name = 'auth_user_id_seq'
            try:
                cursor.execute(f"SELECT MAX(id) FROM {table_name}")
                max_id = cursor.fetchone()[0]

                if max_id is not None:
                    cursor.execute(f"SELECT setval('{seq_name}', {max_id}, true);")
                else:
                    cursor.execute(f"SELECT setval('{seq_name}', 1, false);")
                    
                self.stdout.write(f"  - Reset sequence for {table_name}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  - Could not reset sequence for {table_name}: {e}"))

        self.stdout.write(self.style.SUCCESS('Database sequences have been reset.'))
        self.stdout.write(self.style.SUCCESS('Data loading complete!'))
