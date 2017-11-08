# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-30 21:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cjworkbench', '0003_googlecredentials'),
    ]

    operations = [
        migrations.AlterField(
            model_name='googlecredentials',
            name='id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='google_credentials', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]