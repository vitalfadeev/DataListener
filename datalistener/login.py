from functools import wraps
from flask import Flask, flash, request, redirect, url_for, render_template, Response, abort
from datalistener import settings

# decorator for check login/password
def login_required(func):
    """ Decorator for check user/password
        This version can be used as replace HTTP Basic Auth.
        For auth via HTTP URL params: ?username=test&password=test
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # ?username=test&password=test
        if request.method in ['POST', 'PUT']:
            username = request.values.get('username', None)
            password = request.values.get('password', None)
        else:
            username = request.args.get('username', None)
            password = request.args.get('password', None)

        # check username & password
        if username == settings.USERNAME and password == settings.PASSWORD:
            return func(*args, **kwargs) # OK
        else:
            abort(403) # access denied

    return wrapper


