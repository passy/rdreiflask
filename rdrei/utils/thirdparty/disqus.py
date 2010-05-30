#:coding=utf8:

"""
disqus-api-client

A disqus api client for python.
"""

import simplejson
import httplib
import urllib
import datetime

HOST = "disqus.com"
BASE_URL = "/api/%s/"

REQUEST_METHODS = {
    "create_post": "POST",
    "get_forum_list": "GET",
    "get_forum_api_key": "GET",
    "get_thread_list": "GET",
    "get_num_posts": "GET",
    "get_thread_by_url": "GET",
    "get_thread_posts": "GET",
    "thread_by_identifier": "POST",
    "update_thread": "POST",
}

def date_to_string(d):
    return "%04d-%02d-%02dT%02d:%02d" % (
        d.year,
        d.month,
        d.day,
        d.hour,
        d.minute,
    )

def string_to_date(date):
    return datetime.datetime.strptime(date, r"%Y-%m-%dT%H:%M")

class APIError(Exception):
    pass

class DisqusService(object):
    _debug = False

    def login(self, api_key):
        self.user_api_key = api_key

    def create_post(self,
                    forum,
                    thread,
                    message,
                    author_name,
                    author_email,
                    parent_post=None,
                    created_at=None,
                    author_url=None):
        """
        Key: Forum Key
        Method: POST
        Arguments:
            Required:
                "thread_id": the thread to post to
                "message": the content of the post
                "author_name": the post creator's name
                "author_email": their email address.
            Optional:
                "parent_post": the id of the parent post
                "created_at": the UTC date this post was created in the format
                              %Y-%m-%dT%H:%M (the current time will be used by
                              default)
                "author_url": the author's homepage; and "ip_address", their
                              IP address.

        Action: Creates a new post on the thread. Does not check against spam
                filters or ban list. This is intended to allow automated
                importing of comments.

        Result: The post object just created. See "Object Formats" header below
                for details on post objects.
        """
        params = {
            "forum_api_key": forum.api_key,
            "thread_id": thread.id,
            "message": message,
            "author_name": author_name,
            "author_email": author_email,
        }
        if parent_post:
            params["parent_post"] = parent_post
        if created_at:
            params["created_at"] = date_to_string(created_at)
        if author_url:
            params["author_url"] = author_url
        resp = self._http_request("create_post", params)
        return self._decode_post(forum, thread, resp)

    def get_forum_list(self):
        """
        Key: User Key
        Arguments: None.

        Result: A list of objects representing all forums the user owns. The
                user is determined by the API key. See "Object Formats" header
                below for details on forum objects.
        """
        resp = self._http_request("get_forum_list")
        return [self._decode_forum(f) for f in resp]

    def get_user_api_key(self):
        if getattr(self, "user_api_key",None) is None:
            raise Exception("Please login")
        return self.user_api_key

    def get_forum_api_key(self, forum):
        """
        Key: User Key
        Arguments: "forum_id", the unique id of the forum.

        Result: A string which is the Forum Key for the given forum.
        """
        return self._http_request("get_forum_api_key", { "forum_id":forum.id })

    def get_thread_list(self, forum, limit=25, start=0):
        """
        Key: Forum Key
        Arguments: None.

        Result: A list of objects representing all threads belonging to the
                given forum. See "Object Formats" for details on thread
                objects.
        """
        resp = self._http_request("get_thread_list", {
            "forum_api_key": forum.api_key,
            "user_api_key": self.get_user_api_key(),
            "forum_id": forum.id,
            "start": start,
            "limit": limit
        })
        return [self._decode_thread(forum, t) for t in resp]

    def get_num_posts(self, forum, threads):
        """
        Key: Forum Key
        Arguments: "thread_ids": a comma-separated list of thread IDs belonging
                                 to the given forum.

        Result: An object mapping each thread_id to a list of two numbers. The
                first number is the number of visible comments on on the
                thread; this would be useful for showing users of the site
                (e.g., "5 Comments"). The second number is the total number of
                comments on the thread. These numbers are different because
                some forums require moderator approval, some messages are
                flagged as spam, etc.
        """
        resp = self._http_request("get_num_posts", {
            "forum_api_key": forum.api_key,
            "thread_ids": ",".join([thread.id for thread in threads]),
        })
        return resp

    def get_thread_by_url(self, forum, url):
        """
        Key: Forum Key
        Arguments: "url", the URL to check for an associated thread.

        Result: A thread object if one was found, otherwise null. Only finds
                threads associated with the given forum. Note that there is
                no one-to-one mapping between threads and URLs: a thread will
                only have an associated URL if it was automatically created by
                Disqus javascript embedded on that page. Therefore, we
                recommend using thread_by_identifier whenever possible, and
                this method is provided mainly for handling comments from
                before your forum was using the API.
        """
        resp = self._http_request("get_thread_by_url", {
            "forum_api_key": forum.api_key,
            "url": url,
        })
        return self._decode_thread(forum, resp)

    def get_thread_posts(self, forum, thread):
        """
        Key: Forum Key
        Arguments: "thread_id": the ID of a thread belonging to the given
                                forum.

        Result: A list of objects representing all posts belonging to the
                given forum. See "Object Formats" for details on post objects.
        """
        resp = self._http_request("get_thread_posts", {
            "forum_api_key": forum.api_key,
            "thread_id": thread.id
        })
        return [self._decode_post(forum, thread, post) for post in resp]

    def thread_by_identifier(self, forum, title, identifier):
        """
        Key: Forum Key
        Method: POST
        Arguments: "title": the title of the thread to possibly be created
                   "identifier": a string of your choosing (see Action).

        Action: Create or retrieve a thread by an arbitrary identifying string
                of your choice. For example, you could use your local
                database's ID for the thread. This method allows you to
                decouple thread identifiers from the URLs on which they might
                be appear. (Disqus would normally use a thread's URL to
                identify it, which is problematic when URLs do not uniquely
                identify a resource.) If no thread yet exists for the given
                identifier (paired with the forum), one will be created.

        Result: An object with two keys:
                    "thread": which is the thread object corresponding to the
                              identifier
                    "created": which indicates whether the thread was created
                               as a result of this method call. If created, it
                               will have the specified title.
        """
        resp = self._http_request("thread_by_identifier", {
            "forum_api_key": forum.api_key,
            "title": title,
            "identifier": identifier,
        })
        return {
            "thread": self._decode_thread(forum, resp["thread"]),
            "created": resp["created"],
        }

    def update_thread(self,
                      forum,
                      thread,
                      title=None,
                      slug=None,
                      url=None,
                      allow_comments=None):
        """
        Key: Forum Key
        Method: POST
        Arguments:
            Required:
                "thread_id": the ID of a thread belonging to the given forum.
            Optional:
                any of "title", "slug", "url", and "allow_comments".

        Action: Sets the provided values on the thread object. See Object
                Formats for field meanings.

        Result: An empty success message.
        """
        params = {
            "forum_api_key": forum.api_key,
            "thread_id": thread.id,
        }
        if title:
            params["title"] = title
        if slug:
            params["slug"] = slug
        if url:
            params["url"] = url
        if allow_comments is not None:
            params["allow_comments"] = 1 if allow_comments else 0
        resp = self._http_request("update_thread", params)

    def set_debug(self, debug):
        self._debug = debug

    def _http_request(self, method_name, data={}, user_key_required=True):
        if user_key_required:
            data["user_api_key"] = self.get_user_api_key()

        method = REQUEST_METHODS[method_name]

        con = httplib.HTTPConnection(HOST)

        if 'api_version' not in data:
            data['api_version'] = u'1.1'

        # Make sure data is in encoded string format for urllib
        for d in data:
            if type(data[d]) == unicode:
                data[d] = data[d].encode("utf8")

        if method == 'GET':
            url = (BASE_URL +"?%s") % (method_name, urllib.urlencode(data))

            if self._debug:
                print method, url

            con.request(method, url)
        else:

            url = BASE_URL % method_name

            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "application/json; text/plain",
            }

            params = urllib.urlencode(data)

            if self._debug:
                print method, url
                print params

            con.request(method, url, params, headers)

        resp = con.getresponse()
        if resp.status > 200:
            raise APIError("%s: %s" % (resp.status, resp.reason))

        if self._debug:
            resp_data = resp.read()
            print resp.status
            print resp_data
            return self._decode_response(simplejson.loads(resp_data))
        else:
            return self._decode_response(simplejson.load(resp))

    def _decode_response(self, dct):
        if dct.get("code") == "ok" and dct.get("succeeded"):
            return dct.get("message")
        else:
            raise APIError("%s: %s" % (dct.get("code"), dct.get("message")))

    def _decode_forum(self, dct):
        if self._debug:
            print "decode_forum: %r" % dct
        if not dct:
            return None
        return Forum(
            service=self,
            id=dct.get("id"),
            shortname=dct.get("shortname"),
            name=dct.get("name"),
        )

    def _decode_thread(self, forum, dct):
        if self._debug:
            print "decode_thread: %r" % dct
        if not dct:
            return None
        return Thread(
            service=self,
            id=dct.get("id"),
            forum=forum,
            slug=dct.get("slug"),
            title=dct.get("title"),
            created_at=string_to_date(dct.get("created_at")),
            #created_at=dct.get("created_at"),
            allow_comments=dct.get("allow_comments"),
            url=dct.get("url"),
            identifier=dct.get("identifier"),
        )

    def _decode_post(self, forum, thread, dct):
        if self._debug:
            print "decode_post: %r" % dct
        if not dct:
            return None
        return Post(
            id=dct.get("id"),
            forum=forum,
            thread=thread,
            created_at=string_to_date(dct.get("created_at")),
            message=dct.get("message"),
            parent_post_id=dct.get("parent_post"),
            shown=dct.get("shown"),
            is_anonymous=dct.get("is_anonymous"),
            anonymous_author=self._decode_anonymous_author(dct.get("anonymous_author")),
            author=self._decode_author(dct.get("author")),
        )

    def _decode_author(self, dct):
        if self._debug:
            print "decode_author: %r" % dct
        if not dct:
            return None
        return Author(
            id=dct.get("id"),
            username=dct.get("username"),
            display_name=dct.get("display_name"),
            url=dct.get("url"),
            email_hash=dct.get("email_hash"),
            has_avatar=dct.get("has_avatar"),
        )

    def _decode_anonymous_author(self, dct):
        if self._debug:
            print "decode_anonymous_author: %r" % dct
        if not dct:
            return None
        return AnonymousAuthor(
            name=dct["name"],
            url=dct["url"],
            email_hash=dct["email_hash"],
        )

