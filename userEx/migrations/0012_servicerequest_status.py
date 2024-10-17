# Generated by Django 5.1.1 on 2024-10-17 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userEx', '0011_customer_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicerequest',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending', max_length=10),
        ),
    ]