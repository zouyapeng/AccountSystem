# -*- coding: UTF-8 -*-
import random
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
import re
import uuid
import datetime
from DjangoCaptcha import Captcha
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.sites.models import Site
from django.core import validators
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf.urls import url
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import time
import pytz
from account.permissions import perms
from certificate import generate_browser_certificate
from tastypie import http
from tastypie.authentication import Authentication, SessionAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.constants import ALL
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import NamespacedModelResource
from tastypie.utils import trailing_slash, now
from account.models import UserProfile, UserGroup
from help import send_mail


class UserProfileResource(NamespacedModelResource):
    def get_object_list(self, request):
        objects = super(UserProfileResource, self).get_object_list(request)
        objects = objects.filter(user=request.user)
        return objects

    def put_list(self, request, **kwargs):
        """
        修改用户信息
        :param request:
        :param kwargs:
        :return:
        """
        self.put_detail(request, id=request.user.userprofile.id)
        return http.HttpNoContent()

    class Meta:
        queryset = UserProfile.objects.all()
        resource_name = 'user-profile'
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        list_allowed_methods = ['put']
        detail_allowed_methods = ['get']


class UserResource(NamespacedModelResource):
    def get_object_list(self, request):
        objects = super(UserResource, self).get_object_list(request)
        objects = objects.filter(id=request.user.id)
        return objects

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/change-password%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('change_password')),
            url(r"^(?P<resource_name>%s)/change-security-qa%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('change_security_qa')),
            url(r"^(?P<resource_name>%s)/verified-email%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('verified_email')),
            url(r"^(?P<resource_name>%s)/forget%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('forget')),
            url(r"^(?P<resource_name>%s)/certificate/download%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('certificate_download'), name="certificate_download"),
        ]

    def forget(self, request, **kwargs):
        """
        找回密码
        :param request:
        :param kwargs:
        :return:
        """
        self.method_check(request, allowed=["post"])
        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))

        ca = Captcha(request)
        if not data.get("captcha") or not ca.check(data["captcha"]):
            return self.create_response(request, {"status": False, "msg": "验证码错误", "f": "captcha"})

        email = data.get("email")
        if not email:
            return self.create_response(request, {"status": False, "msg": "邮箱不能为空", "f": "email"})
        try:
            user = User.objects.get(email=email, userprofile__verified_email__isnull=False)
        except ObjectDoesNotExist as e:
            return self.create_response(request, {"status": False, "msg": "邮箱不存在或未激活", "f": "email"})
        user.userprofile.forget()
        return self.create_response(request, {"status": True})


    def certificate_download(self, request, **kwargs):
        """
        证书下载
        :param request:
        :param kwargs:
        :return:
        """
        self.method_check(request, allowed=["post", "get"])
        self.is_authenticated(request)
        user = request.user
        profile = user.userprofile

        if request.method.lower() == "get":
            try:
                f = open(profile.certificate)
                data = f.read()
                f.close()
                response = HttpResponse(data, content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename=%s_browser_cert.p12' % user.username
                return response
            except:
                return HttpResponse("<script >alert('下载错误')</script>")
        else:
            data = self.deserialize(request, request.body,
                                    format=request.META.get('CONTENT_TYPE', 'application/json'))
            password = data.get("password", None)
            if password and not re.compile(r'^\w{6,20}$').match(password):
                raise ImmediateHttpResponse(response=self.create_response(request, {"msg": "密码格式错误"}))

            if profile.certificate:
                # 如果已经生成了证书
                if profile.certificate_password != password:
                    # 修改密码重新生存证书
                    file_path = generate_browser_certificate.generate_pkcs12(user.username, password)
                    profile.certificate = file_path
                    profile.certificate_password = password
                    profile.save()
            else:
                file_path, serial = generate_browser_certificate.generate(user.username, password)
                profile.certificate = file_path
                profile.certificate_password = password
                profile.certificate_serial = serial
                profile.save()
            return self.create_response(request, {"status": True})

    def verified_email(self, request, **kwargs):
        self.method_check(request, allowed=['put'])
        self.is_authenticated(request)
        user = request.user
        userprofile = user.userprofile
        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))

        if data.has_key('email'):
            security_answer = data.get("security_answer")
            # 验证安全问题
            if userprofile.security_answer != security_answer:
                return self.create_response(request, {"status": False, "msg": "安全问题答案错误", "f": "security_answer"})

            email = data['email'].strip()
            if userprofile.verified_email and email == user.email:
                # 如果已经验证邮箱并且修改的email和原email一直
                return self.create_response(request, {"status": False, "msg": "邮箱未修改", "f": "email"})
        else:
            # 重新发送
            if userprofile.verified_email:
                return self.create_response(request, {"status": False, "msg": "邮箱已验证"})
            email = user.email

        try:
            validators.validate_email(email)
        except ValidationError as e:
            return self.create_response(request, {"status": False, "msg": "邮箱格式错误", "f": "email"})

        if user.email != email:
            # 修改邮箱后修改emailtoken
            if User.objects.filter(email=email).exists():
                return self.create_response(request, {"status": False, "msg": "邮箱已存在", "f": "email"})

            emailtoken = uuid.uuid4()
            user.email = email
            user.save()
            userprofile.emailtoken = emailtoken
            userprofile.verified_email = None
            userprofile.save()
            request.session['verified_email'] = None

        # 限制2分钟发一次
        if request.session.get("verified_email"):
            verified_email_date = datetime.datetime.fromtimestamp(float(request.session.get("verified_email")),
                                                                  pytz.UTC) + datetime.timedelta(minutes=1)
            diff = verified_email_date - timezone.now()
            if diff > datetime.timedelta(seconds=0):
                return self.create_response(request, {"status": True, "seconds": diff.seconds})

        try:
            userprofile.send_verified_email()
            request.session['verified_email'] = str(time.time())
            return self.create_response(request, {"status": True})
        except Exception as e:
            return self.create_response(request, {"status": False, "msg": "邮件发送失败"})

    def change_security_qa(self, request, **kwargs):
        self.method_check(request, allowed=['put', 'post'])
        self.is_authenticated(request)
        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))

        user = request.user
        if request.method.lower() == "post":
            # 验证问题
            if user.userprofile.security_answer != data.get("security_answer"):
                return self.create_response(request, {"status": False,
                                                      "msg": "安全问题答案错误",
                                                      "f": "security_answer"})
        else:
            if user.userprofile.security_answer != data.get("security_answer"):
                return self.create_response(request, {"status": False,
                                                      "msg": "安全问题答案错误",
                                                      "f": "security_answer"})
            new_security_question = data.get("new_security_question", "").strip()
            new_security_answer = data.get("new_security_answer", "").strip()
            if not new_security_question or len(new_security_question) <= 0:
                return self.create_response(request, {"status": False,
                                                      "msg": "安全问题不能为空",
                                                      "f": "new_security_question"})
            if not new_security_answer or len(new_security_answer) <= 0:
                return self.create_response(request, {"status": False,
                                                      "msg": "安全问题答案不能为空",
                                                      "f": "new_security_answer"})

            user.userprofile.security_question = new_security_question
            user.userprofile.security_answer = new_security_answer
            user.userprofile.save()

        return self.create_response(request, {"status": True})


    def change_password(self, request, **kwargs):
        self.method_check(request, allowed=['put'])
        self.is_authenticated(request)
        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))
        user = request.user
        profile = user.userprofile
        ldap_user = profile.get_ldap_user()
        if ldap_user:
            if ldap_user.password != data["old_password"]:
                return self.create_response(request, {"status": False, "msg": "原登录密码错误", "f": "old_password"})
            if not data.get("new_password") or len(data.get("new_password")) < 5:
                return self.create_response(request, {"status": False, "msg": "新登录密码格式错误", "f": "new_password"})
            if data.get("new_password") != data.get("new_password1"):
                return self.create_response(request, {"status": False, "msg": "确认新登录密码和新登录密码不同", "f": "new_password1"})
        else:
            return self.create_response(request, {"status": False, "msg": "LDAP用户异常", "f": "old_password"})

        user.userprofile.set_password(data['new_password'], ldap_user)

        user = authenticate(username=user.username, password=data['new_password'])
        if user:
            login(request, user)
        return self.create_response(request, {"status": True})

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ["username", 'email', 'date_joined']
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        always_return_data = True
        filtering = {
            'id': ALL
        }


