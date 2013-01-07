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
    ANY_TYPE = 3

    def __init__(self, master):

        self.master = master
        frame = Frame(master)
        frame.pack()

        params = FilterParams.load()

        f1 = Frame(frame, padx=10, pady=10)
        f1.pack()
        self.show_type = IntVar()
        self.show_type.set(params.category)

        self.l = Label(f1,text="Media Type:").pack(side=LEFT,fill=X)
        rb = Radiobutton(f1, text="Any", variable=self.show_type, value=SearchDialog.ANY_TYPE).pack(anchor=W,side=RIGHT)
        rb = Radiobutton(f1, text="Television", variable=self.show_type, value=SearchDialog.TV_TYPE).pack(anchor=E,side=RIGHT)
        rb = Radiobutton(f1, text="Movie", variable=self.show_type, value=SearchDialog.MOVIE_TYPE).pack(anchor=W,side=RIGHT)

        f2 = Frame(frame, padx=10, pady=10)
        f2.pack()
        self.l = Label(f2,text="Oldest Year:")
        self.l.pack(side=LEFT) 
       
        self.released = StringVar()
        self.movie_year_minimum = Spinbox(f2, from_ = 1900, to_ = 2012, width = 8, textvariable=self.released )
        self.released.set(str(params.released))
        self.movie_year_minimum.pack(side=RIGHT)

        f3 = Frame(frame, padx=10, pady=10)
        f3.pack()
        self.l = Label(f3,text="Lowest Rating:")
        self.l.pack(side=LEFT) 

        self.rating = StringVar()
        self.lowest_rating = Spinbox(f3, from_ = 1, to_ = 5, increment = 0.1, width = 8, textvariable=self.rating )
        self.rating.set(str(params.rating))
        self.lowest_rating.pack(side=RIGHT)

        self.button = Button(master, text="Done", fg="black", command=frame.quit)
        self.button.pack(side=BOTTOM)

    ## TODO: Why does it not work to use this save?  Seems like pickle tries
    ## to pickle the SearchDialog object as if in FilterParams.save() the 'self'
    ## is treated as the 'self' of SearchDialog object????
    def save(self):
        params = FilterParams( category=self.show_type.get(), released = self.movie_year_minimum, 
                               rating=self.lowest_rating )
        print 'params is ', params
        params.save()

    def center_window(self, w=300, h=200):
        # get screen width and height
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        # calculate position x, y
        x = (ws/2) - (w/2)    
        y = (hs/2) - (h/2)
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

class FilterParams(object):
  '''
    Class to persist the filter params
  '''
  def __init__(self, category=SearchDialog.MOVIE_TYPE, released=2000, rating=3.5 ):
    self.category = category
    self.released = released
    self.rating = rating

  def save(self):
    f = open('filter.ini', 'wb')
    pickle.dump(self,f)
    f.close()

  @staticmethod
  def load():
    try:
      f = open('filter.ini')
      return pickle.load(f)
    except:
      return FilterParams()

root = Tk()
root.wm_title("Search Criteria")
dlg = SearchDialog(root)
dlg.center_window()

root.mainloop()

category = dlg.show_type.get()

if category == SearchDialog.MOVIE_TYPE:
  print 'Will show results only for movies'
elif category == SearchDialog.TV_TYPE:
  print 'Will show results only for TV'
elif category == SearchDialog.ANY_TYPE:
  print 'Will show results for TV or movies'

print 'Will ignore shows released before ', dlg.movie_year_minimum.get()
print 'Will ignore shows rated less than  ', dlg.lowest_rating.get()

try:
  released_after = int(dlg.movie_year_minimum.get())
except:
  print 'Invalid year!'
  sys.exit(0)

try:
  min_rating = float(dlg.lowest_rating.get())
except:
  print 'Invalid minimum rating'
  sys.exit(0)

# Save choices for next time to load upon starting
#dlg.save()

params = FilterParams( category=category,released=released_after, rating=min_rating )
print 'params is ', params
params.save()

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

# For debugging mostly save results as json string
f = open('recommendations.json', 'w' )
f.write(json.dumps( reco, sort_keys=False, indent=4, separators=(',', ': ')))
f.close()

# Let's pickle it
f = open('Recommendations.pickle', 'wb')
pickle.dump( reco, f )
f.close()
print 'User recommendations saved to Recommendations.pickle'


def filter_show( movie, cat=SearchDialog.ANY_TYPE, released=0, min_rating=0.0 ):
  '''
    Return True if the show should be included
    in the results or False otherwise
  '''
  if cat != SearchDialog.ANY_TYPE:
    for c in movie['category']:
      is_tv = 'tv' in c['term'].lower() or 'television' in c['term'].lower()
      if cat == SearchDialog.MOVIE_TYPE:
        if is_tv:
          return False
      elif cat == SearchDialog.TV_TYPE:
        if not is_tv:
          return False
  try:
    release_date = int(movie['release_year'])
    if release_date < released:
      #print 'Show is too old: ', release_date
      return False
  except:
    print 'Hmmm, release_date from Netflix seems invalid'

  try:
    rating = float(movie['average_rating'])
    if rating < min_rating:
      #print 'Rating is too low: ', rating
      return False
  except:
    print 'Hmmm, release_date from Netflix seems invalid'

  return True


# Create html file on the fly to display results
results = '<!DOCTYPE HTML> <html> <body>'
results += '<table border="1"> <tr> <th>Title</th> <th>Released</th> <th>Predicted Rating</th> <th>Average Rating</th> <th>Link</th> </tr>'

matches = 0

try:
  for movie in reco['recommendations']['recommendation']:

    # Skip movies that don't match search criteria
    if not filter_show( movie, category, released_after, min_rating ):
      continue

    matches += 1
    results += '<tr>'
    results += '<td>' + unicode(movie['title']['regular']).strip() + '</td>'
    results += '<td>' + unicode(movie['release_year']).strip() + '</td>'
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
    try:
      # Prefer firefox
      #webbrowser.register('firefox')
      wb = webbrowser.get('firefox')
      wb.open_new_tab('./recommendations.html')
    except:
      # Use default
      print 'Use default browser'
      webbrowser.open_new_tab( './recommendations.html' )
  except:
    print 'Could not save/display results in web browser'
    print 'Here they are:'
    print results

except:
  print 'Exception searching recommended titles'

