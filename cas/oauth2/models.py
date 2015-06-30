# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django_extensions.db.fields import CreationDateTimeField

try:
    # Django's new application loading system
    from django.apps import apps

    get_model = apps.get_model
except ImportError:
    from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ImproperlyConfigured

from .settings import oauth2_settings
from .compat import AUTH_USER_MODEL
from .generators import generate_client_secret, generate_client_id
from .validators import validate_uris


@python_2_unicode_compatible
class AbstractApplication(models.Model):
    """
    An Application instance represents a Client on the Authorization server.
    Usually an Application is created manually by client's developers after
    logging in on an Authorization Server.

    Fields:

    * :attr:`client_id` The client identifier issued to the client during the
                        registration process as described in :rfc:`2.2`
    * :attr:`user` ref to a Django user
    * :attr:`redirect_uris` The list of allowed redirect uri. The string
                            consists of valid URLs separated by space
    * :attr:`client_type` Client type as described in :rfc:`2.1`
    * :attr:`authorization_grant_type` Authorization flows available to the
                                       Application
    * :attr:`client_secret` Confidential secret issued to the client during
                            the registration process as described in :rfc:`2.2`
    * :attr:`name` Friendly name for the Application
    """
    CLIENT_CONFIDENTIAL = 'confidential'
    CLIENT_PUBLIC = 'public'
    CLIENT_TYPES = (
        (CLIENT_CONFIDENTIAL, _('Confidential')),
        (CLIENT_PUBLIC, _('Public')),
    )

    GRANT_AUTHORIZATION_CODE = 'authorization-code'
    GRANT_IMPLICIT = 'implicit'
    GRANT_PASSWORD = 'password'
    GRANT_CLIENT_CREDENTIALS = 'client-credentials'
    GRANT_TYPES = (
        (GRANT_AUTHORIZATION_CODE, _('Authorization code')),
        (GRANT_IMPLICIT, _('Implicit')),
        (GRANT_PASSWORD, _('Resource owner password-based')),
        (GRANT_CLIENT_CREDENTIALS, _('Client credentials')),
    )

    client_id = models.CharField(max_length=100, unique=True,
                                 default=generate_client_id, db_index=True)
    user = models.ForeignKey(AUTH_USER_MODEL)
    help_text = _("Allowed URIs list, space separated")
    redirect_uris = models.TextField(help_text=help_text,
                                     validators=[validate_uris], blank=True)
    client_type = models.CharField(max_length=32, choices=CLIENT_TYPES, default=CLIENT_CONFIDENTIAL)
    authorization_grant_type = models.CharField(max_length=32,
                                                choices=GRANT_TYPES, default=GRANT_AUTHORIZATION_CODE)
    client_secret = models.CharField(max_length=255, blank=True,
                                     default=generate_client_secret, db_index=True)
    name = models.CharField('应用名词', max_length=20)

    class Meta:
        abstract = True

    @property
    def default_redirect_uri(self):
        """
        Returns the default redirect_uri extracting the first item from
        the :attr:`redirect_uris` string
        """
        if self.redirect_uris:
            return self.redirect_uris.split().pop(0)

        assert False, "If you are using implicit, authorization_code" \
                      "or all-in-one grant_type, you must define " \
                      "redirect_uris field in your Application model"

    def redirect_uri_allowed(self, uri):
        """
        Checks if given url is one of the items in :attr:`redirect_uris` string

        :param uri: Url to check
        """
        for u in self.redirect_uris.split():
            if uri.startswith(u):
                return True
        return False
        # return uri in self.redirect_uris.split()

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.redirect_uris \
                and self.authorization_grant_type \
                        in (AbstractApplication.GRANT_AUTHORIZATION_CODE,
                            AbstractApplication.GRANT_IMPLICIT):
            error = _('Redirect_uris could not be empty with {0} grant_type')
            raise ValidationError(error.format(self.authorization_grant_type))

    def get_absolute_url(self):
        return reverse('oauth2:detail', args=[str(self.id)])

    def __str__(self):
        return self.name or self.client_id


class Application(AbstractApplication):
    icon = models.ImageField(blank=True, null=True)
    comm = models.TextField("应用简介", max_length=400)
    created = CreationDateTimeField()
    status = models.IntegerField(max_length=1,
                                 choices=((1, "未提交审核"), (2, "审核中"), (3, "审核驳回"), (4, "已上线")),
                                 default=1)
    rejection_reason = models.TextField("驳回原因", null=True, blank=True)

    class Meta:
        ordering = ['-created', '-id']


