# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User
from account.models import UserGroup
from oauth2.models import get_application_model


class DefaultPermissionHandler(object):

    def may_create_application(self, user):
        if user.is_active and user.is_superuser:
            return True
        return user.has_perm("oauth2.add_application") and \
               get_application_model().objects.filter(user=user).count() < user.userprofile.application_size

    def may_audit_user_group(self, user, ug):
        try:
            ug = UserGroup.objects.get(user=user, group=ug.group, user_type="administrator")
            return ug
        except Exception as e:
            pass
        return False

    def may_admin_user_group(self, user, ug):
        try:

            return ug.user_type != 'administrator' and ug.group.groupprofile.founder == user
        except Exception as e:
            pass

        return False

    def may_del_user_group(self, user, ug):
        try:
            gf = ug.group.groupprofile
            if gf.founder == ug.user:
                return False

            if gf.founder == user:
                return True
            else:
                mug = UserGroup.objects.get(user=user, group=ug.group, user_type="user_type")
                if mug.user_type == 'administrator':
                    if ug.user_type != 'administrator':
                        return True
        except Exception as e:
            pass
        return False

perms = DefaultPermissionHandler()