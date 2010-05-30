# -*- coding: utf-8 -*-
"""
rdrei.utils.disqus
~~~~~~~~~~~~~~~~~~

Utilities for accessing the Disqus API.

:copyright: 2010, Pascal Hartig <phartig@rdrei.net>
:license: GPL v3, see doc/LICENSE for more details.
"""

from rdrei import settings
from rdrei.utils.thirdparty.disqus import DisqusService


def get_service():
    service = DisqusService()
    service.login(settings.DISQUS_USER_API_KEY)
    return service


def get_num_posts_by_identifier(identifier, title="Discussion"):
    """
    Returns the number of posts for a given thread by its
    identifier.
    """

    service = get_service()
    forums = service.get_forum_list()

    # Iterate through all forums to find our entry and stop at the first
    # match.
    for forum in forums:
        result = service.thread_by_identifier(forum, title, identifier)
        thread = result['thread']

        num_result = service.get_num_posts(forum, [thread])
        visible, total = num_result[thread.id]
        if visible > 0:
            return visible

    return 0
