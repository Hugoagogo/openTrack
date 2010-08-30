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

class TrackerHandler(webapp.RequestHandler):
    def get(self,key):
        self.response.headers['Content-Type'] = 'text/plain'
        if re.match(r"\w{3,25}",key): ## check if a tracker is valid
            ## Check if the tracker exists, if not create it
            tracker = Tracker.all().filter('name =',key).get()
            if tracker==None:
                tracker = Tracker(name=key)
                tracker.put()

            ## Check if the peer making the request is already in the DB, if not add them
            p = Peer.all().filter('address =',self.request.remote_addr).filter('tracker =',tracker).get()
            if p != None:
                p.put()
            else:
                Peer(address=self.request.remote_addr,tracker=tracker).put()

            ## try getting a given tick if not set the default
            try:
                tick = int(self.request.get('tick'))
            except:
                tick = 60

            ## Get and echo the relevant peers
            plist = Peer.all().filter('tracker =',tracker).filter('datetime >',datetime.now() - timedelta(seconds=tick))
            for peer in plist:
                if peer.address != self.request.remote_addr:
                    self.response.out.write(peer.address+"\n")
        else:
            self.response.out.write('Tracker must contain only numbers, letters and the underscore, it must also be between 3 and 25 charachters')

class CleanHandler(webapp.RequestHandler):
    def get(self):
        ## remove any old peers
        plist = Peer.all().filter('datetime <',datetime.now() - timedelta(days=1))
        peercount = plist.count()
        for p in plist:
            p.delete()

        ## remove any empty trackers
        trackers = Tracker.all()
        trackercount = 0
        for tracker in trackers:
            p = Peer.all().filter('tracker =',tracker).order('-datetime').get()
            if p == None:
                tracker.delete()
                trackercount += 1

        ## some simple stats
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("Cleaned %d trackers and %d peers"%(trackercount,peercount))
        if trackercount and peercount:
            logging.info("Cleaned %d trackers and %d peers"%(trackercount,peercount))


def main():
    ## Set up logging, ready for cleaning
    logging.getLogger().setLevel(logging.DEBUG)

    ## Set Up URLS
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/trk/(.*?)/?', TrackerHandler),
                                          ('/clean/', CleanHandler)],
                                         debug=True)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
