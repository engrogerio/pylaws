# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from law.models import Law
from django.contrib import admin
import csv
from django.http import HttpResponse

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields if field.name !='law_text']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

class LawAdmin(admin.ModelAdmin, ExportCsvMixin): 
    actions = ['export_as_csv']
    list_display = ('number', 'city', 'law_type', 'issued_date', 'created_by', 'scrapped_date', 'summary', 'law_url')
    search_fields = ['summary', 'number', 'law_text', 'created_by',]
    list_filter = ['city', 'law_type', 'created_by']
    # readonly_fields = ('city', 'number', 'summary','created_date', 'issued_date', 'is_active', 'law_type',
    # 'created_by', 'raw', 'law_text', 'law_url')


# Register your models here.
admin.site.register(Law, LawAdmin)
