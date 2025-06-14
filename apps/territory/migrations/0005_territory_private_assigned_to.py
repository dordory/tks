# Generated by Django 5.2.1 on 2025-06-10 07:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('territory', '0004_remove_congregation_service_overseer_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='territory',
            name='private_assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='private_territories', to=settings.AUTH_USER_MODEL),
        ),
    ]
