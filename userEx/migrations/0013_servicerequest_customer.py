# Generated by Django 5.1.1 on 2024-10-17 14:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userEx', '0012_servicerequest_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicerequest',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='userEx.customer'),
        ),
    ]