from __future__ import absolute_import
from django.conf.urls import patterns, url, include

from . import views
from tastypie.api import NamespacedApi
from oauth2 import resource

api = NamespacedApi('v1', urlconf_namespace='oauth2')
api.register(resource.AccessTokenResource())
api.register(resource.UserResource())

urlpatterns = patterns(
    '',
    url(r'^authorize/$', views.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', views.TokenView.as_view(), name="token"),
    url(r'^me/$', views.me_view, name='me'),
    url(r'^api/', include(api.urls)),
)

# Application management views
urlpatterns += patterns(
    '',
    url(r'^applications/$', views.ApplicationList.as_view(), name="list"),
    url(r'^applications/register/$', views.ApplicationRegistration.as_view(), name="register"),
    url(r'^applications/(?P<pk>\d+)/$', views.ApplicationDetail.as_view(), name="detail"),
    url(r'^applications/(?P<pk>\d+)/delete/$', views.ApplicationDelete.as_view(), name="delete"),
    url(r'^applications/(?P<pk>\d+)/update/$', views.ApplicationUpdate.as_view(), name="update"),
    url(r'^applications/(?P<pk>\d+)/examine/$', views.ApplicationExamine.as_view(), name='examine'),
)
