"""
Changelog 20160310:
    add error checking on internet connection
"""

import httplib
import urllib

# write to thingspeak, use thingspeak.py from github/bergey
__version__ = '0.1.1'

headers = {"Content-type": "application/x-www-form-urlencoded",
           "Accept": "text/plain"}

write_API_key = "4GYDGFROYDSPP5U6"
read_API_key = "6VUSLI8ATJTAKYSF"
channel_ID = "114474"

def non_null_values(**kwargs):
    return [(k, v) for (k, v) in kwargs.iteritems() if v is not None]


class TooManyFields(ValueError):
    pass


class channel(object):
    def __init__(self, write_key = write_API_key):
        """write_key is the Write API Key.
        cid is the read_key"""
        self.write_key = write_key

    def update(self, field_ids, field_vals, lat=None, lon=None,
               elevation=None, status=None):
        if len(field_vals) > 8:
            raise TooManyFields('update can only handle 8 field/channel')
        if len(field_ids) != len(field_vals):
            raise TooManyFields('fields and value number not match')

        field_keys = ['field' + str(n) for n in field_ids]
        """ this verbosity, rather than just using kwargs,
        so that callers get a prompt error if they supply
        an arg `update` cannot handle"""
        named_args = non_null_values(lat=lat, lon=lon,
                                     elevation=elevation, status=status)
        params = urllib.urlencode(zip(field_keys, field_vals) +
                                  [('key', self.write_key)] + named_args)
        conn = httplib.HTTPConnection("api.thingspeak.com:80")
        # check if have internet connection to thingspeak
        try:
            conn.request("POST", "/update", params, headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()
        except:
            print "Connection error"
            response = None
            conn.close()

        return response

    def fetch(self, format):
        """ not yet used """
        conn = httplib.HTTPConnection("api.thingspeak.com:80")
        path = "/channels/{0}/feed.{1}".format(self.cid, format)
        params = urllib.urlencode([('key', self.key)])
        conn.request("GET", path, params, headers)
        response = conn.getresponse()
        return response
