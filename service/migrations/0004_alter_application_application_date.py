# Generated by Django 5.1.1 on 2024-12-10 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0003_opportunity_application'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='application_date',
            field=models.DateTimeField(),
        ),
    ]
