import base64
import Cookie

import jwt
from werkzeug.exceptions import BadRequest, Unauthorized


def get_bearer(env):
    # Bearer info can be in two different locations.  Either in the Authorization
    # header or as part of the cookie.  The Authorization header takes precedence
    # if both are set.
    bearer = env.get('HTTP_AUTHORIZATION')
    if not bearer:
        cookiestr = env.get('HTTP_COOKIE')
        if not cookiestr:
            raise Unauthorized()
        cookie = Cookie.SimpleCookie(cookiestr)
        bearer = cookie.get('Bearer').value.decode('utf-8')
    else:
        # Verify that the value of HTTP_AUTHORIZATINO is
        # Bearer <jwt>
        if not bearer.startswith('Bearer '):
            raise BadRequest()
        bearer = bearer.split(' ')[1].decode('utf-8')

    return bearer


def get_user_claims(env):
    bearer = get_bearer(env)
    return jwt.decode(bearer, env['WEB_PUBLIC_KEY'], algorithms='RS256')


class Response(object):
    """ The WebResponse object is a serializable representation of
    a response to an http(s) client request that can be transmitted
    through the RPC subsystem to the appropriate platform's MasterWebAgent
    """

    def __init__(self, content=None, status=None,  headers=None, mimetype=None,
                 content_type=None):
        self._content = content
        self._status = status
        if not self._status:
            self._status = '200 OK'
        self._headers = headers
        if not self._headers:
            self._headers = {}
        self._mimetype = mimetype
        self._contenttype = content_type
        if not self._contenttype:
            self._contenttype = 'text/html'

    @property
    def status(self):
        return self._status

    @property
    def headers(self):
        cpy = self._headers.copy()
        values = [(k, v) for k, v in cpy.items()]
        values.append(('Content-Type', self._contenttype))
        return values

    @property
    def content(self):
        return self._content

    def add_header(self, key, value):
        if key in self._headers:
            raise ValueError("key {} already exists in header.".format(key))

        self._headers[key] = value

    def process_data(self, data):
        if type(data) == bytes:
            self.base64 = True
            data = base64.b64encode(data)
        elif type(data) == str:
            self.base64 = False
        else:
            raise TypeError("Response data is neither bytes nor string type")
        return data
