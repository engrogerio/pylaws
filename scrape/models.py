# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from lxml import html
import requests 
import sys
from law.models import Law
from scrape.utils import get_txt_from_pdf
from scrape.utils import get_txt_from_jpg_from_pdf
from scrape.utils import get_txt_from_jpg
from scrape.utils import get_absolute_url


# Create your models here.
class Scrape(models.Model):

    GET = 1
    POST = 2

    REQUEST_METHOD = (
        (GET, 'GET'),
        (POST, 'POST'),
    )

    city_name = models.CharField(max_length=200)
    site_url = models.CharField(max_length=200)

    site_parameter_name = models.CharField(max_length=100, blank='true', null='true')
    site_parameter_start = models.IntegerField(blank='true', null='true')
    site_parameter_end = models.IntegerField(blank='true', null='true')

    request_method = models.IntegerField(choices=REQUEST_METHOD)
    post_data = models.CharField(max_length=100, blank='true', null='true', help_text='Must be a dictionary')

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

    def __str__(self):
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
    
   
    def get_file_content(self, url):
        """
        Returns a dicionary.
        Uses Apache Tika for PDFs and PyTessaract for images.
        Currently accepted PDF or JPG files.
        """
        dic={'content':'', 'error':'URL {0} contains invalid file. Currently accepting only PDF and JPG !'.format(url)}
        if url[-3:] == 'pdf':
            dic = get_txt_from_pdf(url)
            #if there is no content, extracts text from image from pdf
            if not dic['content']:
                dic['content'] = get_txt_from_jpg_from_pdf(url)

        if url[-3:] == 'jpg':    
            dic = get_txt_from_jpg(url)

        return dic

    def scrape(self, site):
        """
        Populates the laws database based on passed site.
        Fields are:
        law_date,law_number,law_type,law_author,law_summary,law_link
        """
        law_date = ''
        law_number = ''
        law_type = ''
        law_author = ''
        law_summary = ''
        law_link = ''
        htmlElem = html.fromstring(site.content.decode('utf-8'))

        # is there an xpath?
        if self.promulgation_date_xpath:    law_date = htmlElem.xpath(self.promulgation_date_xpath)
        if self.law_number_xpath:           law_number = htmlElem.xpath(self.law_number_xpath)
        if self.law_type_xpath:             law_type = htmlElem.xpath(self.law_type_xpath)
        if self.politician_author_xpath:    law_author = htmlElem.xpath(self.politician_author_xpath)
        if self.summary_xpath:              law_summary = htmlElem.xpath(self.summary_xpath)
        if self.law_url_xpath:              law_link = htmlElem.xpath(self.law_url_xpath)
        
        links = []
        for href in law_link:
            url = href.get("href")
            #There are sites that store just relative url path
            abs_url = get_absolute_url(url, self.site_url)
            links.append(abs_url)

        for i in range(len(law_date)):
            try:    
                issued = datetime.strptime(self.find_between(law_date[i].text ,self.promulgation_date_before_string,self.promulgation_date_after_string).lstrip().rstrip(), "%d/%m/%Y").strftime('%Y-%m-%d')
            except IndexError:
                issued = '1900-01-01'
            except ValueError:
                issued = '1900-01-01' 
            except TypeError:
                issued =  datetime.strptime(law_date[i].text.lstrip().rstrip(), "%d/%m/%Y").strftime('%Y-%m-%d')  
            
            try: 
                number = self.find_between(law_number[i].text, self.law_number_before_string, self.law_number_after_string).lstrip().rstrip()
            except IndexError:
                number = 'Não Informado'
            except TypeError:
                 number = law_number[i].text.lstrip().rstrip()

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
                link = None

            #create the object law without the texts fields
            law = Law()
            try:
                law = Law.objects.create(city=self.city_name, number=number, summary=summary, 
                created_date=issued, issued_date=issued, is_active = 1, law_type=type, 
                created_by=author, law_url=link, ) 
            except:
                 #print(number, summary, issued, type, author, raw, link)
                 print('Oops...Something went wrong with your request for {0}, law {1}.Cause is {2}'.format(
                        link, number, sys.exc_info()[0]))

            # except:
            #     print(sys.exc_info()[0])

            raw = law_text = ''
            dic={}
            # if there is a link to download from and the law was created, extract the text
            if link and law.id:
                dic = self.get_file_content(link)

            raw = dic
            try:
                law_text = dic['content']
            except:
                law_text=''

            #Now that the Law was created, extracts the text from file and add to the law
            
            Law.objects.filter(pk=law.id).update(raw=dic, law_text=law_text)

    def get_site_data(self):

        """
        This methods iterate the site pages to get and save the data on the database:
        
        1 - Calculates the way pylaw should iterate on the site:
        If there is only parameter_start, use it as the only parameter;
        If there is both start and end, creates a loop for [start:end].
        2 - Request may be GET or POST
        """
        
        parameters={}
        if self.site_parameter_start and not self.site_parameter_end and self.request_method == self.GET:
            parameters[self.site_parameter_name]=self.site_parameter_start
            site = requests.get(self.site_url, params=parameters)
            self.scrape(site)
        else:
            if self.site_parameter_start and self.site_parameter_end and self.request_method == self.GET:
                for param in range(self.site_parameter_start, self.site_parameter_end+1):
                    str_param=str(param)
                    parameters[self.site_parameter_name]=str_param
                    site = requests.get(self.site_url, params=parameters)      
                    self.scrape(site)      
            else:
                if self.site_parameter_start and self.site_parameter_end and self.request_method == self.POST:
                    for param in range(self.site_parameter_start, self.site_parameter_end+1):
                        data = dict(eval(self.post_data))
                        data[self.site_parameter_name] = param
                        site = requests.post(self.site_url, data=data)
                        self.scrape(site)
        