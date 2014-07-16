import meeple
import datetime
from flask import request
from flask.ext.security import auth_token_required,current_user
from api_tools import api_package, api_error, api_error_missing, api_not_found, verify_email
from authentication import authenticate, authenticated_user
from crossdomain import crossdomain
from user import User, UserPasswordReset


@meeple.api.route('/users', endpoint="api_users", methods=['GET'])
@crossdomain(origin='*')
@auth_token_required
def api_users():

    users = []
    if 'site_id' in request.args:
        from qsite import SiteUser, Site
        if Site.authorized(request.args["site_id"]):
            q = SiteUser.query
            q = q.filter(SiteUser.site_id == request.args['site_id'])
            users = [user.as_dict() for user in q.all()]

    return api_package(data=users)


@meeple.api.route('/users/self', endpoint="api_user_self", methods=['GET'])
@crossdomain(origin='*')
@auth_token_required
def api_user_self():
    return api_package(data=current_user._get_current_object().as_dict())

@meeple.api.route('/users/<string:user_id>', endpoint="api_user", methods=['GET'])
@crossdomain(origin='*')
@auth_token_required
def api_user(user_id):
    """
    Return a user.
    """

    q = User.authquery()
    q = q.filter(User.id == user_id)
    user = q.first()
    if user is None:
        return api_not_found("User")

    return api_package(data=user.as_dict())


@meeple.api.route('/users', endpoint="api_user_create", methods=['POST'])
@crossdomain(origin='*')
def api_user_create():

    form = request.get_json()    

    # Validate JSON
    if form is None:

        return api_error("Invalid request")
    required = ["email", "givennames", "lastname"]
    for req in required:
        if req not in form:
            return api_error_missing(req)

    if not verify_email(form["email"]):
        return api_error("Invalid email address", 422)

    # Does user exist?
    olduser = User.query.filter(User.email == form["email"]).first()
    if olduser is not None:
        return api_error("Email address already exists")

    newuser = meeple.user_datastore.create_user(email=form['email'], password='password',firstname=form['givennames'],lastname=form['lastname'])
    print newuser
    meeple.db.session.commit()

    return api_package(data=newuser.as_dict())


@meeple.api.route('/initiatepasswordreset', endpoint="api_user_reset", methods=['POST'])
@crossdomain(origin='*')
def api_user_reset():

    form = request.get_json()

    # Validate JSON
    if form is None:
        return api_error("Invalid request")
    required = ["email"]
    for req in required:
        if req not in form:
            return api_error_missing(req)

    user = User.query.filter(User.email == form["email"]).first()
    if user is None:
        return api_not_found("User")

    pwdreset = UserPasswordReset(user.user_id)
    meeple.db.session.add(pwdreset)
    meeple.db.session.commit()

    if meeple.app.config['DEBUG'] is True or meeple.app.config['TESTING'] is True:
        return api_package(data=pwdreset.token)

    # TODO: Send password reset email in production
    return api_package()

@meeple.api.route('/resetpassword', endpoint="api_reset_password", methods=['POST'])
@crossdomain(origin='*')
def api_reset_password():

    form = request.get_json()

    # Validate JSON
    if form is None:
        return api_error("Invalid request")
    required = ["token", "password"]
    for req in required:
        if req not in form:
            return api_error_missing(req)

    if type(form["password"]) != type([1,]):
        return api_error("Password field must be a list of two passwords", 422)
    if len(form["password"]) != 2:
        return api_error("Password field must be a list of two passwords", 422)
    if form["password"][0] != form["password"][1]:
        return api_error("Passwords must match", 422)

    earliest = datetime.datetime.now() - datetime.timedelta(days=3)
    q = UserPasswordReset.query.filter(UserPasswordReset.token == form["token"])
    q = q.filter(UserPasswordReset.created > earliest)
    resetrequest = q.first()

    if resetrequest is None:
        return api_error("Invalid token", 400)

    user = User.query.filter(User.user_id == resetrequest.user_id).first()
    user.change_password(str(form["password"][0]))
    meeple.db.session.delete(resetrequest)
    meeple.db.session.commit()

    return api_package()