from DjangoCaptcha import Captcha
from django.core.urlresolvers import reverse
from django.db.transaction import non_atomic_requests
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext


def home_view(request):
    return redirect(reverse("account:setting", kwargs={"tab": "profile"}))
    return render_to_response('home/home.html', locals(), context_instance=RequestContext(request))


def captcha_view(request):
    ca = Captcha(request)
    ca.img_width = 100
    ca.type = 'word'
    return ca.display()