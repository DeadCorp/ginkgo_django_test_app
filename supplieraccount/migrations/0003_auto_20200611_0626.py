# Generated by Django 3.0.7 on 2020-06-11 06:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supplieraccount', '0002_auto_20200610_1047'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usersupplieraccount',
            old_name='is_current_supplier',
            new_name='is_selected_account',
        ),
    ]
