# Generated by Django 3.0.7 on 2020-06-10 10:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supplieraccount', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supplieraccount',
            name='is_current_supplier',
        ),
        migrations.CreateModel(
            name='UserSupplierAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_current_supplier', models.BooleanField(blank=True, default=False, verbose_name='Selected account')),
                ('supplier_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supplieraccount.SupplierAccount', verbose_name='Supplier account')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]
