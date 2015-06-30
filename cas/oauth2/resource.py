# -*- coding: UTF-8 -*-
from django.conf.urls import url
from django.contrib.auth.models import User, Permission, Group
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.utils import trailing_slash
from account.models import UserProfile, UserGroup
from oauth2.models import Application, AccessToken, UserOpenID
from tastypie import http
from tastypie.authentication import Authentication, SessionAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.constants import ALL
from tastypie.resources import NamespacedModelResource
from tastypie import fields
from oauth2.settings import oauth2_settings


class ErrorResponse(object):
    CODE_TYPE = {
        1001: "token不存在或过期",
        1002: "参数错误",
        1003: "openid不存在",
        1000: "无权限",

        # group
        1100: "用户组不存在",
        1101: "用户不属于该组",
    }

    def __init__(self, resource, code, request):
        self.resource = resource
        self.code = code
        self.request = request

    def __call__(self, *args, **kwargs):
        raise ImmediateHttpResponse(
            response=self.resource.create_response(
                self.request, {
                    "code": self.code,
                    "msg": kwargs.get("msg") or self.CODE_TYPE[self.code]
                }
            ))


class UserAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        return False


class UserAuthorization(Authorization):
    pass


class ApplicationResource(NamespacedModelResource):
    class Meta:
        include_resource_uri = False
        fields = ['name', 'icon', 'created', 'comm']
        queryset = Application.objects.all()


class AccessTokenResource(NamespacedModelResource):
    application = fields.ForeignKey(ApplicationResource, 'application', full=True)

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        data = {}
        if bundle.data.has_key("scope"):
            scope = filter(lambda s: s in oauth2_settings.SCOPES.keys(), bundle.data["scope"].split(" "))
            data["scope"] = " ".join(scope)
        bundle.data = data
        return super(AccessTokenResource, self).obj_update(bundle, skip_errors, **kwargs)

    def obj_delete(self, bundle, **kwargs):

        if not hasattr(bundle.obj, 'delete'):
            try:
                bundle.obj = self.obj_get(bundle=bundle, **kwargs)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")
        bundle.obj.valid = False
        bundle.obj.save()

    def get_object_list(self, request):
        objects = super(AccessTokenResource, self).get_object_list(request)
        objects = objects.filter(user=request.user)
        return objects

    def dehydrate(self, bundle):
        scopes = bundle.obj.get_scopes
        bundle.data['scopes_descriptions'] = map(
            lambda item: {"scope": item[0], "description": item[1], "selected": item[0] in scopes},
            oauth2_settings.SCOPES.items())
        return bundle

    class Meta:
        fields = ['scope']
        queryset = AccessToken.objects.all()
        resource_name = 'access-token'
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        list_allowed_methods = []
        detail_allowed_methods = ['get', "delete", "put"]
        always_return_data = True
        filtering = {
            'id': ALL
        }


class UserProfileResource(NamespacedModelResource):
    class Meta:
        include_resource_uri = False
        fields = ["human_name", "gpg_keyid", "ssh_key", "verified_email", "telephone", "timezone", "locale", "blog_rss",
                  "blog_avatar"]
        queryset = UserProfile.objects.all()


class UserResource(NamespacedModelResource):
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/get_user_info%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_user_info')),
            url(r"^(?P<resource_name>%s)/get_user_group_info%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_user_group_info')),
        ]

    def is_authenticated(self, request, scope=None):
        try:
            useropen_id = UserOpenID.objects.get(openid=request.GET["openid"])
        except MultiValueDictKeyError:
            ErrorResponse(resource=self, code=1002, request=request)()
        except ObjectDoesNotExist:
            ErrorResponse(resource=self, code=1003, request=request)()
        try:
            token = AccessToken.objects.get(
                user=useropen_id.user,
                application__client_id=request.GET["client_id"],
                token=request.GET["access_token"],
                expires__gte=timezone.localtime(timezone.now()),
                valid=True
            )
            if not token.allow_scopes(scope):
                ErrorResponse(resource=self, code=1000, request=request)()
            return token
        except MultiValueDictKeyError:
            ErrorResponse(resource=self, code=1002, request=request)()
        except ObjectDoesNotExist:
            ErrorResponse(resource=self, code=1001, request=request)()

    def get_user_group_info(self, request, **kwargs):
        token = self.is_authenticated(request, scope=['get_user_group'])
        try:
            group_name = request.GET['group']
            group = Group.objects.get_by_natural_key(group_name)
            try:
                ug = group.usergroup_set.get(user=token.user)
            except ObjectDoesNotExist:
                ErrorResponse(resource=self, code=1101, request=request)()
        except MultiValueDictKeyError:
            ErrorResponse(resource=self, code=1002, request=request)()
        except ObjectDoesNotExist:
            ErrorResponse(resource=self, code=1100, request=request)()

        return self.create_response(
            request, UserGroupResource().full_dehydrate(UserGroupResource().build_bundle(
                obj=ug,
                request=request
            ))
        )

    def get_user_info(self, request, **kwargs):
        token = self.is_authenticated(request, scope=['get_user_info'])
        return self.create_response(request, self.full_dehydrate(self.build_bundle(token.user, request=request)))

    def dehydrate(self, bundle):
        bundle.data.update(UserProfileResource().full_dehydrate(
            UserProfileResource().build_bundle(
                obj=bundle.obj.userprofile,
                request=bundle.request)
        ).data)
        return bundle

    class Meta:
        include_resource_uri = False
        queryset = User.objects.all()
        fields = ["username", "email"]
        resource_name = 'user'
        authentication = UserAuthentication()
        authorization = UserAuthorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        always_return_data = True
        filtering = {
            'id': ALL
        }


class UserGroupResource(NamespacedModelResource):
    class Meta:
        include_resource_uri = False
        queryset = UserGroup.objects.all()
        resource_name = 'user-group'
        authentication = UserAuthentication()
        authorization = UserAuthorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        always_return_data = True
        fields = ["is_active", "user_type"]