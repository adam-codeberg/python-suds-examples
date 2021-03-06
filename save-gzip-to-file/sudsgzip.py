#!/bin/python
'''
Checks SOAP response for gzip content-types if
found outputs gzip to file then removes response 
data so it will not break SUDS response parse.
'''

__author__ = 'Adam Sims: mradamsims at gmail dot com'
__doc__ = "Filters and saves gzip files"

from suds.client import Client
from suds.sax.element import Element
from suds.xsd.doctor import ImportDoctor, Import
from suds.transport.https import HttpAuthenticated
from suds.plugin import MessagePlugin

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.INFO)
logging.getLogger('suds.xsd.schema').setLevel(logging.INFO)
logging.getLogger('suds.wsdl').setLevel(logging.INFO)



class GzipSudsTransport(HttpAuthenticated):
  def __init__(self,*args,**kwargs):
    HttpAuthenticated.__init__(self,*args,**kwargs)
    self.last_headers = None

  def send(self,request):
    result = HttpAuthenticated.send(self,request)
    self.last_headers = result.headers
    return result


class GzipFilter(MessagePlugin):
    def __init__(self, *args, **kwargs):
        self.last_payload = None

    def received(self, context):
        logging.info('detected content-type: {}'.format(client.options.transport.last_headers['content-type']))
        if client.options.transport.last_headers['content-type'] == 'binary/x-gzip':
            gzip_data = context.reply

            # Set output filename
            filename = client.options.transport.last_headers['content-disposition']
            filename = filename.split('=')[1]
            saveFile(filename, gzip_data)
    
            # Output message
            self.last_payload = filename
            
            #remove gzip to avoid SUDS parse errors
            context.reply = ""
            return context
        else:
            self.last_payload = context.reply


def saveFile(filename, data):
    f = open(filename,'w')
    f.write(data) 
    f.close() 
            
if __name__=='__main__':

    # Add or remove header authentication fields
    ClientId= Element('ClientId').setText('key')
    UserName= Element('UserName').setText('username')
    Password= Element('Password').setText('password')

    url = 'http://endpoint'

    gzip_filter = GzipFilter()
    client = Client( url,
                 soapheaders= [ ClientId, UserName, Password ],
                 transport=GzipSudsTransport(),
                 plugins= [ gzip_filter ],
                 cache= None )


    # SOAP METHOD CALLS
    res = client.service.method(params)
    
    
    # SOAP RESPONSE DATA
    logging.debug("received: {}".format(len(gzip_filter.last_payload)))
    logging.debug("parsed: {}".format(res))
    logging.debug("headers: {}".format(client.options.transport.last_headers))
    logging.info("output: {}".format(gzip_filter.last_payload))
