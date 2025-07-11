# Generated by Django 5.1.7 on 2025-06-24 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_master_options_alter_service_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='duration',
            field=models.PositiveIntegerField(blank=True, default=20, help_text='Время в минутах', verbose_name='Время выполнения услуги'),
        ),
        migrations.AlterField(
            model_name='service',
            name='is_popular',
            field=models.BooleanField(blank=True, default=False, verbose_name='Популярная услуга'),
        ),
    ]
