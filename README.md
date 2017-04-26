# DICOM-storage
- Based on Database (SQLite) engine
- Compatible with DIMSE protocol: C-Move, C-Store, C-Find
- Compatible with WADO protocol: WADO-URI
- Multilanguage web interface
- 

## How to install:
1rst start iwth server
```
$ sudo apt-get update
$ sudo apt-get udgrade
$ sudo apt-get install nano python3 nginx python3-setuptools python3-venv python3-dev git build-essetial supervisor
```
Have to make new user:
```
$ sudo groupadd admin
$ sudo adduser <username>
$ sudo usermod -a -G admin <username>
$ sudo dpkg-statoverride --update -add root admin 4750 /bin/su
$ su <username>
```

