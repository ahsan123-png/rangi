# Generated by Django 5.1.1 on 2024-10-08 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userEx', '0010_spprofile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='customerDp/'),
        ),
    ]
