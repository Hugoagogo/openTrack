About
openTrack is a simple Tracker that can be used for connecting peers in a P2P program
It is written using python to be run on Google App Engine and can be found at
http://open-track.appspot.com/

Example
To use the tracker visit
http://open-track.appspot.com/trk/<tracker name>
The tracker does not need to be setup beforhand It will return a list of IP adresses that have visited that tracker and add yours to the list
Optionally add "?tick=" to the url where seconds is how recently it has been visited the default tick is 60 seconds

NEW: http://open-track.appspot.com/tick/<tracker name>
provides a way of refreshing yourself in a tracker without retrieveing a list
