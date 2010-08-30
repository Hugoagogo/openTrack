#!/usr/bin/env python
#
# openTrack
#
#     http://www.importsoul.net/
#
from google.appengine.ext import db

class Tracker(db.Model):
    name = db.StringProperty()

class Peer(db.Model):
    tracker = db.ReferenceProperty(reference_class=Tracker,collection_name="peer_list")
    address = db.StringProperty()
    datetime = db.DateTimeProperty(auto_now=True)
