from django.conf.urls import patterns, include, url

urlpatterns = patterns('home.views',
    url(r'^$', 'home_view', name='home'),
    url(r'^captcha/$', 'captcha_view', name='captcha'),
)