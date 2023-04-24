# Generated by Django 4.1.7 on 2023-04-24 20:35

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import route_settings_builder.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Criterion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('internal_name', models.CharField(max_length=63, unique=True, verbose_name='Внутреннее наименование')),
                ('value_type', models.CharField(choices=[('string', 'Строковый'), ('numeric', 'Числовой'), ('range', 'Диапазон')], default='string', max_length=7, verbose_name='Тип значения')),
            ],
            options={
                'verbose_name': 'Критерий',
                'verbose_name_plural': 'критерии',
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('description', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Описание')),
                ('longitude', models.DecimalField(decimal_places=5, max_digits=8, validators=[route_settings_builder.validators.validate_longitude], verbose_name='Долгота')),
                ('latitude', models.DecimalField(decimal_places=5, max_digits=7, validators=[route_settings_builder.validators.validate_latitude], verbose_name='Широта')),
            ],
            options={
                'verbose_name': 'Место',
                'verbose_name_plural': 'места',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('details', models.JSONField(blank=True, null=True, verbose_name='Описание маршрута')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='routes', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Маршрут',
                'verbose_name_plural': 'маршруты',
            },
        ),
        migrations.CreateModel(
            name='RouteCriterion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=255, verbose_name='Значение')),
                ('criterion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='route_settings_builder.criterion', verbose_name='Критерий')),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='route_settings_builder.route', verbose_name='Маршрут')),
            ],
            options={
                'verbose_name': 'Критерий для маршрута',
                'verbose_name_plural': 'критерии для маршрута',
            },
        ),
        migrations.AddField(
            model_name='route',
            name='criteria',
            field=models.ManyToManyField(related_name='routes', through='route_settings_builder.RouteCriterion', to='route_settings_builder.criterion', verbose_name='Критерии'),
        ),
        migrations.AddField(
            model_name='route',
            name='places',
            field=models.ManyToManyField(related_name='routes', to='route_settings_builder.place', verbose_name='Места'),
        ),
        migrations.CreateModel(
            name='PlaceCriterion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=255, verbose_name='Значение')),
                ('criterion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='route_settings_builder.criterion', verbose_name='Критерий')),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='route_settings_builder.place', verbose_name='Место')),
            ],
            options={
                'verbose_name': 'Критерий для места',
                'verbose_name_plural': 'критерии для места',
            },
        ),
        migrations.AddField(
            model_name='place',
            name='criteria',
            field=models.ManyToManyField(related_name='places', through='route_settings_builder.PlaceCriterion', to='route_settings_builder.criterion', verbose_name='Критерии'),
        ),
        migrations.CreateModel(
            name='Guide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('description', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Описание')),
                ('image', models.ImageField(blank=True, null=True, upload_to='guides/', verbose_name='Файл')),
                ('route', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='guide', to='route_settings_builder.route', verbose_name='Маршрут')),
            ],
            options={
                'verbose_name': 'Путеводитель',
                'verbose_name_plural': 'путеводители',
            },
        ),
    ]
