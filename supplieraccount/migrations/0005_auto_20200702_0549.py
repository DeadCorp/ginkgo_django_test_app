# Generated by Django 3.0.7 on 2020-07-02 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplieraccount', '0004_auto_20200622_0834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplieraccount',
            name='email',
            field=models.EmailField(default='', max_length=254, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='supplieraccount',
            name='password',
            field=models.TextField(default='', verbose_name='Password'),
        ),
        migrations.AlterField(
            model_name='supplieraccount',
            name='username',
            field=models.TextField(blank=True, default='', verbose_name='Username'),
        ),
    ]
