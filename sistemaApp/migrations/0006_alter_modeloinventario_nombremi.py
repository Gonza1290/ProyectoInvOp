# Generated by Django 5.0.4 on 2025-03-02 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistemaApp', '0005_rename_category_categoria_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modeloinventario',
            name='nombreMI',
            field=models.CharField(max_length=100),
        ),
    ]
