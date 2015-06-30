from oauthlib.oauth2 import OAuth2Error


class OAuthToolkitError(Exception):
    """
    Base class for exceptions
    """
    def __init__(self, error=None, redirect_uri=None, *args, **kwargs):
        super(OAuthToolkitError, self).__init__(*args, **kwargs)
        self.oauthlib_error = error
        if redirect_uri:
            self.oauthlib_error.redirect_uri = redirect_uri


class FatalClientError(OAuthToolkitError):
    """
    Class for critical errors
    """
    pass


class ApplicationStatusError(OAuth2Error):
    error = 'application status'