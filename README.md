# DICOM-storage
- Based on Database (SQLite) engine
- Compatible with DIMSE protocol: C-Move, C-Store, C-Find
- Compatible with WADO protocol: WADO-URI
- Multilanguage web interface

## How to install:
1) 1rst start server:
```
$ sudo apt-get update
$ sudo apt-get udgrade
$ sudo apt-get install nano python3 nginx python3-setuptools python3-venv python3-dev git build-essetial supervisor
```
2) Have to make new user:
```
$ sudo groupadd admin
$ sudo adduser <username>
$ sudo usermod -a -G admin <username>
$ sudo dpkg-statoverride --update -add root admin 4750 /bin/su
$ su <username>
```
3) Changing locales:
```
$ nano /home/<username>/.bashrc
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
$ sudo locale locale-gen en_US en_US.UTF-8
$ sudo dpkg-reconfigure locales
```
4) To connect to server via ssh without password, need to do on your computer:
```
$ ssh-copy-id <username>@server
```
5) Create and activate virtual enviroment:
```
$ python3 -m venv <name_of_venv>
$ source <name_of_venv>/bin/activate
```

