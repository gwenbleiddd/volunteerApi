# Generated by Django 5.1.1 on 2024-12-13 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0009_rename_applied_application_apply'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='opportunity',
            name='feedback',
        ),
        migrations.AddField(
            model_name='application',
            name='feedback',
            field=models.TextField(blank=True, null=True),
        ),
    ]
