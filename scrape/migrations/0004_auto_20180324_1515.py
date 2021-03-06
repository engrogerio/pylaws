# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-24 15:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrape', '0003_auto_20180322_0047'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrape',
            name='post_data',
            field=models.CharField(blank='true', help_text='Use it for POST requests', max_length=100, null='true'),
        ),
        migrations.AddField(
            model_name='scrape',
            name='request_method',
            field=models.IntegerField(choices=[(1, 'Get Request'), (2, 'Post Request')], default=1),
            preserve_default=False,
        ),
    ]
