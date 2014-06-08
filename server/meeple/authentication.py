"""
Generic reservables table
"""

import meeple
import time
from flask import request
from user import User

import time
from flask import request
from settings import token_pub
import datetime
import jwt
import Crypto.PublicKey.RSA as RSA
from api_tools import date_format

def session_expiration(token):
    pub_key = RSA.importKey(token_pub)
    try:
        header, claims = jwt.verify_jwt(token, pub_key)
        ts = claims["exp"]
        return date_format(datetime.datetime.utcfromtimestamp(ts))
    except ValueError:
        return date_format(datetime.datetime.utcfromtimestamp(0))

def extract_authorization_token():
    if 'Authorization' in request.headers:
        if request.headers['Authorization'].startswith('meepleToken'):
            token = request.headers['Authorization'].split(' ')[1].strip()
            return str(token) #bug? This returns as unicode.. needs to be string for jwt_verify?
    return None

def authenticated_user():

    from user import User
    # Check for basic auth
    auth = request.authorization
    if auth is not None:
        user = User.from_credentials(auth['username'], auth['password'])
        if user is not None:
            return user
        raise Exception("Basic Authentication")
    else:
        token = extract_authorization_token()
        if token is not None:
            pub_key = RSA.importKey(token_pub)
            try:
                header, claims = jwt.verify_jwt(token, pub_key)
            except ValueError:
                raise Exception("Invalid Token")

            user_id = None
            ip = None
            if 'user_id' in claims:
                user_id = claims['user_id']
            if 'ip' in claims:
                ip = claims['ip']
            if user_id is None:
                raise Exception("Invalid Token")
            if str(ip) == str(request.remote_addr):
                return User.query.filter(User.user_id == user_id).first()
            raise Exception("Token Authentication")
    raise Exception("Unkown Authentication")

def check_authentication():
    """
    Authenticate an HTTP request, returning a user if authenticated or None if not.
    """

    #TODO: Reservation based authentication
    try:
        authenticated_user()
    except Exception as e:
        return e

    return True


def ipthrottle(fn):
    def decorator(*args, **kwargs):

        LIMIT = 50
        TIMELIMIT = 60

        # No remote address in testing (unless we set it to test this)
        if request.remote_addr is None:
            return fn(*args, **kwargs)

        counter = "meeple:ipthrottle:"+request.remote_addr
        num = meeple.r.llen(counter)

        if num < LIMIT:
            meeple.r.lpush(counter, time.time())
            meeple.r.expire(counter, 120)
            return fn(*args, **kwargs)
        else:
            t = float(meeple.r.lindex(counter, -1))
            if time.time() - t <= TIMELIMIT:
                import api_tools
                return api_tools.api_error("Slow down buddy", status=429)
            else:  # pragma: no cover
                meeple.r.lpush(counter, time.time())
                meeple.r.rpop(counter)
                meeple.r.expire(counter, 120)
                return fn(*args, **kwargs)

    return decorator



def authenticate(fn):
    def decorator(*args, **kwargs):
        import api_tools
        auth_check = check_authentication()
        if auth_check is True:
            return fn(*args, **kwargs)
        return api_tools.api_authentication_error(auth_check)
    return decorator