# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-23 22:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('law', '0008_auto_20180323_2245'),
    ]

    operations = [
        migrations.AddField(
            model_name='law',
            name='law_text',
            field=models.TextField(blank='true', null='true'),
        ),
    ]
