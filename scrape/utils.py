
from tika import parser
import tika
import sys
import os
import pytesseract
from PIL import Image
from urllib.parse import urlparse
import urllib
from urllib.request import urlopen
import io


def extract_txt_from_jpg(file):
    """ 
    Extract jpg's from pdf's. Quick and dirty.
    and saves N files on C:/temp/jpgN.jpg. Returns a txt.

    """
    pdf = open(file, "rb").read()
    path = 'C:/temp'
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
        jpgfile = open("{0}/jpg{1}.jpg".format(path, njpg), "wb")
        jpgfile.write(jpg)
        jpgfile.close()

        njpg += 1
        i = iend

    # get the text from saved jpgs
    result_txt=''
    for jpg in range(njpg):
        file = io.BytesIO(b"{0}/jpg{1}.jpg".format(path, jpg)).read()
        im=Image.open(file) 
        txt = pytesseract.image_to_string(im, lang='por', config='', nice=0) #, output_type=Output.STRING)
        result_txt += txt
        # remove used file
        try:
            os.remove("{0}/jpg{1}.jpg".format(path, jpg))
        except OSError:
            pass
    return result_txt

def get_txt_from_pdf(url):
    tika.TikaClientOnly = True
    try: 
        # tika just parse from url !!!
        dic = parser.from_file(url)
        # tika returns the content on the key 'content'
        
    except Exception as e:
        dic = {'url': url,'error': e, 'content': None} 
    # except AttributeError:
    #     raise ValueError('Invalid URL {0} - '.format(url))
    # except urllib.error.HTTPError:
    #     raise ValueError('URL Return 404 Error - {0}'.format(url))
    return dic
            
def get_txt_from_jpg_from_pdf(url):
    path = 'C:/temp'
    txt = ''
    try:
        # download the file to temporary directory
        pdf_file = urlopen(url)
        with open('{0}/laws_temp.pdf'.format(path),'wb') as output:
            output.write(pdf_file.read())
        # extract text from jpg inside pdf    
        txt = extract_txt_from_jpg('{0}/laws_temp.pdf'.format(path))
    except Exception as e:
        txt = e
    try:
        os.remove('{0}/laws_temp.pdf'.format(path))
    except:
        pass
    return txt

def get_txt_from_jpg(url):
    try: 
        # get the image from url !!!
        file = io.BytesIO(urlopen(url).read())
        im = Image.open(file)
        dic = {'content': pytesseract.image_to_string(im, lang='por', config='', nice=0) } #, output_type=Output.STRING)
    except Exception as e:
        dic = {'url': url,'error': e, 'content':''} 
    return dic    

def get_absolute_url(test_url, site_url):
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
