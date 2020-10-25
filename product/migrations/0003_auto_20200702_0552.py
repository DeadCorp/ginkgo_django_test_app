# Generated by Django 3.0.7 on 2020-07-02 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_auto_20200626_0909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='available_count',
            field=models.CharField(blank=True, default='', max_length=25, verbose_name='Available count'),
        ),
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.TextField(blank=True, default='', verbose_name='Brand'),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.TextField(blank=True, default='', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='product',
            name='img',
            field=models.TextField(blank=True, default='', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='product',
            name='model',
            field=models.TextField(blank=True, default='', verbose_name='Model'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.TextField(blank=True, default='', verbose_name='Product name'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(max_length=255, primary_key=True, serialize=False, verbose_name='Product SKU'),
        ),
        migrations.AlterField(
            model_name='product',
            name='url',
            field=models.TextField(blank=True, default='', verbose_name='Url'),
        ),
        migrations.AlterField(
            model_name='product',
            name='variants_tag',
            field=models.TextField(blank=True, default='', verbose_name='Variants'),
        ),
    ]