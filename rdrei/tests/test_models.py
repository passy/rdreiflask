from rdrei.models import Photos
from rdrei.utils import redis_db
from rdrei.application import app
from flask import g


class TestPhotos(object):
    """Tests the Photos model."""

    def __init__(self):
        """Initializes the redis db."""

        self.app = app.test_client()

    def test_basic_query(self):
        """Tests a basic photo query."""

        self.app.get('/')
        counter = 0
        for photo in Photos.by_tag("strand050708"):
            counter += 1

        assert counter > 0, "No photos yielded."
