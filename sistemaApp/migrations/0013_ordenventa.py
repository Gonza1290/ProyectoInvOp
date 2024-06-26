# Generated by Django 5.0.4 on 2024-06-30 20:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistemaApp', '0012_articulo_demandapredecida'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrdenVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidadVendida', models.IntegerField(default=1)),
                ('montoTotal', models.IntegerField(default=0)),
                ('fechaHoraVenta', models.DateField(blank=True, default=None, null=True)),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordenes_venta', to='sistemaApp.articulo')),
            ],
        ),
    ]
