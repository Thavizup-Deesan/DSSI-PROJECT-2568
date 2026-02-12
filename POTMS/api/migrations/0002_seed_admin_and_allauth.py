"""
Data migration: สร้าง admin users เริ่มต้น + ตั้งค่า Google SocialApp

Admin เริ่มต้น: wayo.p@ubu.ac.th, thavizup.de.66@ubu.ac.th
เพิ่ม admin เพิ่มเติมได้ผ่าน env POTMS_ADMIN_EMAILS (comma-separated)
"""
import os
from django.db import migrations


# Admin emails เริ่มต้น
DEFAULT_ADMIN_EMAILS = [
    'wayo.p@ubu.ac.th',
    'thavizup.de.66@ubu.ac.th',
]


def seed_admin_users(apps, schema_editor):
    User = apps.get_model('api', 'User')

    # รวม admin เริ่มต้น + จาก env variable
    admin_emails = list(DEFAULT_ADMIN_EMAILS)
    extra = os.environ.get('POTMS_ADMIN_EMAILS', '')
    if extra:
        admin_emails += [e.strip() for e in extra.split(',') if e.strip()]

    for email in admin_emails:
        User.objects.get_or_create(
            email=email,
            defaults={
                'full_name': email.split('@')[0].replace('.', ' ').title(),
                'is_admin': True,
                'is_officer': True,
            }
        )


def setup_google_social_app(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    SocialApp = apps.get_model('socialaccount', 'SocialApp')

    # สร้าง/อัปเดต Site id=1
    site, _ = Site.objects.get_or_create(
        id=1,
        defaults={'domain': 'localhost:8000', 'name': 'POTMS'}
    )

    # สร้าง Google SocialApp
    social_app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Google',
            'client_id': os.environ.get(
                'GOOGLE_CLIENT_ID',
                '129454383537-0ceqhjq06rnmv9tf1jjgoakmc8mjcqo0.apps.googleusercontent.com'
            ),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
        }
    )
    social_app.sites.add(site)


def reverse(apps, schema_editor):
    User = apps.get_model('api', 'User')
    SocialApp = apps.get_model('socialaccount', 'SocialApp')

    User.objects.filter(email__in=DEFAULT_ADMIN_EMAILS).delete()
    SocialApp.objects.filter(provider='google').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
        ('socialaccount', '0006_alter_socialaccount_extra_data'),
    ]

    operations = [
        migrations.RunPython(seed_admin_users, reverse),
        migrations.RunPython(setup_google_social_app, reverse),
    ]
