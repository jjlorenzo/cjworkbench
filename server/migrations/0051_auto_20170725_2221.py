# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-25 22:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0050_auto_20170725_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wfmodule',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
