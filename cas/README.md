
## 安装

### 安装依赖

```
sudo apt-get install python-virtualenv python-pip python-dev
```

#### python 虚拟环境的路径（virtualenv）
``` virtualenv /var/www/env ```

#### 使用虚拟环境
```source /var/www/env/bin/activate```


### 安装python packages
必须先装Django 因为很多packages依赖Django

####注意 不能使用sudo pip， 会安装到系统的环境，而不会安装env下， 
可以修改env目录的所有者为当前用户

```
chown {当前登陆用户}:{当前登陆用户组} /var/www/env -R
```
<br>
<br>
<br>
然后

```
pip install Django==1.7.4
```

通过requirements.txt文件安装python依赖packages

在cas/cas/路径下 

```
pip install -r requirements.txt
```

### 创建数据库

```
python manage.py syncdb
```


### 安装uwsgi

```
pip install http://projects.unbit.it/downloads/uwsgi-lts.tar.gz
```


### 在cas/cas/路径下创建uwsgi配置文件 uwsgi.ini

```
vim uwsgi.ini
```

    
    [uwsgi]

    \#socket路径 能让nginx 访问到

    socket = /tmp/cas.socket

    \# uwsgi reload id

    pidfile = /tmp/cas.pid

    \#python 虚拟环境的路径（virtualenv）python libraries 路径
    virtualenv = /var/www/env

    pythonpath = /var/www

    \#项目的跟路径

    pythonpath = /var/www/cas/cas

    chdir = /var/www/cas/cas
    \#日志文件

    daemonize = /var/www/cas/cas/web.log

    chmod-socket = 666

    master = true

    processes = 4

    \#项目的setting.py 文件

    env=DJANGO_SETTINGS_MODULE=settings

    env=PYTHON_EGG_CACHE=/tmp/cas

    env=LANG=zh_CN.UTF-8

    env=LC_ALL=zh_CN.UTF-8

    \#项目的wsgi.py 文件

    module = wsgi

    max-requests = 500000

    \#运行项目的用户， 启动uwsgi时必须 给项目目录 www-data和python 虚拟环境的路径的权限


    gid = www-data

    uid = www-data

    ignore-sigpipe = true

    enable-threads = true



### 启动uwsgi

```
sudo -u www-data uwsgi --ini uwsgi.ini
```

启动完成 /tmp/ 会存在cas.socket


### 创建nginx配置文件

```
cd /etc/nginx/sites-available/
```

```
vim cas
```

    server {

        listen 8000 default_server;
        
        #项目跟跟路径
        
        root /var/www/cas/cas;
        
        #静态文件配置
        
        location ~ ^(/static/) {
        
                root /var/www/cas/cas;
                expires 7d;
                access_log   off;
        }

        #上传静态文件配置
        location ~ ^(/media/) {
                root /var/www/cas/cas;
                access_log   off;
        }
        #不需要记录日志
        location ~* ^.+\.(jpg|jpeg|gif|png|ico|css|zip|tgz|gz|rar|bz2|doc|xls|exe|pdf|ppt|txt|tar|mid|midi|wav|bmp|rtf|js|mov) {
                access_log   off;
        }

        #日志文件
        access_log /var/log/nginx/cas_access.log;
        error_log /var/log/nginx/cas_error.log;
        location / {
                include uwsgi_params;
                #uwsgi 里面生成的socket文件
                uwsgi_pass unix:///tmp/cas.socket;
        }
    }


```
cd ../sites-enabled/
ln -s /etc/nginx/sites-available/cas ./
```

重启nginx

```
service nginx restart
```


## 注意
1.所有命令都是在root权限下执行

2.运行uwsgi是www-data用户,所以项目目录和环境目录必须为www-data:www-data 

chown www-data:www-data /var/www/cas/cas -R

chown www-data:www-data /var/www/env -R





##如果验证码没显示
先卸载Pillow

```
pip uninstall Pillow
```

```
sudo apt-get install libjpeg8-dev  libpng12-dev libfreetype6-dev zlib1g-dev
```

```
pip install Pillow
```