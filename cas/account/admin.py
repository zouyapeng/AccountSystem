# -*- coding: UTF-8 -*-
from django.contrib import admin

from django.utils.translation import ugettext, ugettext_lazy as _
# Register your models here.
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from account import models
from account.models import LdapGroup, LdapUser
from oauth2.models import get_application_model


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False
    max_num = 1
    inline_classes = ('grp-collapse grp-open',)
    readonly_fields = ('emailtoken', 'passwordtoken', 'old_password', 'creation', 'ldap_dn')
    fieldsets = (
        ("基本信息", {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('human_name',
                       "gpg_keyid",
                       "ssh_key",
                       "old_password",
                       ("passwordtoken",
                       "password_changed",),
                       ("emailtoken",
                       "verified_email",),
                       "security_question",
                       "security_answer",
                       "comments",
                       "postal_address",
                       "country_code",
                       "telephone",
                       "facsimile",
                       "affiliation",
                       "certificate_serial",
                       "creation",
                       "internal_comments",
                       "ircnick",
                       "last_seen",
                       "status",
                       "status_change",
                       "locale",
                       "timezone",
                       "latitude",
                       "longitude",
                       "privacy",
                       "alias_enabled",
                       "blog_rss",
                       "blog_avatar",
                       'ldap_dn',
            )
        }),
        ("application", {

            'classes': ('grp-collapse grp-closed',),
            'fields': ('application_size', )
        }),
        ("证书", {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('certificate', 'certificate_password')
        }),
    )


class UserAdmin(UserAdmin):
    readonly_fields = ('last_login', 'date_joined')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', 'last_login', 'date_joined')}),
        (_('Permissions'), {

            'classes': ('grp-collapse grp-closed',),
            'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "user_permissions":
            kwargs["queryset"] = Permission.objects.filter(
                content_type=ContentType.objects.get_for_model(get_application_model()),
                codename="add_application"
            )
        return super(UserAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
    inlines = [UserProfileInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return list(self.readonly_fields)+['username']
        else:
            return self.readonly_fields

    def save_model(self, request, obj, form, change):
        create = False
        if not obj.id:
            create = True
        super(UserAdmin, self).save_model(request, obj, form, change)
        if create:
            models.create_user_ldap(obj, form.cleaned_data["password1"])


class GroupProfileInline(admin.StackedInline):
    model = models.GroupProfile
    can_delete = False
    max_num = 1
    inline_classes = ('grp-collapse grp-open',)


class MyGroupAdmin(GroupAdmin):

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "permissions":
            kwargs["queryset"] = Permission.objects.filter(id=-1)
        return super(MyGroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
    inlines = [GroupProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, MyGroupAdmin)


class LdapUserAdmin(admin.ModelAdmin):
    readonly_fields = ['dn']
    list_display = ['username', 'last_name', 'email', 'uid']


class LdapGroupAdmin(admin.ModelAdmin):
    exclude = ['dn', 'usernames']
    list_display = ['name', 'gid']
    search_fields = ['name']

# admin.site.register(LdapGroup, LdapGroupAdmin)
# admin.site.register(LdapUser, LdapUserAdmin)