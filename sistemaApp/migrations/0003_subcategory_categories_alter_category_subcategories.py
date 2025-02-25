# Generated by Django 5.0.4 on 2025-02-25 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistemaApp', '0002_rename_fechahorabajaarticulo_articulo_fechahorabaja_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='subCategories_set', to='sistemaApp.category'),
        ),
        migrations.AlterField(
            model_name='category',
            name='subCategories',
            field=models.ManyToManyField(blank=True, related_name='categories_set', to='sistemaApp.subcategory'),
        ),
    ]
