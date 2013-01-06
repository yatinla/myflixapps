#!/usr/bin/env python
#
# Module to retrieve Netflix authentication token for 
# Netflix applications.
#
import pickle
import sys
import os
from pyflix2 import *
import sys
import os
import webbrowser

class NetflixAuth(object):
  def __init__(self, appname, consumer_token, consumer_secret ):
    self.appname = appname
    self.consumer_token = consumer_token
    self.consumer_secret = consumer_secret
    self.auth_token = None
    self.auth_secret = None
  def user_auth( self, token, secret ):
    self.auth_token = token
    self.auth_secret = secret

  ''' Method to persist object '''
  def persist(self, fname ):
    f = open(fname, 'wb')
    pickle.dump(self,f)
    f.close()

  ''' Class method to load object from file '''
  @staticmethod
  def load(fname):
    print 'Loading from ' + fname
    f = open(fname)
    o = pickle.load(f)
    f.close()
    return o

  def dump(self):
    if self.appname != None:
      print 'Application name: ' + self.consumer_token
    if self.consumer_token != None:
      print 'Consumer token: ' + self.consumer_token
    if self.consumer_secret != None:
      print 'Consumer secret: ' + self.consumer_secret
    if self.auth_token != None:
      print 'Auth token: ' + self.auth_token
    if self.auth_secret != None:
      print 'Auth secret: ' + self.auth_secret

def useage():
    print 'Useage: NetflixAuth.py file_name [get]'
    print '  If get is omitted it attempts to open file_name and'
    print '  display info about netflix authentication.  If'
    print '  get is present also then it attempts to get the auth'
    print '  information and persist it to the file name'

def get_info(fname):
  appname = raw_input("Enter application name:")
  consumer_token = raw_input("Enter consumer token:")
  consumer_secret = raw_input("Enter consumer secret:")
  o = NetflixAuth( appname, consumer_token, consumer_secret )

  netflix = NetflixAPIV2( appname, consumer_token, consumer_secret )

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

  # Save access token and secret and persist
  o.user_auth( access_token, access_secret )
  o.persist(fname)

if __name__ == "__main__":
  if len(sys.argv) < 2:
    useage()
    sys.exit(0)

  fname = sys.argv[1]
  if len(sys.argv) > 2:
    if sys.argv[2] != 'get':
      useage()
      sys.exit(0)
    else:
      get_info(fname)
      print 'The data has been saved in the file ' + fname
      print 'To display the data use this same script without the get argument'
  else:
    o = NetflixAuth.load(fname)
    print "Here is the data from the file %s:\n" % fname
    o.dump() 



