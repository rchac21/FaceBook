# Generated by Django 5.0.2 on 2024-04-23 15:23

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_app', '0006_req_resp_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='posts',
            name='date_added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
