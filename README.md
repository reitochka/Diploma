# DICOM-storage
- Based on Database (SQLite) engine
- Compatible with DIMSE protocol: C-Move, C-Store, C-Find
- Compatible with WADO protocol: WADO-URI
- Multilanguage web interface

## How to deploy server:
1) Connect to server, write it in terminal on your computer (change localhost to your server):
```
$ ssh root@127.0.0.1
```
2) After 1rst start server, we need to update server:
```
$ sudo apt-get update
$ sudo apt-get upgrade
```
3) Have to make new user:
```
$ sudo groupadd admin
$ sudo adduser <username>
$ sudo usermod -a -G admin <username>
$ sudo dpkg-statoverride --update -add root admin 4750 /bin/su
$ su <username>
```
4) Changing locales:
```
$ sudo apt-get install nano
$ sudo nano /etc/default/locale
```
add to this file info:
```
LANGUAGE=en_US.UTF-8
LC_ALL=en_US.UTF-8
LANG=en_US.UTF-8
LC_TYPE=en_US.UTF-8
```
and then activate changes:
```
$ sudo locale-gen en_US en_US.UTF-8
($ sudo locale-gen en_US.UTF-8)
$ sudo dpkg-reconfigure locales
```
5) To connect to server via ssh without password, need to do on your computer:
```
$ ssh-copy-id <username>@server
```
6) Install all needed packages:
```
$ sudo apt-get install python3 nginx python3-setuptools python3-venv python3-dev git build-essential supervisor mysql-server libmysqlclient-dev
```

7) Create and activate virtual enviroment:
```
$ python3 -m venv <name_of_venv>
$ source <name_of_venv>/bin/activate
```
8) Install all needed libraries for python:
```
(<name_of_venv>) pip install django gunicorn mysqlclient 
```
### How to install EXISTED Django-app:
1) Initialize your local repository: 
```
$ git init
```
2) Clone your project from working repository:
```
$ git clone https://github.com/myproject.git
```
3) Change <name_of_project>/settings.py:
```
ALLOWED_HOSTS = ['127.0.0.1', 'your_server_host']
```

### How to install NEW Django-app:
1) Make new project:
```
(<name_of_venv>) django-admin startproject <name_of_project>
```
2) Make new application:
```
(<name_of_venv>) python manage.py startapp <name_of_app>
```
3) Change <name_of_project>/settings.py:
```
ALLOWED_HOSTS = ['127.0.0.1', 'your_server_host']
INSTALLED_APPS = [
  ...
  '<name_of_app>',
]
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': '<my_database>',
    'USER': '<username>',
    'PASSWORD': 'password',
    'HOST': 'localhost',
    'PORT': '',
  }
}
TIME_ZONE='Europe/Moscow'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static')
```
### How to install and run Mysql server:
1) If version of mysql < 5.7, you need to run:
```
$ sudo mysql-install_db
```
2) Set mysql-server and follow the instructions:
```
$ sudo mysql_secure_installation
```
3) Creatre db for Django-app:
```
$ sudo mysql -u root -p
> CREATE DATABASE my_database CHARACTER SET UTF8;
> CREATE USER <username>@localhost IDENTIFIED BY 'password'
> GRANT ALL PRIVILEGES ON my_database.* TO '<username>'@'localhost';
> FLUSH PRIVILEGES;
> exit;
```
## Let's return to deploying web-app:
9) Set database Django-app
```
$ python manage.py migrate
$ python manage.py makemigrations
$ python manage.py createsuperuser
```
10) Collect static files in Django-app
```
$ python manage.py collectstatic
```
11) Start nginx frond-end server, make new config
```
$ sudo nano /etc/nginx/sites-enabled/my_conf.conf
```
and copy this:
```
server {
    listen 80;
    server_name 111.222.333.44; #либо ip, либо доменное имя
    access_log  /var/log/nginx/example.log;

    location  /static {
        alias /home/admin/project/app/static;
    }

    location / {
        proxy_pass http://127.0.0.1:8000; 
        proxy_set_header Host $server_name;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
  }
```
start nginx:
```
$ sudo service nginx restart
or
$ sudo /etc/init.d/nginx restart
```
12) Start gunicorn, make new gunicorn config:
```
$ nano /path/to/<name_of_project>/<name_of_project>/gunicorn.conf.py
```
and copy this:
```
bind = '127.0.0.1:8000'
workers = 3
user = '<username>'
```
13) Configure and run supervisor for gunicorn:
```
$ sudo nano /etc/supervisor/conf.d/<name_of_project>.conf
```
and add this info:
```
[program:<name_of_project>]
command = /path/to/<name_of_venv>/bin/gunicorn <name_of_project>.wsgi:application -c /path/to/<name_of_project>/<name_of_project>/gunicorn.conf.py
directory = /path/to/<name_of_project>
user = <username>
autorestart = true
redidect_stderr = true
```
and run supervisor:
```
$ sudo supervisord
```

## How to use git:
1) Create new short name for repository
```
$ git remote add <myproj> https://github.com/reitochka/Diploma.git
```
2) Download last update 
```
$ git pull <myproj> master
```
3) Upload last update
```
$ git add * (or names of needed files)
$ git commit -m 'Comment for commit'
$ git push <myproj> master
```

## How to use supervisor:
1) Read updated configs
```
$ supervisorctl reread
```
2) ???
```
$ supervisorctl update
```
3) Get status of project
```
$ supervisorctl status <myproject>
```
4) Restart project
```
$ supervisorctl restart <myproject>
```
## How to use mysql:
1) Connect to database
```
$ sudo mysql -u <username> -p
```
2) Some commands to show some info
```
> SHOW DATABASEES;
> USE <database_name>;
> SHOW TABLES;
> SHOW COLUMNS FROM <table_name>;
> SELECT * FROM <table_name>
```
3) How to make database dump
```
$ mysqldump -u <username> -p dbname_old > dbname.sql
$ mysql -u <username2> -p dbname_new < dbname.sql
```
4) How to start mysql server
```
$ sudo /etc/init.d/mysql start
```
5) delete smth
```
> DLETE FROM <table_name> WHERE <column> like '%some_text%' LIMIT 1;
```
