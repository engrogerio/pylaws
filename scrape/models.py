# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from tika import parser
import tika
import requests
from lxml import html
from law.models import Law
import sys

# Create your models here.
class Scrape(models.Model):

    city_name = models.CharField(max_length=200)
    site_url = models.CharField(max_length=200)
    site_parameter_name = models.CharField(max_length=100, blank='true', null='true')
    site_parameter_start = models.IntegerField(blank='true', null='true')
    site_parameter_end = models.IntegerField(blank='true', null='true')

    city_xpath = models.CharField(max_length=200, blank='true', null='true',)

    law_number_xpath = models.CharField(max_length=200, blank='true', null='true',)
    law_number_before_string = models.CharField(max_length = 20, blank='true', null='true',)
    law_number_after_string = models.CharField(max_length = 20, blank='true', null='true',)
    summary_xpath = models.CharField(max_length=200, blank='true', null='true',)
    created_date_xpath = models.CharField(max_length=200, blank='true', null='true',)

    promulgation_date_xpath = models.CharField(max_length=200, blank='true', null='true',)
    promulgation_date_before_string = models.CharField(max_length = 20, blank='true', null='true',)
    promulgation_date_after_string = models.CharField(max_length = 20, blank='true', null='true',)

    law_type_xpath = models.CharField(max_length=200, blank='true', null='true',)
    created_by_xpath = models.CharField(max_length=200, blank='true', null='true',)
    politician_author_xpath = models.CharField(max_length=200, blank='true', null='true',)
    law_url_xpath = models.CharField(max_length=200, blank='true', null='true',)




    def __unicode__(self):
        return self.city_name

    def find_between( self, s, first, last ):
        """
        returns the string between string first and last
        """
        try:
            start = s.index( first ) + len( first )
            if last:
                end = s.index( last, start )
            else:
                end=len(s)
            return s[start:end]
        except ValueError:
            return ""
    

    def scrape(self, site):

        law_date = ''
        law_number = ''
        law_type = ''
        law_author = ''
        law_summary = ''
        law_link = ''
        htmlElem = html.fromstring(site.content)

        # is there an xpath?
        if self.promulgation_date_xpath:    law_date = htmlElem.xpath(self.promulgation_date_xpath)
        if self.law_number_xpath:           law_number = htmlElem.xpath(self.law_number_xpath)
        if self.law_type_xpath:             law_type = htmlElem.xpath(self.law_type_xpath)
        if self.politician_author_xpath:    law_author = htmlElem.xpath(self.politician_author_xpath)
        if self.summary_xpath:              law_summary = htmlElem.xpath(self.summary_xpath)
        if self.law_url_xpath:              law_link = htmlElem.xpath(self.law_url_xpath)

        tika.TikaClientOnly = True
        
        links = []
        for href in law_link:
            links.append(href.get('href'))

        for i in range(len(law_date)):
            
            try:    
                issued = datetime.strptime(self.find_between(law_date[i].text ,self.promulgation_date_before_string,self.promulgation_date_after_string).lstrip().rstrip(), "%d/%m/%Y").strftime('%Y-%m-%d')
            except IndexError:
                issued = 'Não Informado'
            except ValueError:
                issued = '1900-01-01'    
            try: 
                number = self.find_between(law_number[i].text, self.law_number_before_string, self.law_number_after_string).lstrip().rstrip()
            except IndexError:
                number = 'Não Informado'
            try: 
                type = law_type[i].text.lstrip().rstrip()
            except IndexError:
                type = 'Não Informado'
            try: 
                author = law_author[i].text.lstrip().rstrip()
            except IndexError:
                author = 'Não Informado'
            try: 
                summary = law_summary[i].text.lstrip().rstrip()
            except IndexError:
                summary = 'Não Informado'
            try: 
                link = links[i]
            except IndexError:
                link = 'Não Informado'
            try: 
                # tika just parse from url !!!
                raw = parser.from_file(links[i])
                # creates the object on the database
            except IndexError:
                raw = 'Link Não Informado'
            except AttributeError:
                raw = 'Link Inválido'
            try:
                law = Law.objects.create(city=self.city_name, number=number, summary=summary, 
                created_date=issued, issued_date=issued, is_active = 1, law_type=type, 
                created_by=author, text=raw, law_url=link)
            except:
                print(number, summary, issued, type, author, raw, link)
                print('Oops...Something went wrong with your request for {0}.Cause is {1}'.format(
                    site.url, sys.exc_info()[0]))

    def get_site_data(self):

        """
        This methods iterate the site pages to get and save the data on the database:
        
        1 - Calculates the way pylaw should iterate on the site:
        If there is only parameter_start, use it as the only parameter;
        If there is both start and end, creates a loop for [start:end].
        """
        #this inverts the law type dictionary so we can get key from value
        # types_dict = dict(Law.TYPES)
        # inv_type = {v: k for k, v in types_dict.iteritems()}

        parameters={}
        if self.site_parameter_start and not self.site_parameter_end:
            parameters[self.site_parameter_name]=self.site_parameter_start
            site = requests.get(self.site_url, params=parameters)
            self.scrape(site)

        else:
            if self.site_parameter_start and self.site_parameter_end:
                for param in range(self.site_parameter_start, self.site_parameter_end+1):
                    str_param=str(param)
                    parameters[self.site_parameter_name]=str_param
                    site = requests.get(self.site_url, params=parameters)
                    self.scrape(site)