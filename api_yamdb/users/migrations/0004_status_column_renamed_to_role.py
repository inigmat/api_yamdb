# Generated by Django 2.2.16 on 2022-08-10 11:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20220809_1845'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='status',
            new_name='role',
        ),
    ]
