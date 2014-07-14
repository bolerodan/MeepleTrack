
import meeple
from datetime import datetime, timedelta
from settings import token_priv
from crossdomain import crossdomain
from authentication import authenticate, authenticated_user
from flask import request
from flask.ext.security import Security, login_required,http_auth_required,auth_token_required,current_user,roles_required
import jwt
import Crypto.PublicKey.RSA as RSA
import api_tools




@meeple.api.route('/session', endpoint="api_auth", methods=['GET'])
@http_auth_required
def api_auth():
    expires = api_tools.date_format(datetime.utcnow() + timedelta(minutes=30))
    return api_tools.api_package(data={'token':current_user.get_auth_token(), "expires": expires})

# @meeple.api.route('/session', endpoint="api_session", methods=['GET'])
# @crossdomain(origin='*')
# @authenticate
# def api_session():
#     """
#     Request and generate a new user session
#     """

#     user = authenticated_user()
#     priv_key = RSA.importKey(token_priv)
#     payload = {'user_id': user.user_id, 'ip': request.remote_addr}
#     token = jwt.generate_jwt(payload, priv_key, 'PS256', timedelta(minutes=30))
#     expires = api_tools.date_format(datetime.utcnow() + timedelta(minutes=30))
#     data = {"token": token, "expires": expires}
#     return api_tools.api_package(data=data)