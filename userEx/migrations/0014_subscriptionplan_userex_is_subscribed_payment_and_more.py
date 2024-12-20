# Generated by Django 5.1.1 on 2024-10-22 16:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userEx', '0013_servicerequest_customer'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('plan_type', models.CharField(choices=[('customer', 'Customer'), ('service_provider', 'Service Provider')], max_length=20)),
                ('duration', models.CharField(choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=10)),
                ('tier', models.CharField(choices=[('basic', 'Basic'), ('normal', 'Normal'), ('premium', 'Premium')], max_length=10)),
            ],
        ),
        migrations.AddField(
            model_name='userex',
            name='is_subscribed',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stripe_payment_intent', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userEx.userex')),
            ],
        ),
        migrations.CreateModel(
            name='UserSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField()),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userEx.subscriptionplan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userEx.userex')),
            ],
        ),
    ]
