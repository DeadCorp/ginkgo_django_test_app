# Generated by Django 3.0.7 on 2020-06-26 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='delivery_price',
            field=models.CharField(blank=True, default='', max_length=25, verbose_name='Delivery price'),
        ),
    ]