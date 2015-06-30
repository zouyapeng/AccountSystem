from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
import settings

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'oauth_demo.views.home', name='home'),
                       url(r'^oauth2/', include('oauth2.urls', namespace='oauth2')),
                       url(r'^account/', include('account.urls', namespace="account")),

                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^', include('home.urls', namespace="home")),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
