# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-11 02:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0095_remove_parameterspec_visible_if_not'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parameterspec',
            name='id_name',
            field=models.CharField(max_length=200, verbose_name='id_name'),
        ),
    ]
