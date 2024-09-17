# Generated by Django 5.1.1 on 2024-09-16 18:00

import django.contrib.auth.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('userEx', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserEx',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('isServiceProvider', models.BooleanField(default=False)),
                ('isCustomer', models.BooleanField(default=False)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('zipCode', models.CharField(blank=True, max_length=10, null=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
