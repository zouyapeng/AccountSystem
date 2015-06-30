# -*- coding: UTF-8 -*-
import os
import subprocess
from django.conf import settings
import pexpect

private_dir = "private"
certs_dir = "certs"
cbs_key = "{private}/cbs_ca_cert.key".format(private=private_dir)
cbs_crt = "cbs_ca_cert.crt"


def generate_pkcs12(username, password, key=None, crt=None, out=None, certificate_dir=settings.CERTIFICATE_DIR):
    p = subprocess.Popen("sh generate_certificate.sh -w -n {name} -p {password}".format(name=username, password=password),
                         shell=True, cwd="/var/www/cas/cas/certificate/", stdout=subprocess.PIPE)
    r = map(lambda x:x.replace("\r", '').replace("\n", ''), p.stdout.readlines())
    return "{certificate_dir}/{certs}".format(certs=r.pop(), certificate_dir=certificate_dir)


def generate(username, password, certificate_dir=settings.CERTIFICATE_DIR):
    """
    生成浏览器证书
    :param username: 用户名
    :return:
    """
    p = subprocess.Popen("sh generate_certificate.sh  -n  {name} -p {password}".format(name=username, password=password), shell=True, cwd="/var/www/cas/cas/certificate/", stdout=subprocess.PIPE)
    r = map(lambda x:x.replace("\r", '').replace("\n", ''), p.stdout.readlines())
    if len(r) < 2:
        raise Exception("参数错误")
    p12_path = r.pop()
    serial = r.pop()
    return "{certificate_dir}/{p12_path}".format(p12_path=p12_path, certificate_dir=certificate_dir), serial