# Add swappable like this to not break django 1.4 compatibility
Application._meta.swappable = 'OAUTH2_PROVIDER_APPLICATION_MODEL'


@python_2_unicode_compatible
class Grant(models.Model):
    """
    A Grant instance represents a token with a short lifetime that can
    be swapped for an access token, as described in :rfc:`4.1.2`

    Fields:

    * :attr:`user` The Django user who requested the grant
    * :attr:`code` The authorization code generated by the authorization server
    * :attr:`application` Application instance this grant was asked for
    * :attr:`expires` Expire time in seconds, defaults to
                      :data:`settings.AUTHORIZATION_CODE_EXPIRE_SECONDS`
    * :attr:`redirect_uri` Self explained
    * :attr:`scope` Required scopes, optional
    """
    user = models.ForeignKey(AUTH_USER_MODEL)
    code = models.CharField(max_length=255, db_index=True)  # code comes from oauthlib
    application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL)
    expires = models.DateTimeField()
    redirect_uri = models.CharField(max_length=255)
    scope = models.TextField(blank=True)

    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        return timezone.now() >= self.expires

    def redirect_uri_allowed(self, uri):
        return uri == self.redirect_uri

    def __str__(self):
        return self.code


@python_2_unicode_compatible
class UserOpenID(models.Model):
    openid = models.AutoField(primary_key=True)
    application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL)
    user = models.ForeignKey(AUTH_USER_MODEL)
    created = CreationDateTimeField()

    def __str__(self):
        return str(self.openid)



@python_2_unicode_compatible
class AccessToken(models.Model):
    """
    An AccessToken instance represents the actual access token to
    access user's resources, as in :rfc:`5`.

    Fields:

    * :attr:`user` The Django user representing resources' owner
    * :attr:`token` Access token
    * :attr:`application` Application instance
    * :attr:`expires` Expire time in seconds, defaults to
                      :data:`settings.ACCESS_TOKEN_EXPIRE_SECONDS`
    * :attr:`scope` Allowed scopes
    """
    user = models.ForeignKey(AUTH_USER_MODEL)
    token = models.CharField(max_length=255, db_index=True)
    application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL)
    expires = models.DateTimeField()
    scope = models.TextField(blank=True)
    created = CreationDateTimeField()
    valid = models.BooleanField(default=True)

    def is_valid(self, scopes=None):
        """
        Checks if the access token is valid.

        :param scopes: An iterable containing the scopes to check or None
        """
        return self.valid and not self.is_expired() and self.allow_scopes(scopes)

    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        return timezone.now() >= self.expires

    @property
    def get_scopes(self):
        return set(self.scope.split())

    def allow_scopes(self, scopes):
        """
        Check if the token allows the provided scopes

        :param scopes: An iterable containing the scopes to check
        """
        if not scopes:
            return True

        provided_scopes = set(self.scope.split())
        resource_scopes = set(scopes)

        return resource_scopes.issubset(provided_scopes)

    class Meta:
        ordering = ['-created', '-id']

    def __str__(self):
        return self.token


@python_2_unicode_compatible
class RefreshToken(models.Model):
    """
    A RefreshToken instance represents a token that can be swapped for a new
    access token when it expires.

    Fields:

    * :attr:`user` The Django user representing resources' owner
    * :attr:`token` Token value
    * :attr:`application` Application instance
    * :attr:`access_token` AccessToken instance this refresh token is
                           bounded to
    """
    user = models.ForeignKey(AUTH_USER_MODEL)
    token = models.CharField(max_length=255, db_index=True)
    application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL)
    access_token = models.OneToOneField(AccessToken,
                                        related_name='refresh_token')

    def __str__(self):
        return self.token


def get_application_model():
    """ Return the Application model that is active in this project. """
    try:
        app_label, model_name = oauth2_settings.APPLICATION_MODEL.split('.')
    except ValueError:
        e = "APPLICATION_MODEL must be of the form 'app_label.model_name'"
        raise ImproperlyConfigured(e)
    app_model = get_model(app_label, model_name)
    if app_model is None:
        e = "APPLICATION_MODEL refers to model {0} that has not been installed"
        raise ImproperlyConfigured(e.format(oauth2_settings.APPLICATION_MODEL))
    return app_model
