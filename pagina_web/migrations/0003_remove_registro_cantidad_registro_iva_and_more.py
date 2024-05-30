# Generated by Django 4.2.4 on 2024-04-25 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagina_web', '0002_rename_registros_registro'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registro',
            name='cantidad',
        ),
        migrations.AddField(
            model_name='registro',
            name='iva',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='registro',
            name='subtotal',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='registro',
            name='total',
            field=models.FloatField(default=0),
        ),
    ]