class Forum(object):
    """
    id field: a unique alphanumeric string identifying this Forum object.
    shortname: the unique string used in disqus.com URLs relating to this
               forum. For example, if the shortname is "bmb", the forum's
               community page is at http://bmb.disqus.com/.
    name: a string for displaying the forum's full title,
          like "The Eyeball Kid's Blog".
    """
    def __init__(self, service, id, shortname, name):
        self.service = service
        self.id = id
        self.shortname = shortname
        self.name = name
        self._api_key = None
        self._threads = None

    def _get_api_key(self):
        if self._api_key is None:
            self._api_key = self.service.get_forum_api_key(self)
        return self._api_key
    api_key = property(_get_api_key)

    def get_thread_list(self):
        if self._threads is None:
            self._threads = self.service.get_thread_list(self)
        return self._threads

    def get_thread_by_url(self, url):
        if self._threads is not None:
            for thread in self._threads:
                if thread.url == url:
                    return thread
        return self.service.get_thread_by_url(self, url)

    def __str__(self):
        return ("%s object: '%s'" % (
            self.__class__.__name__,
            self.name,
        )).encode('utf-8')

class Thread(object):
    """
    id: a unique alphanumeric string identifying this Thread object.
    forum: the id for the forum this thread belongs to.
    slug: the per-forum-unique string used for identifying this thread in
          disqus.com URLs relating to this thread. Composed of
          underscore-separated alphanumeric strings.
    title: the title of the thread.
    created_at: the UTC date this thread was created, in the format
                %Y-%m-%dT%H:%M.
    allow_comments: whether this thread is open to new comments.
    url: the URL this thread is on, if known.
    identifier: the user-provided identifier for this thread, as in
                thread_by_identifier above (if available)
    """
    def __init__(self,
                 service,
                 id,
                 forum,
                 slug,
                 title,
                 created_at,
                 allow_comments,
                 url,
                 identifier):
        self.service = service
        self.id = id
        self.forum = forum
        self.slug = slug
        self.title = title
        self.created_at = created_at
        self.allow_comments = allow_comments
        self.url = url
        self.identifier = identifier

        self._num_visible_posts = None
        self._num_total_posts = None
        self._posts = None

    def _get_num_posts(self):
        data = self.service.get_num_posts(self.forum, [self])
        self._num_visible_posts = data[self.id][0]
        self._num_total_posts = data[self.id][1]

    def _get_visible_posts(self):
        if self._num_visible_posts is None:
            self._get_num_posts()
        return self._num_visible_posts

    num_visible_posts = property(_get_visible_posts)

    def _get_total_posts(self):
        if self._num_total_posts is None:
            self._get_num_posts()
        return self._num_total_posts

    num_total_posts = property(_get_total_posts)

    def _get_posts(self):
        if self._posts is None:
            self._posts = self.service.get_thread_posts(self.forum, self)
        return self._posts

    posts = property(_get_posts)

    def create_post(self,
                    message,
                    author_name,
                    author_email,
                    parent_post=None,
                    created_at=None,
                    author_url=None):

        if type(parent_post) == Post:
            parent_post = parent_post.id

        post = self.service.create_post(
            self.forum,
            self,
            message,
            author_name,
            author_email,
            parent_post,
            created_at,
            author_url,
        )
        # Append the new post to the posts
        # list if we've gotten it.
        if self._posts is not None:
            self._posts.append(post)
        return post

    def update(self):
        self.service.update_thread(
            self.forum,
            self,
            self.title,
            self.slug,
            self.url,
            self.allow_comments,
        )

    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id

    def __str__(self):
        return ("%s object: '%s'" % (
            self.__class__.__name__,
            self.title,
        )).encode('utf-8')

