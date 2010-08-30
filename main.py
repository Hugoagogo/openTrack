#!/usr/bin/env python
#
# openTrack
#
#     http://www.importsoul.net/
#
import re, os, logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from models import Tracker, Peer
from datetime import datetime, timedelta


class MainHandler(webapp.RequestHandler):
    def get(self):
        if os.environ.get('HTTP_HOST'):
            url = os.environ['HTTP_HOST']
        else:
            url = os.environ['SERVER_NAME']

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(
"""OpenTrack\n
Extreamly Basic tracking system, for use with p2p programs

To use the tracker visit

http://%s/trk/<tracker name>

The tracker does not need to be setup beforhand
It will return a list of IP adresses that have visited
that tracker and add yours to the list

Optionally add "?tick=<seconds>" to the url where seconds
is how recently it has been visited the default tick is 60 seconds
 
\nCurrent Trackers (activity last 24 hours)\n"""%(url))
        trackers = Tracker.all()
        for tracker in trackers:
            self.response.out.write(" - %s\n"%tracker.name)
        

class NewTrackerHandler(webapp.RequestHandler):
    def get(self,key):
        self.response.headers['Content-Type'] = 'text/plain'
        if re.match(r"\w{3,25}",key):
            tracker = list(Tracker.all().filter('name =',key))
            if len(tracker):
                self.response.out.write('Tracker "%s" already exists, you can still use it though'%key)
            else:
                Tracker(name=key).put()
                self.response.out.write('Tracker "%s" created'%key)
            
        else:
            self.response.out.write('Tracker must contain only numbers, letters and the underscore, it must also be between 3 and 25 charachters')

class TrackerHandler(webapp.RequestHandler):
    def get(self,key):
        self.response.headers['Content-Type'] = 'text/plain'
        if re.match(r"\w{3,25}",key):
            tracker = Tracker.all().filter('name =',key).get()
            if tracker==None:
                tracker = Tracker(name=key)
                tracker.put()
                
            p = Peer.all().filter('address =',self.request.remote_addr).filter('tracker =',tracker).get()
            if p != None:
                p.put()
            else:
                Peer(address=self.request.remote_addr,tracker=tracker).put()

            plist = Peer.all().filter('tracker =',tracker)
            try:
                tick = int(self.request.get('tick'))
            except:
                tick = 60
                
            plist.filter('datetime >',datetime.now() - timedelta(seconds=tick))
            
            for peer in plist:
                if peer.address != self.request.remote_addr:
                    self.response.out.write(peer.address+"\n")
        else:
            self.response.out.write('Tracker must contain only numbers, letters and the underscore, it must also be between 3 and 25 charachters')
class CleanHandler(webapp.RequestHandler):
    def get(self):
        plist = Peer.all().filter('datetime <',datetime.now() - timedelta(days=1))
        peercount = plist.count()
        for p in plist:
            p.delete()
        
        trackers = Tracker.all()
        trackercount = 0
        for tracker in trackers:
            p = Peer.all().filter('tracker =',tracker).order('-datetime').get()
            if p == None:
                tracker.delete()
                trackercount += 1
        
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("Cleaned %d trackers and %d peers"%(trackercount,peercount))
        if trackercount and peercount:
            logging.info("Cleaned %d trackers and %d peers"%(trackercount,peercount))


def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/new/(.*?)/?', NewTrackerHandler),
                                          ('/trk/(.*?)/?', TrackerHandler),
                                          ('/clean/', CleanHandler)],
                                         debug=True)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
