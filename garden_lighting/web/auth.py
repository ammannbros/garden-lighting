from flask import request, session


class Auth:
    def __init__(self, token):
        self.token = token

    def auth(self):
        if self.token == "":
            return True

        if 'token' in request.args and request.args.get('token') == self.token:
            session['auth'] = True
            return True
        else:
            return 'auth' in session and session['auth']


def fucked_auth():
    return 'Uhm, nope?', 403