class Post(object):
    def __init__(self,
                 id,
                 forum,
                 thread,
                 created_at,
                 message,
                 parent_post_id,
                 shown,
                 is_anonymous=False,
                 anonymous_author=None,
                 author=None):
        """
        id: a unique alphanumeric string identifying this Post object.
        forum: the id for the forum this post belongs to.
        thread: the id for the thread this post belongs to.
        created_at: the UTC date this post was created, in the format %Y-%m-%dT%H:%M.
        message: the contents of the post, such as "First post".
        parent_post: the id of the parent post, if any
        shown: whether the post is currently visible or not.
        is_anonymous: whether the comment was left anonymously, as opposed to a
                      registered Disqus account.
        anonymous_author: An AnoymousAuthor object. Present only when is_anonymous is true.
        author: Author object. Present only when is_anonymous is false. An object containing these fields:

        """
        self.id = id
        self.forum = forum
        self.thread = thread
        self.created_at = created_at
        self.message = message
        self._parent_post_id = parent_post_id
        self._parent_post = None
        self.shown = shown
        self.is_anonymous = is_anonymous
        if self.is_anonymous:
            self.anonymous_author = anonymous_author
            self.author = None
        else:
            self.author = author
            self.anonymous_author = None

    def _get_parent_post(self):
        if self._parent_post_id and self._parent_post is None:
            for post in self.thread.posts:
                if self._parent_post_id == post.id:
                    self._parent_post = post
        return self._parent_post

    def _set_parent_post(self, post):
        self._parent_post = post

    parent_post = property(_get_parent_post, _set_parent_post)

    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id

    def __str__(self):
        return ("%s object: '%s'" % (
            self.__class__.__name__,
            self.message[:15]+'...' if len(self.message) > 15 else self.message,
        )).encode('utf-8')


class Author(object):
    def __init__(self,
                 id,
                 username,
                 display_name,
                 url,
                 email_hash,
                 has_avatar):
        """
        id: the unique id of the commenter's Disqus account
        username: the author's username
        display_name: the author's full name, if provided
        url: their optionally provided homepage
        email_hash: md5 of the author's email address
        has_avatar: whether the user has an avatar on disqus.com
        """
        self.id = id
        self.username = username
        self.display_name = display_name
        self.url = url
        self.email_hash = email_hash
        self.has_avatar = has_avatar

    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id

    def __str__(self):
        return ("%s object: '%s'" % (
            self.__class__.__name__,
            self.display_name,
        )).encode('utf-8')

class AnonymousAuthor(object):
    def __init__(self,
                 name,
                 url,
                 email_hash):
        """
        name: the display name of the commenter
        url: their optionally provided homepage
        email_hash: md5 of the author's email address
        """
        self.name = name
        self.url = url
        self.email_hash = email_hash

    def __eq__(self, other):
        return type(self) == type(other) and self.email_hash == other.email_hash

    def __str__(self):
        return ("%s object: '%s'" % (
            self.__class__.__name__,
            self.name,
        )).encode('utf-8')
