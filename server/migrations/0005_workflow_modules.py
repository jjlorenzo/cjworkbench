# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-21 18:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0004_remove_workflow_modules'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='modules',
            field=models.ManyToManyField(to='server.WfModule'),
        ),
    ]
