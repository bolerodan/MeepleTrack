import meeple
from authentication import authenticate,authenticated_user
@meeple.api.route("/test")
@authenticate
def hello():
    return "Hello World!"