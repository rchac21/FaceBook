# Generated by Django 5.0.2 on 2024-04-22 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_app', '0005_searcheduserstable'),
    ]

    operations = [
        migrations.CreateModel(
            name='Req_Resp_Table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('req_email', models.EmailField(max_length=254)),
                ('resp_email', models.EmailField(max_length=254)),
            ],
        ),
    ]
