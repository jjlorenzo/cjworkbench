# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-15 17:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0102_remove_workflow_module_library_collapsed'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='anonymous_owner_session_key',
            field=models.CharField(max_length=40, null=True, verbose_name='anonymous_owner_session_key'),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]