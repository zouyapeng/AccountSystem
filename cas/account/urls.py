from django.conf.urls import patterns, include, url
from tastypie.api import NamespacedApi
from account import resource

api = NamespacedApi('v1', urlconf_namespace='account')
api.register(resource.UserResource())
api.register(resource.UserProfileResource())
api.register(resource.GroupResource())


urlpatterns = patterns('account.views',
    # Examples:
    url(r'^new/$', 'new_view', name='new'),
    url(r'^signin/$', 'signin_view', name='signin'),
    url(r'^signout/$', 'signout_view', name='signout'),
    url(r'^signup/$', 'signup_view', name='signup'),
    url(r'^forget/(?P<token>.*)$', 'forget_view', name='forget'),

    url(r'^auth-manager/$', 'auth_manager_view', name='auth_manager'),
    url(r'^setting/security/(?P<tab>\w+)/$', 'security_view', name='security'),
    url(r'^group/$', 'group_view', name='group'),
    url(r'^group/(?P<pk>.+)/user/$', 'group_user_view', name='group_user'),
    url(r'^group/add/$', 'group_add_view', name='add_group'),
    url(r'^group/detail/(?P<pk>.+)/$', 'group_detail_view', name='group_detail'),
    url(r'^setting/(?P<tab>.+)/$', 'setting_view', name='setting'),

    url(r'^active/(?P<token>.+)/$', 'active_view', name='active'),
    url(r'^$', 'home_view', name='home'),

    url(r'^api/', include(api.urls)),

)