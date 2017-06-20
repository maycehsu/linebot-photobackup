#!/usr/bin/env python2.7

# Copyright 2009 Mark Longair

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This depends on a couple of packages:
#   apt-get install python-pysqlite2 python-flickrapi

import os
import sys
import re
import xml
import tempfile
from subprocess import call, Popen, PIPE
import flickrapi
from optparse import OptionParser
from common import *

'''
command example
Upload with tags and verbose output
python flickr-upload.py -v -g aa,bb,cc -u eason 00001.jpg

Get authorize URL
python flickr-upload.py -a -u eason

Authorize with verifier code
python flickr-upload.py -a -c 000-000-001 -u eason


'''

def print_out(*args, **kargs):
    
    if 'verbose' in kargs:
        verbose = kargs['verbose']
    else:
        verbose = False
    if options.verbose or verbose:
        output=u''
        for arg in args:
            if not output:
                output=unicode(arg)
            else:
                if type(arg) is unicode:
                    output = output+u' '+arg
                else:
                    output = output+u' '+unicode(arg)
    
        print output
        
parser = OptionParser(usage="Usage: %prog [OPTIONS] [FILENAME]")
parser.add_option('--public', dest='public', default=False, action='store_true',
                  help='make the image viewable by anyone')
parser.add_option('--family', dest='family', default=False, action='store_true',
                  help='make the image viewable by contacts marked as family')
parser.add_option('--friends', dest='friends', default=False, action='store_true',
                  help='make the image viewable by contacts marked as friends')
parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                  help='verbose output')
parser.add_option('-a', '--authorize', dest='authorize', default=False, action='store_true',
                  help='authorize flickr')
parser.add_option('-c', '--verifier', dest='verifier', metavar='VERIFIER',
                  help='verifier code for authorization')
parser.add_option('-t', '--title', dest='title',
                  metavar='TITLE',
                  help='set the title of the photo')
parser.add_option('-g', '--tags', dest='tags',
                  metavar='TAGS',
                  help='set the tags of the photo')


options,args = parser.parse_args()

date_pattern = '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
date_error_message = 'must be of the form "YYYY-MM-DD HH:MM:SS'


if not 1 == len(args) and not options.authorize:
    print "No filename to upload supplied:"
    parser.print_help()
    sys.exit(1)

flickr = flickrapi.FlickrAPI(configuration['api_key'],configuration['api_secret'], token_cache_location='.')

if options.authorize:
    if not flickr.token_valid(perms='write'):
    
        # Get a request token
        flickr.get_request_token(oauth_callback=u'oob')

        # Open a browser at the authentication URL. Do this however
        # you want, as long as the user visits that URL.
        
        authorize_url = flickr.auth_url(perms=u'write')
        #webbrowser.open_new_tab(authorize_url)
        
        print_out(authorize_url, verbose=True)
            
        # Get the verifier code from the user. Do this however you
        # want, as long as the user gives the application the code.
        
        verifier = unicode(raw_input('Verifier code: '))
        
        
        # Trade the request token for an access token
        try:
            flickr.get_access_token(verifier)
        
            if flickr.token_valid(perms='write'):
                print_out('Success', verbose=True)
            else:
                print_out('Fail', verbose=True)
            
            
        except flickrapi.exceptions.FlickrError:
            print_out('Fail', verbose=True)
            
        
    else:
        print_out('Success', verbose=True)
    
    exit(0)

if not flickr.token_valid(perms='write'):
    print 'No valid flickr user authorized, use -a to authorize first, exit..'
    exit(0)
        
'''

(token, frob) = flickr.get_token_part_one(perms='write')
if not token:
    raw_input("Press 'Enter' after you have authorized this program")
flickr.get_token_part_two((token, frob))
'''
def progress(percent,done):
    if done and options.verbose:
        print_out("Finished.")
    elif options.verbose:
        print_out(""+str(int(round(percent)))+"%")

real_sha1 = sha1sum(args[0])
real_md5 = md5sum(args[0])

tags = sha1_machine_tag_prefix + real_sha1 + " " + md5_machine_tag_prefix + real_md5

if options.tags:
    add_tags=options.tags.split(',')
    for tag in add_tags:
        tags+=" "+tag
    
    print_out("Tags: ", tags)
    
result = flickr.upload(filename=args[0],
                       callback=progress,
                       title=(options.title or os.path.basename(args[0])),
                       tags=tags,
                       is_public=int(options.public),
                       is_family=int(options.family),
                       is_friend=int(options.friends))

photo_id = result.getchildren()[0].text
if options.verbose:
    print_out("photo_id of uploaded photo: "+str(photo_id))
    print_out("Uploaded to: "+short_url(photo_id))

