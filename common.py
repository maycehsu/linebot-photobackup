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

import sys
import os
import re
from subprocess import Popen, PIPE
import flickrapi
#flickr_api_filename = os.path.join(os.environ['HOME'],'.flickr-api')
flickr_api_filename = '.flickr-api'
if not os.path.exists(flickr_api_filename):
    print "You must put your Flickr API key and secret in "+flickr_api_filename

configuration = {}
for line in open(flickr_api_filename):
    if len(line.strip()) == 0:
        continue
    m = re.search('\s*(\S+)\s*=\s*(\S+)\s*$',line)
    if m:
        configuration[m.group(1)] = m.group(2)
    if not m:
        print "Each line of "+flickr_api_filename+" must be either empty"
        print "or of the form 'key = value'"
        sys.exit(1)
    continue

if not ('api_key' in configuration and 'api_secret' in configuration):
    print "Both api_key and api_secret must be defined in "+flickr_api_filename

#flickr = flickrapi.FlickrAPI(configuration['api_key'],configuration['api_secret'], token_cache_location='.')

def md5sum(filename):
    return checksum(filename,"md5")

def sha1sum(filename):
    return checksum(filename,"sha1")

def checksum(filename,type):
    result = Popen([type+"sum",filename],stdout=PIPE).communicate()[0]
    m = re.search('^('+checksum_pattern+')',result.strip())
    if not m:
        raise Exception, "Output from "+type+"sum was unexpected: "+result
    return m.group(1)

checksum_pattern = "[0-9a-f]{32,40}"

md5_machine_tag_prefix = "checksum:md5="
sha1_machine_tag_prefix = "checksum:sha1="

def base58(n):
    a='123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
    bc=len(a)
    enc=''
    while n >= bc:
        div, mod = divmod(n,bc)
        enc = a[mod]+enc
        n = div
    enc = a[n]+enc
    return enc

def short_url(photo_id):
    encoded = base58(int(photo_id,10))
    return "http://flic.kr/p/%s" % (encoded,)

def flickr_is_authorized():
  
    if flickr.token_valid(perms='write'):
        return True
    else:
        return False
def flickr_get_authorize_url():
    
    if not flickr.token_valid(perms='write'):
        print 'get_request_token'
        # Get a request token
        flickr.get_request_token(oauth_callback=u'oob')
        print 'get auth_url'
        # Open a browser at the authentication URL. Do this however
        # you want, as long as the user visits that URL.
        authorize_url = flickr.auth_url(perms=u'write')
        #webbrowser.open_new_tab(authorize_url)
        print 'authorize_url=', authorize_url
        return authorize_url
    else:
        print 'Authorized'
        
def flickr_get_access_token(verifier):
    # Trade the request token for an access token
    return flickr.get_access_token(verifier)

def flickr_get_username():
    return flickr.token_cache.token.username
