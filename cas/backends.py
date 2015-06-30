# # -*- coding: utf-8 -*-

import json
import re
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from account.models import LdapUser


class LdapBackend(ModelBackend):
    def authenticate(self, username,  password):
        try:
            ldap_user = LdapUser.objects.get(username=username, password=password)
            #print ldap_user.description
        except ObjectDoesNotExist:
            return None

        try:
            user = User.objects.get(username=ldap_user.username)
            return user
        except ObjectDoesNotExist:
            return User.objects.create_user(ldap_user.username, ldap_user.email, id=ldap_user.uid)
