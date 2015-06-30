# -*- coding: UTF-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete, pre_save
from django.utils import timezone
import uuid
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.db import models

# Create your models here.
from django.template.loader import render_to_string
from django.utils.timezone import now
from django_extensions.db.fields import CreationDateTimeField
import ldapdb
from help import send_mail
from django.utils.encoding import python_2_unicode_compatible
from ldapdb.models import fields as ldap_fields


class LdapUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """
    # LDAP meta-data
    base_dn = "ou=People,dc=ldap,dc=com"
    object_classes = ['posixAccount', 'top', 'inetOrgPerson']

    last_name = ldap_fields.CharField("Last name", db_column='sn')
    full_name = ldap_fields.CharField('Common Name', db_column='cn', primary_key=True)

    email = ldap_fields.CharField(db_column='mail')
    uid = ldap_fields.IntegerField(db_column='uidNumber', unique=True)

    group = ldap_fields.IntegerField('GID Number', db_column='gidNumber')
    home_directory = ldap_fields.CharField('Home directory', db_column='Homedirectory')

    username = ldap_fields.CharField(db_column='uid')
    password = ldap_fields.CharField(db_column='userPassword')

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.full_name


def delete_ldap_user(sender, instance, **kwargs):
    # 删除ldap用户
    try:
        LdapUser.objects.get(username=instance.username).delete()
    except Exception as e:
        pass


post_delete.connect(delete_ldap_user, sender=User)


class LdapGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP group entry.
    """
    # LDAP meta-data
    base_dn = "ou=Groups,dc=ldap,dc=com"
    object_classes = ['posixGroup']
    # posixGroup attributes
    gid = ldap_fields.IntegerField(db_column='gidNumber', unique=True)
    name = ldap_fields.CharField(db_column='cn', max_length=200, primary_key=True)
    usernames = ldap_fields.ListField(db_column='memberUid')


    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


@python_2_unicode_compatible
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    human_name = models.TextField("真实姓名")
    gpg_keyid = models.CharField(max_length=64, null=True, blank=True)
    ssh_key = models.TextField(null=True, blank=True)

    old_password = models.CharField("旧密码", max_length=127, null=True, blank=True)
    password_changed = models.DateTimeField("修改密码的时间", default=now())
    passwordtoken = models.TextField("找回密码Token", null=True, blank=True)
    passwordtoken_expires = models.DateTimeField("找回密码Token有效期限", null=True, blank=True)

    emailtoken = models.TextField(default=str(uuid.uuid4()))
    verified_email = models.DateTimeField(null=True, blank=True)
    security_question = models.TextField()
    security_answer = models.TextField()
    comments = models.TextField(null=True, blank=True)
    postal_address = models.TextField(null=True, blank=True)
    country_code = models.TextField(max_length=2, null=True, blank=True)
    telephone = models.TextField(null=True, blank=True)
    facsimile = models.TextField(null=True, blank=True)
    affiliation = models.TextField(null=True, blank=True)

    creation = CreationDateTimeField("注册日期")

    certificate = models.TextField("证书路径", null=True, blank=True)
    certificate_serial = models.CharField(max_length=255, null=True, blank=True)
    certificate_password = models.CharField("证书密码", max_length=255, null=True, blank=True)

    internal_comments = models.TextField(null=True, blank=True)
    ircnick = models.TextField(null=True, blank=True)
    last_seen = models.DateTimeField(default=now())
    status = models.TextField(default="active")
    status_change = models.DateTimeField(default=now())
    locale = models.TextField(default="C")
    timezone = models.TextField(default="UTC")
    latitude = models.IntegerField(null=True, blank=True)
    longitude = models.IntegerField(null=True, blank=True)
    privacy = models.BooleanField(default=False)
    alias_enabled = models.BooleanField(default=True)
    blog_rss = models.TextField(null=True, blank=True)
    blog_avatar = models.TextField(null=True, blank=True)

    # =========app=======
    application_size = models.IntegerField("允许创建应用的数量", default=10, help_text="用户必须拥有add_application权限")

    ldap_dn = models.CharField('LDAP DN', null=True, blank=True, max_length=255)

    def reset_passwordtoken(self):
        """
        重设置passwordtoken
        :return:
        """
        self.passwordtoken = uuid.uuid4()
        self.passwordtoken_expires = timezone.now() + timedelta(
            seconds=settings.PASSWORD_TOKEN_EXPIRE_SECONDS)
        self.save()

    def forget(self):
        """
        找回密码
        #在token有效期内发送的token一样
        :return:
        """

        if not self.passwordtoken:
            self.reset_passwordtoken()
        else:
            if not self.passwordtoken_expires or timezone.now() >= self.passwordtoken_expires:
                self.reset_passwordtoken()
        site = Site.objects.get_current().domain
        domain = '%s://%s' % ('https' if settings.USE_HTTPS else 'http', site)
        body = render_to_string("email_templates/user_forget.html",
                                {"token": self.passwordtoken, "domain": domain,
                                 "user": self.user})
        send_mail("找回密码", None, body, settings.DEFAULT_FROM_EMAIL, [self.user.email])

    def get_ldap_user(self):
        try:
            return LdapUser.objects.get(username=self.user.username)
        except ObjectDoesNotExist:
            return None

    def set_password(self, newpassword, ldap_user=None):
        self.passwordtoken = None
        self.passwordtoken_expires = None
        self.password_changed = now()
        self.old_password = self.user.password
        self.save()

        self.user.set_password(newpassword)
        self.user.save()
        if ldap_user:
            ldap_user.password = newpassword
            ldap_user.save()


    def send_verified_email(self):
        """
        发送激活邮件
        :return:
        """
        user = self.user
        if user.email:
            site = Site.objects.get_current().domain
            domain = '%s://%s' % ('https' if settings.USE_HTTPS else 'http', site)
            body = render_to_string("email_templates/user_active.html",
                                    {
                                        "token": self.emailtoken,
                                        "user": user,
                                        "domain": domain
                                    }
            )
            send_mail("激活邮件", None, body, settings.DEFAULT_FROM_EMAIL, [self.user.email])
        else:
            raise ValueError("用户邮箱不存在")

    class Meta(object):
        verbose_name_plural = verbose_name = "用户扩增字段"

    def __str__(self):
        return self.user.username


