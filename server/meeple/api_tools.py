import re
import json
import datetime
import decimal
from flask import Response

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError
    
def date_format(date):
    if date:
        return date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    else:
        return None

def date_parse(date):
    try:
        return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.000Z')
    except ValueError:
        try:
            return datetime.datetime.fromtimestamp(int(date))
        except valueError:
            return None

def verify_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    return True

def api_package(status='success', status_code=200, data=None, errors=None):
    """
    Generate a nice api package that follows the specifications of the BIRG API.
    """

    api_format, version = get_api_version()

    if api_format == 'json':  # pragma: no cover
        package = {}
        package['api_version'] = version
        package['status'] = status

        if data is not None:
            package['data'] = data

        if errors is not None:
            package['errors'] = errors

        js = json.dumps(package, default=decimal_default)
        resp = Response(js, status=status_code, mimetype='application/json')
        resp.headers.add('Cache-Control', 'no-cache')

        from authentication import extract_authorization_token, session_expiration
        token = extract_authorization_token()
        if token is not None:
            expiration = session_expiration(token)
            resp.headers.add('X-Token-Expire', expiration)
        return resp
    return None

## Wrapper Error Generating Function for missing fields
def api_validation_error(errors):
    msg = ''
    for err in errors:
        msg += str(errors[err]) + ' ('+err+'), '
    return api_error(msg, status=422)
    
## Error Generating Function
def api_error(errors, status=400):

    if type(errors) != type([]):
        errors = [errors]

    return api_package(status='failure',
                       status_code=status,
                       errors=errors)


## Wrapper Error Generating Function for missing fields
def api_error_missing(missing):
    return api_error("Missing field: %s" % missing, status=422)


## Wrapper Error Generating Function for missing fields
def api_not_found(item):
    return api_error("%s not found" % item, status=404)

## Wrapper Error Generating Function for authentication issues
def api_authentication_error(msg=""):
    return api_error("Authentication required (Attempted: %s)" % msg,
                     status=401
                       )

def api_forbidden(msg=""):
    return api_error("Access Denied: %s " % msg,
                     status=403
                       )


def get_api_version():
    """
    Determine what resource type was requested in an API request.

    Returns a tuple with the first position a string represeting the type (json, xml, etc.) and the second the version.

    Looks in the Accept header for:
        application/vnd.mcmaster.birg-v0+json        <-- Internal version in JSON
        application/vnd.mcmaster.birg-v1+json        <-- Version 1 in JSON
        application/vnd.mcmaster.birg+json           <-- Latest version in JSON

    """

    #valid_formats = ['json']
    #valid_versions = [0, 1]

    #default_format = 'json'
    #default_version = 1

    api_format = 'json'
    version = 1

    """
    accepts = str(request.accept_mimetypes).split(',')
    for header in accepts:
        header = header.strip().lower()
        if header.find('application/vnd.qreserve.qreserve') == 0:
            parts = header.split('+')
            if len(parts) > 1:
                api_format = parts[-1]
                if api_format not in valid_formats:
                    api_format = default_format

            version_parts = parts[0].split('-')
            if len(version_parts) > 1:
                api_version = version_parts[-1][1:]  # Strip off the 'v'
                try:
                    version = int(api_version)
                except ValueError:
                    version = default_version
                if version not in valid_versions:
                    version = default_version
    """
    return (api_format, version)