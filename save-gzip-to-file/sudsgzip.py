#!/bin/python
'''
Checks SOAP response for gzip content-types
if found outputs gzip to file and removes 
response data that will break SUDS response parse.
'''

__author__ = 'Adam Sims: mradamsims@gmail.com'
__doc__ = "Filters and saves gzip files"

import zlib

from suds.client import Client
from suds.sax.element import Element
from suds.xsd.doctor import ImportDoctor, Import
from suds.transport.https import HttpAuthenticated
from suds.plugin import MessagePlugin


class MyTransport(HttpAuthenticated):
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
        if client.options.transport.last_headers['content-type'] == 'binary/x-gzip':
            
            # recieved xml as a string
            print "%s bytes recieved" % len(context.reply)
            
            gzip_data = context.reply

            # Set output filename
            filename = client.options.transport.last_headers['content-disposition']
            filename = filename.split('=')[1]
            saveFile(filename, gzip_data)
    
            # Output message
            self.last_payload = 'See file output %s' % filename
            
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

    ClientId= Element('ClientId').setText('authkey')
    UserName= Element('UserName').setText('username')
    Password= Element('Password').setText('password')

    url = 'http://endpoint'

    gzip_filter = GzipFilter()
    client = Client( url,
                 soapheaders= [ ClientId, UserName, Password ],
                 transport=MyTransport(),
                 plugins= [ gzip_filter ],
                 cache= None )


    # SOAP METHOD CALLS
    res = client.service.method(params)
    
    
    # SOAP RESPONSE DATA
    print "received %s bytes" % len(gzip_filter.last_payload)
    print "parsed result: %s" % res
    print client.options.transport.last_headers
    print "response payload: %s" % gzip_filter.last_payload
