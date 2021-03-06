import json
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.views.generic import View, FormView
from django.utils import timezone

from oauthlib.oauth2 import Server, InvalidRequestError, InvalidRedirectURIError, InvalidClientIdError

from braces.views import LoginRequiredMixin, CsrfExemptMixin

from ..settings import oauth2_settings
from ..exceptions import OAuthToolkitError, FatalClientError, ApplicationStatusError
from ..forms import AllowForm
from ..models import get_application_model, AccessToken, UserOpenID
from .mixins import OAuthLibMixin

Application = get_application_model()

log = logging.getLogger('oauth2_provider')


class BaseAuthorizationView(LoginRequiredMixin, OAuthLibMixin, View):
    """
    Implements a generic endpoint to handle *Authorization Requests* as in :rfc:`4.1.1`. The view
    does not implement any strategy to determine *authorize/do not authorize* logic.
    The endpoint is used in the following flows:

    * Authorization code
    * Implicit grant

    """

    def dispatch(self, request, *args, **kwargs):
        self.oauth2_data = {}
        return super(BaseAuthorizationView, self).dispatch(request, *args, **kwargs)

    def error_response(self, error, **kwargs):
        """
        Handle errors either by redirecting to redirect_uri with a json in the body containing
        error details or providing an error response
        """
        redirect, error_response = super(BaseAuthorizationView, self).error_response(error, **kwargs)

        if redirect:
            return HttpResponseRedirect(error_response['url'])

        status = error_response['error'].status_code
        return self.render_to_response(error_response, status=status)


class AuthorizationView(BaseAuthorizationView, FormView):
    """
    Implements and endpoint to handle *Authorization Requests* as in :rfc:`4.1.1` and prompting the
    user with a form to determine if she authorizes the client application to access her data.
    This endpoint is reached two times during the authorization process:
    * first receive a ``GET`` request from user asking authorization for a certain client
    application, a form is served possibly showing some useful info and prompting for
    *authorize/do not authorize*.

    * then receive a ``POST`` request possibly after user authorized the access

    Some informations contained in the ``GET`` request and needed to create a Grant token during
    the ``POST`` request would be lost between the two steps above, so they are temporary stored in
    hidden fields on the form.
    A possible alternative could be keeping such informations in the session.

    The endpoint is used in the followin flows:
    * Authorization code
    * Implicit grant
    """
    template_name = 'oauth2/authorize.html'
    form_class = AllowForm

    server_class = Server
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS

    def get_initial(self):
        # TODO: move this scopes conversion from and to string into a utils function
        scopes = self.oauth2_data.get('scope', self.oauth2_data.get('scopes', []))
        initial_data = {
            'redirect_uri': self.oauth2_data.get('redirect_uri', None),
            'scope': ' '.join(scopes),
            'client_id': self.oauth2_data.get('client_id', None),
            'state': self.oauth2_data.get('state', None),
            'response_type': self.oauth2_data.get('response_type', None),
        }
        return initial_data

    def form_valid(self, form):
        try:
            credentials = {
                'client_id': form.cleaned_data.get('client_id'),
                'redirect_uri': form.cleaned_data.get('redirect_uri'),
                'response_type': form.cleaned_data.get('response_type', None),
                'state': form.cleaned_data.get('state', None),
            }

            scopes = form.cleaned_data.get('scope')
            allow = form.cleaned_data.get('allow')
            uri, headers, body, status = self.create_authorization_response(
                request=self.request, scopes=scopes, credentials=credentials, allow=allow)
            self.success_url = uri
            log.debug("Success url for the request: {0}".format(self.success_url))
            return super(AuthorizationView, self).form_valid(form)

        except OAuthToolkitError as error:
            return self.error_response(error)

    def get(self, request, *args, **kwargs):
        try:
            scopes, credentials = self.validate_authorization_request(request)
            kwargs['scopes_descriptions'] = [oauth2_settings.SCOPES[scope] for scope in scopes]
            kwargs['scopes'] = scopes
            # at this point we know an Application instance with such client_id exists in the database
            application = Application.objects.get(client_id=credentials['client_id'])
            #print request.user.accesstoken_set.filter()
            if application.status != 4:
                if request.user != application.user:
                    raise FatalClientError(error=ApplicationStatusError(), redirect_uri="111")
            kwargs['application'] = application  # TODO: cache it!

            kwargs.update(credentials)
            self.oauth2_data = kwargs
            # following two loc are here only because of https://code.djangoproject.com/ticket/17795
            form = self.get_form(self.get_form_class())
            kwargs['form'] = form
            qd = QueryDict("", mutable=True)
            qd["next"] = self.request.get_full_path()
            qd["next"] = "%s?%s" % (reverse("account:signin"), qd.urlencode(safe='/'))
            kwargs["next"] = qd.urlencode(safe='/')
            # Check to see if the user has already granted access and return
            # a successful response depending on 'approval_prompt' url parameter
            require_approval = request.GET.get('approval_prompt', oauth2_settings.REQUEST_APPROVAL_PROMPT)
            if require_approval == 'auto':
                tokens = request.user.accesstoken_set.filter(application=kwargs['application'],
                                                             expires__gt=timezone.now(), valid=True).all()
                # check past authorizations regarded the same scopes as the current one
                for token in tokens:
                    if token.allow_scopes(scopes):
                        uri, headers, body, status = self.create_authorization_response(
                            request=self.request, scopes=" ".join(scopes),
                            credentials=credentials, allow=True)
                        return HttpResponseRedirect(uri)
            return self.render_to_response(self.get_context_data(**kwargs))

        except OAuthToolkitError as error:
            return self.error_response(error)


def me_view(request):
    access_token = request.GET['access_token']
    token = AccessToken.objects.get(token=access_token)
    if not token.is_expired():
        user_openid = UserOpenID.objects.get(user=token.user, application=token.application)
        return HttpResponse(json.dumps({"openid": user_openid.openid}), content_type='application/json')


class TokenView(CsrfExemptMixin, OAuthLibMixin, View):
    """
    Implements an endpoint to provide access tokens

    The endpoint is used in the following flows:
    * Authorization code
    * Password
    * Client credentials
    """
    server_class = Server
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS

    def post(self, request, *args, **kwargs):
        url, headers, body, status = self.create_token_response(request)
        print url, headers, body, status
        response = HttpResponse(content=body, status=status)

        for k, v in headers.items():
            response[k] = v
        return response
