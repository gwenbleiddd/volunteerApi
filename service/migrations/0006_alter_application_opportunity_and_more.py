# Generated by Django 5.1.1 on 2024-12-11 14:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0005_customuser_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='opportunity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='applications', to='service.opportunity'),
        ),
        migrations.AlterField(
            model_name='application',
            name='volunteer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='applications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='opportunities', to=settings.AUTH_USER_MODEL),
        ),
    ]