def create_user_ldap(user, pwd):
    profile = user.userprofile
    if LdapUser.objects.filter(username=user.username).exists():
        raise Exception("Ldap User Exists")

    l = LdapUser(last_name=user.username,
                 full_name=user.username,
                 uid=user.id,
                 username=user.username,
                 password=pwd,
                 group=settings.LDAP['DEFAULT_GROUP_ID'],
                 home_directory='/home/%s' % user.id,
                 email=user.email)
    l.save()
    # 添加默认的组
    try:
        group = Group.objects.get(id=settings.LDAP['DEFAULT_GROUP_ID'])
        UserGroup(user=user, group=group)
        UserGroup.objects.get_or_create(
            defaults={"user_type": 'user', "is_active": now()},
            user=user,
            group=Group.objects.get(id=settings.LDAP['DEFAULT_GROUP_ID'])
        )
        group.user_set.add(user)
    except:
        pass

    if not profile.ldap_dn:
        profile.ldap_dn = l.build_dn()
        # profile.save()


@python_2_unicode_compatible
class GroupProfile(models.Model):
    group = models.OneToOneField(Group)
    creation = CreationDateTimeField("创建日期")
    founder = models.ForeignKey(User, verbose_name="创建人")
    describe = models.TextField("描述", null=True, blank=True)
    apply = models.BooleanField("用户是否可以申请加入", default=True)

    def __str__(self):
        return self.group.name

    @classmethod
    def post_save(cls, sender, instance, created, **kwargs):
        if created:
            instance.group.user_set.add(instance.founder)
            UserGroup(user=instance.founder, group=instance.group, user_type="administrator", is_active=now()).save()


post_save.connect(GroupProfile.post_save, sender=GroupProfile)


def group_post_save(sender, instance, created, **kwargs):
    if created:
        LdapGroup(gid=instance.id, name=instance.name).save()


def group_pre_save(sender, instance, **kwargs):
    if not instance.pk and LdapGroup.objects.filter(name=instance.name).exists():
        raise Exception("LDAP组已经存在")


def group_post_delete(sender, instance, **kwargs):
    g = LdapGroup.objects.filter(name=instance.name)
    if g.exists():
        g.delete()


post_save.connect(group_post_save, sender=Group)
pre_save.connect(group_pre_save, sender=Group)
post_delete.connect(group_post_delete, sender=Group)


@python_2_unicode_compatible
class UserGroup(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    user_type = models.CharField(choices=(("administrator", "管理员"), ("user", "普通用户")), max_length=30, default="user")
    is_active = models.DateTimeField("验证的时间", null=True, blank=True)
    creation = CreationDateTimeField("加入组的时间")

    class Meta(object):
        verbose_name_plural = verbose_name = "用户所属组信息"

    @classmethod
    def post_delete(cls, sender, instance, **kwargs):
        ldap_group = LdapGroup.objects.get(gid=instance.group.id)
        if instance.user.username in ldap_group.usernames:
            ldap_group.usernames.remove(instance.user.username)
            ldap_group.save()

    @classmethod
    def post_save(cls, sender, instance, created, **kwargs):
        if instance.is_active:
            ldap_group = LdapGroup.objects.get(gid=instance.group.id)
            if instance.user.username not in ldap_group.usernames:
                ldap_group.usernames += [instance.user.username]
                ldap_group.save()




    def __str__(self):
        return "%s-%s" % (self.user.username, self.group.name)


post_save.connect(UserGroup.post_save, sender=UserGroup)
post_delete.connect(UserGroup.post_delete, sender=UserGroup)