# -*- coding: UTF-8 -*-
from urllib import quote
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission, Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.shortcuts import render, render_to_response
from django.template import RequestContext

# Create your views here.
import os
from django.template.loader import render_to_string
from pytz import all_timezones_set
from django.utils import timezone
import pytz
from account.forms import SigninForm, SignupForm, ResetPasswordForm, ProfileForm
from account.models import UserProfile, UserGroup
from help import send_mail


@login_required
def home_view(request):
    return redirect(reverse("account:setting", kwargs={"tab": "profile"}))
    return render_to_response('account/home.html', locals(), context_instance=RequestContext(request))


def active_view(request, token):
    context = {"status": True}

    try:
        userprofile = UserProfile.objects.get(emailtoken=token, verified_email__isnull=True)
        userprofile.verified_email = timezone.now()
        ldap_user = userprofile.get_ldap_user()
        if ldap_user:
            ldap_user.email = userprofile.user.email
            ldap_user.save()
        userprofile.save()
        logout(request)
    except Exception as e:
        context['status'] = False
    return render_to_response('account/active.html', context, context_instance=RequestContext(request))

@login_required
def security_view(request, tab):
    tab1 = "security"
    return render_to_response('account/setting_security_%s.html' % tab, locals(),
                              context_instance=RequestContext(request))


@login_required
def group_add_view(request):
    tab = "group"
    groups = Group.objects.all()

    if request.GET.get("kw"):
        groups = groups.filter(
            Q(name__icontains=request.GET.get("kw")) | Q(groupprofile__describe__icontains=request.GET.get("kw")))
    return render_to_response('account/group_add.html', locals(),
                              context_instance=RequestContext(request))


@login_required
def group_user_view(request, pk):
    tab = "group"
    group = Group.objects.get(name=pk)
    user_set = group.user_set.all().order_by("usergroup__creation")
    if request.GET.get("user_type") in ["administrator", 'user']:
        user_set = user_set.filter(usergroup__user_type=request.GET.get("user_type"))
    if request.GET.get("kw"):
        user_set = user_set.filter(username__icontains=request.GET.get("kw"))
    return render_to_response('account/group_user.html', locals(),
                              context_instance=RequestContext(request))


@login_required
def group_detail_view(request, pk):
    tab = "group"
    group = Group.objects.get(name=pk)
    administrators = group.usergroup_set.filter(user_type="administrator")
    is_active_count = group.user_set.filter(usergroup__is_active__isnull=False).count()
    return render_to_response('account/group_detail.html', locals(),
                              context_instance=RequestContext(request))


@login_required
def group_view(request):
    tab = "group"
    groups = request.user.groups.all()
    return render_to_response('account/group_list.html', locals(),
                              context_instance=RequestContext(request))


@login_required
def setting_view(request, tab):
    user = request.user
    profile = user.userprofile
    if tab == "profile":
        all_timezones = list(all_timezones_set)
        all_timezones.sort()
        return render_to_response('account/setting_profile.html', locals(), context_instance=RequestContext(request))
    elif tab == "certificate":
        return render_to_response('account/setting_certificate.html', locals(),
                                  context_instance=RequestContext(request))


@login_required
def auth_manager_view(request):
    accesstokens = request.user.accesstoken_set.filter(valid=True)
    return render_to_response('account/auth_manager.html', locals(), context_instance=RequestContext(request))


def signup_view(request):
    form = SignupForm()
    if request.method == 'POST':
        form = SignupForm(request.POST, request=request)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=user.username, password=form.data['password'])
            if user:
                login(request, user)

            return HttpResponseRedirect(request.POST.get("next", reverse("account:home")))
    return render_to_response('account/signup.html', locals(), context_instance=RequestContext(request))


def forget_view(request, token=None):
    """
    忘记密码
    :param request:
    :return:
    """
    if token:
        try:
            user_profile = UserProfile.objects.get(passwordtoken=token, verified_email__isnull=False)

        except ObjectDoesNotExist:
            pass
        if not user_profile.passwordtoken_expires or timezone.now() >= user_profile.passwordtoken_expires:
            expires = True
        else:
            form = ResetPasswordForm()
            if request.method == "POST":
                form = ResetPasswordForm(request.POST)
                if form.is_valid():
                    form.save(user_profile.user)
                    return redirect(reverse("account:signin"))

        return render_to_response('account/reset_password.html', locals(), context_instance=RequestContext(request))
    else:
        return render_to_response('account/forget.html', locals(), context_instance=RequestContext(request))


def new_view(request):
    try:
        request.user.userprofile
        return redirect(request.GET.get("next") or reverse("account:home"))
    except ObjectDoesNotExist:
        form = ProfileForm({"email": request.user.email})
        if request.method == 'POST':
            form = ProfileForm(request.POST)
            if form.is_valid():
                form.save(request.user)
                _next = request.GET.get("next", '').strip()
                return redirect(_next or reverse("account:home"))

        return render_to_response('account/new.html', locals(), context_instance=RequestContext(request))

def signout_view(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get('next') or reverse("home:home"))




def signin_view(request):
    form = SigninForm()
    error = None

    if request.method == 'POST':
        error = '用户名或密码错误'
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            if request.POST.get('remember_me'):
                request.session.set_expiry(settings.REMEMBER_SESSION_COOKIE_AGE)
            _next = request.POST.get("next")
            response = redirect(_next or reverse("account:home"))
            return response
    return render_to_response('account/signin.html', {'form': form, "error": error}, context_instance=RequestContext(request))

