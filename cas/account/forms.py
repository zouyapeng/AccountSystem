# -*- coding: UTF-8 -*-
import inspect
from DjangoCaptcha import Captcha

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Permission
from django.core import validators
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.timezone import now
from account.models import UserProfile, create_user_ldap, LdapUser


class FormCharField(forms.CharField):
    def widget_attrs(self, widget):
        attrs = super(FormCharField, self).widget_attrs(widget)
        if not attrs.has_key("class"):
            attrs['class'] = ""
        attrs['class'] += ' form-control input-sm'
        return attrs


class SigninForm(forms.Form):
    username = FormCharField(label="用户名")
    password = FormCharField(widget=forms.PasswordInput, label="密码")

    def clean_username(self):

        try:
            self.user = User.objects.get(username=self.cleaned_data['username'])
        except ObjectDoesNotExist:
            raise forms.ValidationError("用户名不存在")
        return self.cleaned_data['username']

    def clean_password(self):
        try:
            if not self.user.check_password(self.cleaned_data['password']):
                raise forms.ValidationError("密码错误")
        except AttributeError:
            pass
        return self.cleaned_data['password']


class ProfileForm(forms.Form):
    human_name = FormCharField(label="真实姓名")
    email = FormCharField(validators=[validators.validate_email], label="常用邮箱")
    security_question = FormCharField(label="安全问题")
    security_answer = FormCharField(label="安全答案")

    def clean_email(self):
        try:
            User.objects.get(email=self.cleaned_data['email'])
        except ObjectDoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError("邮箱已存在")

    def save(self, user):
        ldap_user = LdapUser.objects.get(username=user.username)
        UserProfile(user=user,
                    human_name=self.cleaned_data['human_name'],
                    security_question=self.cleaned_data['security_question'],
                    security_answer=self.cleaned_data['security_answer'],
                    ldap_dn=ldap_user.build_dn()
        ).save()
        user.email = self.cleaned_data['email']
        user.save()


class ResetPasswordForm(forms.Form):
    newpassword = FormCharField(widget=forms.PasswordInput, min_length=5, max_length=30, label="新登录密码")
    newpassword1 = FormCharField(widget=forms.PasswordInput, min_length=5, max_length=30, label="确认新登录密码")

    def clean_newpassword1(self):
        if self.cleaned_data['newpassword'] != self.cleaned_data['newpassword1']:
            raise forms.ValidationError("确认新登录密码错误")

    def save(self, user):
        user.userprofile.set_password(self.cleaned_data['newpassword'])


class SignupForm(forms.Form):
    username = FormCharField(label="用户名")
    human_name = FormCharField(label="真实姓名")
    email = FormCharField(validators=[validators.validate_email], label="常用邮箱")
    security_question = FormCharField(label="安全问题")
    security_answer = FormCharField(label="安全答案")
    password = FormCharField(widget=forms.PasswordInput, label="密码")
    password1 = FormCharField(widget=forms.PasswordInput, label="确认密码")
    captcha = FormCharField(label="验证码")

    def __init__(self, *args, **kwargs):
        if args:
            kwargs.update(dict(zip(inspect.getargspec(super(SignupForm, self).__init__)[0][1:], args)))
        self.request = kwargs.pop('request', None)
        super(SignupForm, self).__init__(**kwargs)

    def clean_captcha(self):
        if hasattr(self, "request"):
            ca = Captcha(self.request)
            if not self.cleaned_data.get("captcha") or not ca.check(self.cleaned_data["captcha"]):
                raise forms.ValidationError("验证码错误")
        return self.cleaned_data['captcha']

    def clean_email(self):
        try:
            User.objects.get(email=self.cleaned_data['email'])
        except ObjectDoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError("邮箱已存在")

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data['username']).exists() or LdapUser.objects.filter(
                username=self.cleaned_data['username']).exists():
            raise forms.ValidationError("用户名已存在")
        return self.cleaned_data['username']

    def clean_password1(self):
        if self.cleaned_data['password'] != self.cleaned_data['password1']:
            raise forms.ValidationError("确认密码错误")

    @transaction.atomic()
    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = User.objects.create_user(username=username, password=password, email=self.cleaned_data["email"])
        # 添加权限
        permissions = (
            ("change_userprofile", 'account', "userprofile"),
            # ("delete_accesstoken", 'oauth2', "accesstoken"),
            ("change_accesstoken", 'oauth2', "accesstoken"),
        )
        for permission in permissions:
            user.user_permissions.add(Permission.objects.get_by_natural_key(*permission))
        user.userprofile = UserProfile(
            user=user,
            human_name=self.cleaned_data['human_name'],
            security_question=self.cleaned_data['security_question'],
            security_answer=self.cleaned_data['security_answer'],
        )

        #添加ldap账户
        create_user_ldap(user, password)
        user.userprofile.save()
        return user
