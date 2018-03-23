# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-22 00:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrape', '0002_auto_20180318_0131'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scrape',
            old_name='issued_date_xpath',
            new_name='promulgation_date_xpath',
        ),
        migrations.AddField(
            model_name='scrape',
            name='law_number_after_string',
            field=models.CharField(blank='true', max_length=20, null='true'),
        ),
        migrations.AddField(
            model_name='scrape',
            name='law_number_before_string',
            field=models.CharField(blank='true', max_length=20, null='true'),
        ),
        migrations.AddField(
            model_name='scrape',
            name='promulgation_date_after_string',
            field=models.CharField(blank='true', max_length=20, null='true'),
        ),
        migrations.AddField(
            model_name='scrape',
            name='promulgation_date_before_string',
            field=models.CharField(blank='true', max_length=20, null='true'),
        ),
    ]