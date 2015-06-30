from django.conf import settings


def config(request):
    content = {"PATH_INFO": filter(lambda x: x, request.META.get("PATH_INFO").split("/"))}
    try:
        content['user'] = request.user if request.user.is_authenticated else None
    except:
        pass
    return content

