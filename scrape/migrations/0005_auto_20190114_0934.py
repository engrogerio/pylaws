# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrape', '0004_auto_20180324_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrape',
            name='post_data',
            field=models.CharField(max_length=100, blank='true', null='true', help_text='Must be a dictionary'),
        ),
        migrations.AlterField(
            model_name='scrape',
            name='request_method',
            field=models.IntegerField(choices=[(1, 'GET'), (2, 'POST')]),
        ),
    ]
