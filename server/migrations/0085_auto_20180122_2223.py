# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-22 22:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0084_module_html_output'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='module',
            name='html_output',
        ),
        migrations.AddField(
            model_name='moduleversion',
            name='html_output',
            field=models.BooleanField(default=False, verbose_name='html_output'),
        ),
    ]
