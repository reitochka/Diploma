# DICOM-storage
- Based on Database (SQLite) engine
- Compatible with DIMSE protocol: C-Move, C-Store, C-Find
- Compatible with WADO protocol: WADO-URI
- Multilanguage web interface

## How to install:
1) Connect to server, write it in terminal on your computer (change localhost to your server):
```
$ ssh root@127.0.0.1
```
2) After 1rst start server, we need to update server:
```
$ sudo apt-get update
$ sudo apt-get udgrade
```
3) Install all needed packages:
```
$ sudo apt-get install nano python3 nginx python3-setuptools python3-venv python3-dev git build-essetial supervisor 
```
4) Have to make new user:
```
$ sudo groupadd admin
$ sudo adduser <username>
$ sudo usermod -a -G admin <username>
$ sudo dpkg-statoverride --update -add root admin 4750 /bin/su
$ su <username>
```
5) Changing locales:
```
$ nano /home/<username>/.bashrc
```
add to this file info:
```
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```
and then activate changes:
```
$ sudo locale locale-gen en_US en_US.UTF-8
$ sudo dpkg-reconfigure locales
```
6) To connect to server via ssh without password, need to do on your computer:
```
$ ssh-copy-id <username>@server
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


### How to install NEW Django-app:
1) Make new project:
```
(<name_of_venv>) python django_admin startproject <name_of_project>
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
```
