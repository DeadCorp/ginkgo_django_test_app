# Generated by Django 3.0.7 on 2020-07-10 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_auto_20200707_0644'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='url',
            new_name='product_url',
        ),
    ]
