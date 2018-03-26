# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from law.models import Law
from django.contrib import admin


class LawAdmin(admin.ModelAdmin): 
    list_display = ('number', 'city', 'law_type', 'issued_date', 'created_by', 'summary', 'law_url')
    search_fields = ['summary', 'number', 'law_text']
    list_filter = ['city', 'law_type', 'created_by']
    # readonly_fields = ('city', 'number', 'summary','created_date', 'issued_date', 'is_active', 'law_type',
    # 'created_by', 'raw', 'law_text', 'law_url')


# Register your models here.
admin.site.register(Law, LawAdmin)