class GroupResource(NamespacedModelResource):
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<id>\w+)/applications%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('applications'), name="group_applications"),
            url(r"^(?P<resource_name>%s)/audit/(?P<id>\w+)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('audit'), name="group_audit")
        ]

    def audit(self, request, **kwargs):
        self.method_check(request, allowed=["post", "delete", 'put'])
        self.is_authenticated(request)
        ug = UserGroup.objects.get(id=kwargs['id'])
        if request.method.lower() == "delete":
            ug_user = ug.user
            if perms.may_del_user_group(request.user, ug):
                ug.group.user_set.remove(ug_user)
                ug.delete()
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(ug.group).pk,
                    object_id=ug.group.pk,
                    object_repr=force_unicode(ug.group),
                    action_flag=2,
                    change_message="{user}从{group}组移除了{user1}".format(user=force_unicode(request.user),
                                                                      user1=force_unicode(ug_user),
                                                                      group=force_unicode(ug.group))
                )
                return self.create_response(request, {"status": True})

        if request.method.lower() == "put":
            if perms.may_admin_user_group(request.user, ug):
                ug.user_type = 'administrator'
                ug.save()
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(ug.group).pk,
                    object_id=ug.group.pk,
                    object_repr=force_unicode(ug.group),
                    action_flag=2,
                    change_message="{user}设置{user1}为{group}组管理员".format(user=force_unicode(request.user),
                                                                        user1=force_unicode(ug.user),
                                                                        group=force_unicode(ug.group))
                )
                return self.create_response(request, {"status": True})
        else:
            if not ug.is_active and perms.may_audit_user_group(request.user, ug):
                ug.is_active = now()
                ug.save()

                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(ug.group).pk,
                    object_id=ug.group.pk,
                    object_repr=force_unicode(ug.group),
                    action_flag=2,
                    change_message="{user}审批通过{user1}加入{group}组".format(user=force_unicode(request.user),
                                                                        user1=force_unicode(ug.user),
                                                                        group=force_unicode(ug.group))
                )
                return self.create_response(request, {"status": True})

    def applications(self, request, **kwargs):
        self.method_check(request, allowed=["post"])
        self.is_authenticated(request)
        user = request.user
        try:
            group = self.get_object_list(request).get(id=kwargs['id'])
        except:
            return self.create_response(request, {"status": False, "msg": "组不存在"})

        if not group.groupprofile.apply:
            return self.create_response(request, {"status": False, "msg": "该组不允许用户申请"})

        if not user.groups.filter(id=group.id).exists():
            UserGroup(user=user, group=group).save()
            group.user_set.add(user)
        return self.create_response(request, {"status": True})

    class Meta:
        queryset = Group.objects.all()
        resource_name = 'group'
        # fields = ["name']
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        list_allowed_methods = []
        detail_allowed_methods = []
        always_return_data = True
        filtering = {
            'id': ALL
        }
