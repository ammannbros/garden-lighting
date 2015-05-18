from flask import request, session


class Auth:
    def __init__(self, token, logger):
        self.logger = logger
        self.token = token

    def auth(self):
        if self.token == "":
            return True

        if 'token' in request.args and request.args.get('token') == self.token:
            session['auth'] = True
            self.logger.info("New user %s" % request.remote_addr)
            return True
        else:
            return 'auth' in session and session['auth']


def fucked_auth():
    return 'Uhm, nope?', 403
