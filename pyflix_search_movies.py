#!/usr/bin/env python

'''
Mainly this is to record the API key and shared secret and also 
do a basic test
'''

from pyflix2 import *
import sys
import os
import webbrowser
from netflixauth import NetflixAuth

fname = raw_input('Enter file name with auth info: ')

authdata = NetflixAuth.load( fname )

search_term = raw_input('Enter search term: ')

print 'App name: ', authdata.appname

netflix = NetflixAPIV2( authdata.appname, authdata.consumer_token, authdata.consumer_secret )

movies = netflix.title_autocomplete(search_term)

print 'Movies Titles with ' + search_term + ' in them: ' + "\n"

for title in movies['autocomplete']['autocomplete_item']:
    print '\t' + unicode(title['title']['short'])


