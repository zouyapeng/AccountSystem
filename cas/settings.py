# -*- coding: UTF-8 -*-
"""
Django settings for oauth2_demo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
# import sys
#
#
# reload(sys)
# sys.setdefaultencoding('utf8')

IS_SERVER = False
if os.environ.get("USER") == 'www-data':
    IS_SERVER = True

BASE_DIR = os.path.dirname(__file__)
COMPRESS_OUTPUT_DIR = "dist"
# ==========COMPRESS==============
#
# COMPRESS_HTML = True
# COMPRESS_ENABLED = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@ef_1%i#-bbgn%60zxga&&4sw^$dqdhwni!k7onhce)&k^cz&u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ["*"]

SESSION_COOKIE_NAME = 'cas-sessionid'

# Application definition

INSTALLED_APPS = (
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # 'oauth2_provider',
    'pagination',
    'compressor',
    'account',
    'oauth2',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'account.middleware.TimezoneMiddleware',
    'account.middleware.AuthMiddleware',
    'compresshtml.middleware.CompressHtmlMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "context_processors.config",
)
SITE_ID = 1
USE_HTTPS = True
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
# ===================DATE_FORMAT==============================
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'
TIME_FORMAT = 'H:i:s'

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'

LOGIN_URL = '/account/signin/'
# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': 'ldap://0.0.0.0/',
        'USER': 'cn=admin,dc=ldap,dc=com',
        'PASSWORD': '123456',
    }
}

DATABASE_ROUTERS = ['ldapdb.router.Router']

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'zh-CN'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
OAUTH2_PROVIDER = {
    'SCOPES': {
        "get_user_info": "获取用户信息",
        "update_user_info": "修改用户信息无",
        "get_user_group": "获取用户组信息"
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
# STATICFILES_DIRS = (
# # Put strings here, like "/home/html/static" or "C:/www/django/static".
#     # Always use forward slashes, even on Windows.
#     # Don't forget to use absolute paths, not relative paths.
#     os.path.join(
#         os.path.dirname(__file__),
#         'static',
#     ),
#
# )

AUTHENTICATION_BACKENDS = (
    'backends.LdapBackend',
    # 'django.contrib.auth.backends.ModelBackend',
)


STATIC_ROOT = os.path.join(
    os.path.dirname(__file__),
    'static',
)

PAGINATION_DEFAULT_WINDOW = 2

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

#============浏览器关闭退出==============
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#============记住登陆状态的时间默认2周==============
REMEMBER_SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 2

#============找回密码TOKEN的有效期==============
PASSWORD_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24

#============TASTYPIE==============
TASTYPIE_DEFAULT_FORMATS = ['xml', 'json']

OAUTH2_PROVIDER_APPLICATION_MODEL = "oauth2.Application"


#========Email==========
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.cstnet.cn"
EMAIL_PORT = "25"
EMAIL_USE_TLS = False
EMAIL_HOST_USER = "hulj_os@sari.ac.cn"
EMAIL_HOST_PASSWORD = "zs123123"
DEFAULT_FROM_EMAIL = "hulj_os@sari.ac.cn"

#==========certificate=========
CERTIFICATE_DIR = os.path.join(BASE_DIR, "certificate")

if IS_SERVER:
    COMPRESS_HTML = True
    COMPRESS_ENABLED = True

#ldap
LDAP = {
    "DEFAULT_GROUP_ID": 1
}
