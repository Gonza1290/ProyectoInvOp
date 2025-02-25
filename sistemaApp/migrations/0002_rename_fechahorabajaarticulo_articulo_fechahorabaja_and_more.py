# Generated by Django 5.0.4 on 2025-02-25 20:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sistemaApp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='articulo',
            old_name='fechaHoraBajaArticulo',
            new_name='fechaHoraBaja',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='fechaHoraBajaCategory',
            new_name='fechaHoraBaja',
        ),
        migrations.RenameField(
            model_name='estadoordencompra',
            old_name='fechaHoraBajaEOC',
            new_name='fechaHoraBaja',
        ),
        migrations.RenameField(
            model_name='marca',
            old_name='fechaHoraBajaMarca',
            new_name='fechaHoraBaja',
        ),
        migrations.RenameField(
            model_name='modeloinventario',
            old_name='fechaHoraBajaMI',
            new_name='fechaHoraBaja',
        ),
        migrations.RenameField(
            model_name='proveedor',
            old_name='fechaHoraBajaProveedor',
            new_name='fechaHoraBaja',
        ),
        migrations.RenameField(
            model_name='subcategory',
            old_name='fechaHoraBajaSubCategory',
            new_name='fechaHoraBaja',
        ),
        migrations.RenameField(
            model_name='unidadmedida',
            old_name='fechaHoraBajaUM',
            new_name='fechaHoraBaja',
        ),
    ]
