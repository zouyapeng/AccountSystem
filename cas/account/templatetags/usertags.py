# -*- coding: UTF-8 -*-
import datetime
from django import template
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.template import resolve_variable
import pytz
from account.permissions import perms
import inspect

register = template.Library()


@register.filter()
def user_tz(value, user):
    if not value:
        return None
    tz = settings.TIME_ZONE
    if isinstance(user, User):
        try:
            tz = user.userprofile.timezone
        except ObjectDoesNotExist:
            pass
    try:
        result = value.astimezone(pytz.timezone(tz))
    except ValueError:
        result = value.replace(tzinfo=pytz.timezone(settings.TIME_ZONE)).astimezone(pytz.timezone(tz))
    return result


@register.assignment_tag(takes_context=True)
def has_perm(context, perm):
    try:
        request = context['request']
        user = request.user
        return user.has_perm(perm)
    except:
        return False


def load_perms_filters():
    def partial(func_name, perms_obj):
        def newfunc(user, obj):
            return getattr(perms_obj, func_name)(user, obj)

        return newfunc

    def partial_no_param(func_name, perms_obj):
        def newfunc(user):
            return getattr(perms_obj, func_name)(user)

        return newfunc

    for method in inspect.getmembers(perms):
        if inspect.ismethod(method[1]) and inspect.getargspec(method[1]).args[0] == 'self' and \
                (method[0].startswith('may') or method[0].startswith('filter')):
            if len(inspect.getargspec(method[1]).args) == 3:
                register.filter('%s%s' % ('perm_', method[0]), partial(method[0], perms))
            elif len(inspect.getargspec(method[1]).args) == 2:
                register.filter('%s%s' % ('perm_', method[0]), partial_no_param(method[0], perms))


class UserGroupNode(template.Node):
    def __init__(self, nodelist, user, group, ug):
        self.nodelist = nodelist
        self.group = group
        self.user = user
        self.ug = ug

    def render(self, context):
        group = resolve_variable(self.group, context)
        user = resolve_variable(self.user, context)
        try:
            ug = group.usergroup_set.get(user=user)
            context.push({self.ug: ug})
            output = self.nodelist.render(context)
            context.pop()
        except:
            output = self.nodelist.render(context)
        return output


@register.tag
def user_group(parser, token):
    tag_name, user, group, ug = token.split_contents()
    nodelist = parser.parse(('enduser_group', ))
    parser.delete_first_token()
    return UserGroupNode(nodelist, user, group, ug)


class PaginationResultsNode(template.Node):
    def render(self, context):
        try:
            paginator = context['paginator']
            if not paginator.count:
                return ''
            page_obj = context['page_obj']
            start = (page_obj.number - 1) * paginator.per_page + 1
            end = start + paginator.per_page-1
            if paginator.count < end:
                end = paginator.count
            return "第: <b>%s</b> - <b>%s</b> 个, 共 <b>%s</b> 个" % (start, end, paginator.count)
        except:
            return ''


@register.tag
def pagination_results(parser, token):
    token.split_contents()
    return PaginationResultsNode()


load_perms_filters()