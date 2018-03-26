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
import os
import pytesseract
from PIL import Image
from urllib.parse import urlparse
import urllib
from urllib.request import urlopen
import io

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
    
    def get_absolute_url(self, test_url, site_url):
        """
        Returns an absolute URL.If test_url is like "www.domain.com/path" it returns the same url passed.
        When passing "/path",returns the absolute URL "www.domain.com/path" based on site_url
        >>> assertTrue(bool(urlparse('www.domain.com/path').netloc))
        >>> assertFalse(bool(urlparse('/path').netloc))
        """
        if bool(urlparse(test_url).netloc):
            absolute_url = test_url
        else:
            absolute_url = urlparse(site_url).scheme+'://'+urlparse(site_url).netloc+'/'+test_url
        return absolute_url

    def extract_txt_from_jpg(self, file):
        # Extract jpg's from pdf's. Quick and dirty.
        # Saves N files on /tmp/jpgN.jpg

        pdf = open(file, "rb").read()

        startmark = b"\xff\xd8"
        startfix = 0
        endmark = b"\xff\xd9"
        endfix = 2
        i = 0

        njpg = 0
        
        while True:
            istream = pdf.find(b'stream', i)
            
            if istream < 0:
                break
            istart = pdf.find(startmark, istream, istream+20)
            if istart < 0:
                i = istream+20
                continue
            iend = pdf.find(b"endstream", istart)
            if iend < 0:
                raise Exception("Didn't find end of stream!")
            iend = pdf.find(endmark, iend-20)
            if iend < 0:
                raise Exception("Didn't find end of JPG!")

            istart += startfix
            iend += endfix
            print ("JPG %d from %d to %d" % (njpg, istart, iend))
            jpg = pdf[istart:iend]
            jpgfile = open("/tmp/jpg%d.jpg" % njpg, "wb")
            jpgfile.write(jpg)
            jpgfile.close()

            njpg += 1
            i = iend

        # get the text from saved jpgs
        raw=''
        for jpg in range(njpg):
            file = io.BytesIO(b'/tmp/jpg%d.jpg' % jpg).read()
            im=Image.open(file) 
            txt = pytesseract.image_to_string(im, lang='por', config='', nice=0) #, output_type=Output.STRING)
            raw += txt
        # remove used file
            try:
                os.remove('/tmp/jpg%d.jpg' % jpg)
            except OSError:
                pass
        return raw

    def get_file_content(self, url):
        """
        Return file content as raw text that may be a dicionary or just text.
        Uses Apache Tika for PDFs and PyTessaract for images.
        Currently accepted PDF or JPG files.
        """
        raw='URL {0} contains invalid extension. Currently accepting only PDF and JPG !'.format(url)
        #if it's a pdf file, use tikas
        if url[-3:] == 'pdf':
            tika.TikaClientOnly = True
            try: 
                # tika just parse from url !!!
                raw = parser.from_file(url)
                # tika returns the content on the key 'content'
                law_text = raw['content']
            except IndexError:
                raw = 'Link Não Informado'
            except AttributeError:
                raw = 'Link Inválido' + url
            except urllib.error.HTTPError:
                raw = 'Link Inválido' + url
            # if content = None, it means that there is an image inside PDF file, so lets extract it...
            if law_text == None:
                try:
                    # download the file to temporary directory
                    pdf_file = urlopen(url)
                    with open('/tmp/laws_temp.pdf','wb') as output:
                        output.write(pdf_file.read())
                except:
                    raw = 'It was no possible to download file {0}'.format(url)
                try:
                    # extract text from jpg inside pdf    
                    raw = self.extract_txt_from_jpg('/tmp/laws_temp.pdf')
                    os.remove('/tmp/laws_temp.pdf')
                except:
                    raw = 'It was not possible to extract text from {0}. Error {1}'.format(url, sys.exc_info()[0])

        #if it's an image, use tessaract
        if url[-3:] == 'jpg':
            try: 
                # get the image from url !!!
                file = io.BytesIO(urlopen(url).read())
                im = Image.open(file)
                print('Converting {0} - Law number {1} - URL {2}'.format(i, number, url))
                raw = pytesseract.image_to_string(im, lang='por', config='', nice=0) #, output_type=Output.STRING)
            except IndexError:
                raw = 'Link Não Informado'
            except AttributeError:
                raw = 'Link Inválido' + url
            except urllib.error.HTTPError:
                raw = 'Link Inválido' + url
        return raw    

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
            abs_url = self.get_absolute_url(url, self.site_url)
            links.append(abs_url)

        for i in range(len(law_date)):
            try:    
                issued = datetime.strptime(self.find_between(law_date[i].text ,self.promulgation_date_before_string,self.promulgation_date_after_string).lstrip().rstrip(), "%d/%m/%Y").strftime('%Y-%m-%d')
            except IndexError:
                issued = '1900-01-01'
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

            raw = law_text = ''
            #try:
            raw = self.get_file_content(links[i])
            #except:
            #    print(sys.exc_info()[0])

            try:
                # Check if return value raw is a dictionary
                dic = dict(raw)
                # If it is a dictionary, set law_txt = value under 'content' key
                law_text = dic['content']
            except ValueError:
                print('Law {0} has not a dictionary {1}'.format(number, sys.exc_info()[0]))
                # If it is not a dictionary set law_txt = raw and raw is not necessary
                law_text = raw
                raw = ''     

            #create the object law    
            try:
                law = Law.objects.create(city=self.city_name, number=number, summary=summary, 
                created_date=issued, issued_date=issued, is_active = 1, law_type=type, 
                created_by=author, raw=raw, law_url=link, law_text=law_text)

            except:
                 #print(number, summary, issued, type, author, raw, link)
                 print('Oops...Something went wrong with your request for {0}, law {1}.Cause is {2}'.format(
                     site.url, number, sys.exc_info()[0]))

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
        