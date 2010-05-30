# -*- coding: utf-8 -*-
"""
rdrei.tests.disqus
~~~~~~~~~~~~~~~~~~

Tests the disqus utility functions.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from rdrei.utils.disqus_utils import get_num_posts_by_identifier, \
        get_service


def test_num_posts():
    """Tests the num posts function."""

    # We assume our test comment does not get removed.
    result = get_num_posts_by_identifier("photo:2765703772")
    assert result > 0, "No comment found!"


def test_latest_posts():
    """Tests the API to get the most recent post."""

    service = get_service()
    service.set_debug(True)
    forum = service.get_forum_list()[0]
    threads = forum.get_thread_list()
    assert(len(threads) > 1)
