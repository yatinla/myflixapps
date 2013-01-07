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
import json

if len(sys.argv) == 1:
  # Try to get default file 
  fname = 'authinfo'

try:
  authdata = NetflixAuth.load( fname )
except Exception as e:
  print 'Default \'authinfo\' file not found'
  try:
    fname = raw_input('Enter file name with auth info: ')
  except:
    print 'Failed loading auth data from file ' + fname
    print e
    sys.exit(0)

search_term = raw_input('Enter search term: ')

netflix = NetflixAPIV2( authdata.appname, authdata.consumer_token, authdata.consumer_secret )

movies = netflix.title_autocomplete(search_term)

print '\n\nMovies Titles with ' + search_term + ' in them: ' + "\n"

f = open('search.json', 'w' )
f.write(json.dumps( movies, sort_keys=False, indent=4, separators=(',', ': ')))
f.close()

# Well, this is a pretty poor design choice.  If only
# one result is returned then it isn't in an array!
try:
  for title in movies['autocomplete']['autocomplete_item']:
      print '\t' + unicode(title['title']['short'])
except:
    print '\t' + unicode(movies['autocomplete']['autocomplete_item']['title']['short'])

print ''


