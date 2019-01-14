# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from scrape.models import Scrape
# Register your models here.

class ScrapeMixin:
    def scrape(self, request, queryset):

        form = None
        # Get data from site using scrape
        for c in queryset:
            c.get_site_data()
        rows_updated = queryset.count()

        if rows_updated == 1:
            message_bit = "1 site was"
        else:
            message_bit = "%s sites were" % rows_updated
        self.message_user(request, "%s scraped." % message_bit)

        return response

    scrape.short_description = "Download the laws"
    
class ScrapeAdmin(admin.ModelAdmin, ScrapeMixin):
    actions = ['scrape']
    def get_actions(self, request):
        actions = super(ScrapeAdmin, self).get_actions(request)
        self.actions.append('get_data') 
        return actions

admin.site.register(Scrape, ScrapeAdmin)

