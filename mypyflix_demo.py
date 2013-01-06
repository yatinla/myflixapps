#!/usr/bin/env python

'''
Mainly this is to record the API key and shared secret and also 
do a basic test
'''

from pyflix2 import *
import sys
import os
import webbrowser


my_app = 'LoveMoviesToo'
my_request_token = 'cgnq7bbwx8g8hnacwggjbusd'
my_secret = 'cF7neNurgB'

oauth_data = TaylorOauthData( my_app, my_request_token, my_secret )

oauth_data.auth_token = None
oauth_data.auth_secret = None
oauth_data.verified_code = None

search_term = 'Terminator'

netflix = NetflixAPIV2( my_app, my_request_token, my_secret )

movies = netflix.title_autocomplete(search_term)

print 'Movies Titles with ' + search_term + ' in them: ' + "\n"

for title in movies['autocomplete']['autocomplete_item']:
    print '\t' + unicode(title['title']['short'])

try:
  # NOTE: Using OOB for now which means the user must login to Netflix and
  # it will provide a temporary key
  req_token,req_secret,auth_url = netflix.get_request_token(use_OOB = True)
except NetflixError as e:
  print 'Exception getting access token: ', e 
  sys.exit(0)

print 'Got request token and secret: ', req_token + ':' + req_secret

webbrowser.open_new_tab( auth_url )

verification_code = raw_input('Enter access code or q to quit: ')
if verification_code == 'q':
  print 'Bye'
  sys.exit(0)


print 'It got this verification code after logging in with our real Netflix account'
print 'at the auth_url: ' + verification_code 

try:
  access_token, access_secret = netflix.get_access_token( req_token, req_secret, verification_code )
except NetflixError as e:
  print 'Exception getting access token/secret: ', e
  sys.exit(0)
else:
  print 'Access token/secret: ', access_token, '/', access_secret

try:
  user = netflix.get_user(access_token, access_secret)
except NetflixError as e:
  print 'Exception getting user: ', e
  sys.exit(0)
else:
  print 'Got user: ', user

try:
  reco = user.get_reccomendations()
except NetflixError as e:
  print 'Exception getting user recommendations: ', e
  sys.exit(0)

try:
  for movie in reco['recommendations']:
      print movie['title']['regular']
except:
  print 'Exception searching recommended titles'


