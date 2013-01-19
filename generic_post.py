#!/usr/bin/python

import urllib
import urllib2
import sys

url = "YOUR_UPLOAD_URL"


if len(sys.argv) == 1:
    data = {'note' : sys.stdin.read()}

elif len(sys.argv) == 2:
    if sys.argv[1] == '-':
        data = {'note' : sys.stdin.read()}
    else:
        data = {'note' : open(sys.argv[1]).read()}

elif len(sys.argv) == 3:
    if sys.argv[1] == '-':
        data = {sys.argv[2] : sys.stdin.read()}
    else:
        data = {sys.argv[2] : open(sys.argv[1]).read()}

elif len(sys.argv) > 3:
    data = {}
    for f in sys.argv[1:]:
        data[f] = open(f).read()


req = urllib2.Request(url, urllib.urlencode(data), {})

response = urllib2.urlopen(req)

headers = response.headers.headers

data = response.read()

print data

