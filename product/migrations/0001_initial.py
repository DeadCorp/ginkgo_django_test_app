# Generated by Django 3.0.7 on 2020-06-10 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('sku', models.CharField(max_length=100, primary_key=True, serialize=False, verbose_name='Product SKU')),
                ('product_id', models.CharField(blank=True, default='', max_length=100, verbose_name='Supplier product id')),
                ('option_id', models.CharField(blank=True, default='', max_length=100, verbose_name='Supplier option id')),
                ('name', models.CharField(blank=True, default='', max_length=100, verbose_name='Product name')),
                ('price', models.CharField(blank=True, default='', max_length=50, verbose_name='Price')),
                ('url', models.CharField(blank=True, default='', max_length=100, verbose_name='Url')),
                ('category', models.CharField(blank=True, default='', max_length=100, verbose_name='Category')),
                ('rating', models.CharField(blank=True, default='', max_length=25, verbose_name='Rating')),
                ('available', models.CharField(blank=True, default='', max_length=25, verbose_name='Availability')),
                ('brand', models.CharField(blank=True, default='', max_length=25, verbose_name='Brand')),
                ('available_count', models.CharField(blank=True, default='', max_length=10, verbose_name='Available count')),
                ('delivery_price', models.CharField(blank=True, default='', max_length=10, verbose_name='Delivery price')),
                ('variants_tag', models.CharField(blank=True, default='', max_length=100, verbose_name='Variants')),
                ('img', models.CharField(blank=True, default='', max_length=100, verbose_name='Image')),
                ('supplier', models.CharField(blank=True, default='', max_length=2, verbose_name='Supplier')),
                ('model', models.CharField(blank=True, default='', max_length=25, verbose_name='Model')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description')),
                ('is_variant', models.BooleanField(blank=True, default=False, verbose_name='Is variance product')),
                ('delivery', models.BooleanField(blank=True, default=False, verbose_name='Delivery')),
                ('shipping', models.BooleanField(blank=True, default=False, verbose_name='Shipping')),
                ('store_pickup', models.BooleanField(blank=True, default=False, verbose_name='Store pickup')),
            ],
        ),
    ]
