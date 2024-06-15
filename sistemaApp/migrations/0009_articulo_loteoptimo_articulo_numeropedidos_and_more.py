# Generated by Django 5.0.4 on 2024-06-15 18:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistemaApp', '0008_rename_cantidadddemanda_demandahistorica_cantidaddemanda'),
    ]

    operations = [
        migrations.AddField(
            model_name='articulo',
            name='loteOptimo',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='articulo',
            name='numeroPedidos',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='articulo',
            name='proveedor_predefinido',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sistemaApp.proveedor'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='tiempoEntrePedidos',
            field=models.IntegerField(default=0),
        ),
    ]
