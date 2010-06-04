# -*- coding: utf-8 -*-
"""
rdrei.utils.flickr
~~~~~~~~~~~~~~~~~~

Some utils to access the flickr api easily.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

import simplejson
import re
from rdrei.settings import FLICKR_USER_ID, FLICKR_API_KEY
from urllib import urlencode
from urllib2 import urlopen


class FlickrClient(object):
    """Easy access to the flickr API."""

    HOST = "http://flickr.com"
    PATH = "/services/rest/"

    def __init__(self, api_key):
        self.api_key = api_key

    def __getattr__(self, method):
        """
        Allows direct access on the client an returns a decoded json
        object.
        """
        def _inner(**params):
            _method = method.replace("_", ".")
            url = ("{host}{path}?method={method}&{params}&format=json"
                  "&api_key={api_key}"
                    .format(
                        host=self.HOST,
                        path=self.PATH,
                        method=_method,
                        params=urlencode(params),
                        api_key=self.api_key))
            # This might raise exceptions based on network state.
            response = urlopen(url).read()
            return self._parse_response(response)
        return _inner

    def _parse_response(self, response):
        """
        Watches for failures in the response and decodes the json
        object.
        """

        # flickr returns JSONP what is not what we want, so we strip of the
        # leading 'jsonFlickrApi(' and the trailing ')'.
        data = simplejson.loads(response[14:-1])
        if data['stat'] == 'fail':
            raise FlickrError(data['err']['code'], data['err']['msg'])

        return data


_ORIGINAL_SECRET_RE = re.compile(
    r'^http:\/\/farm\d+\.static.flickr.com\/\d+/\d+_([a-z0-9]+)_o\.jpg')


def _extract_original_secret(url_o):
    """Extracts the secret for the original photo."""

    return _ORIGINAL_SECRET_RE.match(url_o).group(1)


def get_recent_profile_photos(user_id=FLICKR_USER_ID, max_photos=500,
                              per_page=50):
    """
    Yields a generator over the most recent photos for ``user_id``.
    """

    page_index = 1
    client = FlickrClient(FLICKR_API_KEY)

    while page_index * per_page <= max_photos:
        photos = client.flickr_people_getPublicPhotos(
            user_id=user_id,
            page=page_index,
            per_page=per_page,
            extras='tags,url_o,url_m,o_dims')

        assert 'photos' in photos, "Invalid flickr response"

        for photo in photos['photos']['photo']:
            # flickr is weird with this stuff. For no obvious reasons it
            # sometimes includes the original format URLs, sometimes not. The
            # problem with this is, that without the url, there are no
            # dimension information available.
            if 'url_o' in photo:
                photo['original_secret'] = _extract_original_secret(
                    photo['url_o'])
                del photo['url_o']

            del photo['url_m']
            yield photo

        page_index += 1
        if page_index > photos['photos']['pages']:
            # No more photos to fetch.
            break
