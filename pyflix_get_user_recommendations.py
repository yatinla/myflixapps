#!/usr/bin/env python
from pyflix2 import *
import sys
import os
import webbrowser
from netflixauth import NetflixAuth
import json
import pickle
from Tkinter import *

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

# Find out what kind of programming to search for recommendations
# on etc. via a small Tkinter dialog

class SearchDialog:
    MOVIE_TYPE = 1
    TV_TYPE = 2
    def __init__(self, master):

        self.master = master
        frame = Frame(master)
        frame.pack()

        f1 = Frame(frame, padx=10, pady=10)
        f1.pack()
        self.show_type = IntVar()
        self.show_type.set(1)

        self.l = Label(f1,text="Media Type:").pack(side=LEFT,fill=X)
        rb = Radiobutton(f1, text="Television", variable=self.show_type, value=SearchDialog.TV_TYPE).pack(anchor=E,side=RIGHT)
        rb = Radiobutton(f1, text="Movie", variable=self.show_type, value=SearchDialog.MOVIE_TYPE).pack(anchor=W,side=RIGHT)

        f2 = Frame(frame, padx=10, pady=10)
        f2.pack()
        self.l = Label(f2,text="Oldest Year:")
        self.l.pack(side=LEFT) 
        
        self.movie_year_minimum = Spinbox(f2, from_ = 1980, to_ = 2012, width = 8 )
        self.movie_year_minimum.pack(side=RIGHT)

        f3 = Frame(frame, padx=10, pady=10)
        f3.pack()
        self.l = Label(f3,text="Lowest Rating:")
        self.l.pack(side=LEFT) 

        self.lowest_rating = Spinbox(f3, from_ = 1, to_ = 5, increment = 0.1, width = 8 )
        self.lowest_rating.pack(side=RIGHT)

        self.button = Button(master, text="Done", fg="black", command=frame.quit)
        self.button.pack(side=BOTTOM)

        #self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        #self.hi_there.pack(side=LEFT)

    def say_hi(self):
        print "hi there, everyone!"

    def center_window(self, w=300, h=200):
        # get screen width and height
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        # calculate position x, y
        x = (ws/2) - (w/2)    
        y = (hs/2) - (h/2)
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

root = Tk()
root.wm_title("Search Criteria")
dlg = SearchDialog(root)
dlg.center_window()

root.mainloop()

print 'Main loop finished: ', dlg.show_type.get()

if dlg.show_type.get() == SearchDialog.MOVIE_TYPE:
  print 'You selected movies'
elif dlg.show_type.get() == SearchDialog.TV_TYPE:
  print 'You selected television'

print 'Will ignore shows released before ', dlg.movie_year_minimum.get()
print 'Will ignore shows rated less than  ', dlg.lowest_rating.get()


sys.exit(0)

netflix = NetflixAPIV2( authdata.appname, authdata.consumer_token, authdata.consumer_secret )

try:
  user = netflix.get_user(authdata.auth_token, authdata.auth_secret)
except NetflixError as e:
  print 'Exception getting user: ', e
  sys.exit(0)
#else:
#  print 'Got user: ', user

try:
  reco = user.get_reccomendations()
except NetflixError as e:
  print 'Exception getting user recommendations: ', e
  sys.exit(0)

print json.dumps( reco, sort_keys=False, indent=4, separators=(',', ': '))

# Let's pickle it
f = open('Recommendations.pickle', 'wb')
pickle.dump( reco, f )
f.close()
print 'User recommendations saved to Recommendations.pickle'

# Create html file on the fly to display results
results = '<!DOCTYPE HTML> <html> <body>'
results += '<table border="1"> <tr> <th>Title</th> <th>Predicted Rating</th> <th>Average Rating</th> <th>Link</th> <</tr>'

try:
  for movie in reco['recommendations']['recommendation']:
    results += '<tr>'
    results += '<td>' + unicode(movie['title']['regular']).strip() + '</td>'
    results += '<td>' + unicode(movie['predicted_rating']).strip() + '</td>'
    results += '<td>' + unicode(movie['average_rating']).strip() + '</td>'
    results += '<td>'
    # If there's an href (almost certainly there is) add link to display
    for l in movie['link']:
      if 'web page' in l['title']:
        results += "<a href=\"" + l['href'] + "\"><img src=\"" + movie['box_art']['small'] + "\"></a>"
        break
    results += '</td>'

  results += '</table></body></html>'

  #Open results in web browser
  try:
    f = open('recommendations.html', 'w')
    f.write(results)
    f.close()
    webbrowser.open( './recommendations.html' )
  except:
    print 'Could not save/display results in web browser'
    print 'Here they are:'
    print results

except:
  print 'Exception searching recommended titles'

