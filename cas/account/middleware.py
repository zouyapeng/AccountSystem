from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils import timezone


class TimezoneMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            try:
                timezone.activate(request.user.userprofile.timezone)
            except:
                pass

    def process_response(self, request, response):
        return response


class AuthMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            if not request.path in ['/account/new/', '/account/signout/', '/account/forget/', '/account/signin/']:
                try:
                    request.user.userprofile
                except ObjectDoesNotExist:
                    return redirect(reverse("account:new") + '?next=%s' % request.path)
