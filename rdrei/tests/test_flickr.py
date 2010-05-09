from rdrei.utils import flickr
from rdrei.settings import FLICKR_API_KEY
from nose.tools import eq_


TEST_USER_ID = '80007380@N00'


def test_api():
    client = flickr.FlickrClient(FLICKR_API_KEY)

    result = client.flickr_people_getInfo(user_id=TEST_USER_ID)
    eq_(result['person']['username']['_content'], 'Cravior')

def test_recent():
    photo_counter = 0
    for photo in flickr.get_recent_profile_photos(TEST_USER_ID, per_page=10,
                                                  max_photos=10):
        photo_counter += 1
        assert 'title' in photo
        assert 'tags' in photo

    eq_(photo_counter, 10)
