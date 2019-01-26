# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from lxml import html
import requests 
import sys, os
from law.models import Law
from scrape.utils import get_txt_from_pdf
from scrape.utils import get_txt_from_jpg_from_pdf
from scrape.utils import get_txt_from_jpg
from scrape.utils import get_absolute_url
from django.db import IntegrityError
import json
import logging


class Scrape(models.Model):

    path = os.path.dirname(r'/home/ubuntu/invent/pylaws/')
    # grab configuration variables
    # https://hackernoon.com/4-ways-to-manage-the-configuration-in-python-4623049e841b
    print(path)
    with open(path+'/config.json', 'r') as f:
        config = json.load(f)

    env = config['ENV']
    logging_file = config[env]['LOGGING_FILE']

    # set basic parameters for logging
    logging.basicConfig(level=logging.DEBUG, 
	format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(logging_file),
        logging.StreamHandler()
    ])
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
        Currently accepting PDF or JPG files.
        """
        dic={'content':'', 'error':'URL ' + url + ' contains invalid file. Currently accepting only PDF and JPG !'}
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
        htmlElem = html.fromstring(site.content) #.decode('unicode'))

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
                logging.info('Calculated issue date as %s', issued)
            except IndexError:
                logging.warning('Issued date not defined.')
                issued = '1900-01-01'
            except ValueError:
                issued = '1900-01-01' 
                logging.warning('Issued date with wrong format :%s', law_date[i].text)
            except TypeError:
                issued =  datetime.strptime(law_date[i].text.lstrip().rstrip(), "%d/%m/%Y").strftime('%Y-%m-%d')  
                logging.warning('Issued date with type error :%s', law_date[i].text)
            try: 
                number = self.find_between(law_number[i].text, self.law_number_before_string, self.law_number_after_string).lstrip().rstrip()
                logging.info('Calculated number as %s', number)
            except IndexError:
                number = 'Não Informado'
                logging.warning('Law number not informed. Using: "Não Informado"')
            except TypeError:
                number = law_number[i].text.lstrip().rstrip()
                logging.warning('Law number type error. :%s', law_number[i].text)

            try: 
                type = law_type[i].text.lstrip().rstrip()
                logging.info('Calculated law type as %s', type)
            except IndexError:
                type = 'Não Informado'
                logging.warning('Law type not informed.')

            try: 
                author = law_author[i].text.lstrip().rstrip()
                logging.info('Calculated law author as %s', author)
            except IndexError:
                author = 'Não Informado'
                logging.warning('Author name not informed.')

            try: 
                summary = law_summary[i].text.lstrip().rstrip()
                logging.info('Calculated law summary as %s', summary)
            except IndexError:
                summary = 'Não Informado'
                logging.warning('Law summary not informed.')
            try: 
                link = links[i]
                logging.info('Calculated law link as %s', link)
            except IndexError:
                link = None
                logging.warning('Law link not informed.')

            #create the object law without the texts fields
            law = Law()
            try:
                law = Law.objects.create(city=self.city_name, number=number, summary=summary, 
                created_date=issued, issued_date=issued, is_active = 1, law_type=type, 
                created_by=author, law_url=link, ) 
                logging.info('Created the law %s on database', law)
            except IntegrityError as e:
                logging.warning('There is already information on database for link %s law number %s and date %s. Cause is %s.Ignoring.', 
                    link, number, issued, e)
                continue

            except Exception as e:
                 #print(number, summary, issued, type, author, raw, link)
                logging.warning('Oops...Something went wrong with your request for %s, law %s.Cause is %s.Ignoring.', 
                    link, number, e) #sys.exc_info()[0]))
                continue
            # except:
            #     print(sys.exc_info()[0])

            raw = law_text = ''
            dic={}
            # if there is a link to download from and the law was created, extract the text
            if link and law.id:
                dic = self.get_file_content(link)
                logging.info('Got the content for law No %s: %s', law.id, dic)
            raw = dic
            try:
                law_text = dic['content']
                logging.info('Law content is %s.', law_text)
            except Exception as e:
                law_text='Law content could not be extracted'
                logging.warning('Law content could not be extracted. Error %s.', eval)
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
            logging.info ('Scrapping URL: %s', site.url)
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
        
