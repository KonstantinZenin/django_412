# Generated by Django 5.1.7 on 2025-04-15 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_order_options_alter_service_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='services',
            field=models.ManyToManyField(blank=True, null=True, related_name='orders', to='core.service'),
        ),
    ]
