# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-31 14:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0136_auto_20181030_2217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addmodulecommand',
            name='order',
        ),
        migrations.RemoveField(
            model_name='addmodulecommand',
            name='selected_wf_module',
        ),
    ]
