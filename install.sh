#!/bin/bash

#本脚本需要root身份执行 或者 sudo ./update.sh 执行

[ `id -u` = 0 ] || exit 0

apt-get -y install slapd ldap-utils
sudo dpkg-reconfigure slapd
ldapadd -x -D cn=admin,dc=ldap,dc=com -f ./config/init.ldif -w "123456"

python config_env.py

#安装nginx
apt-get -y install nginx
if [ $? != 0 ]; then
    echo "========================================"
    echo "can not install nginx, then exit"
    exit 2
fi

#拷贝配置文件
rm -rf /etc/nginx/sites-enabled/default
cp ./config/cas_http /etc/nginx/sites-enabled/
if [ $? != 0 ]; then
    echo "========================================"
    echo "can no copy nginx config file, then exit"
    exit 2
fi

rm -rf ./cas/static/admin
rm -rf ./cas/static/grappelli

ln -s /var/www/CAS/env/lib/python2.7/site-packages/django_grappelli-2.6.3-py2.7.egg/grappelli/static/grappelli/ ./cas/static/grappelli
ln -s /var/www/CAS/env/lib/python2.7/site-packages/django_grappelli-2.6.3-py2.7.egg/grappelli/static/admin/ ./cas/static/admin

cp ./config/cas_start.sh /etc/profile.d


#初始化cas
echo ""
echo "初始化cas"
CAS_PATH=`pwd`
chown www-data:www-data $CAS_PATH -R
cas-admin -i

#重启服务
service nginx restart


