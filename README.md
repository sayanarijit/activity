# activity
Perform bulk server command execution and validations over ssh in an organised and efficient way.

### Requirements
* Python 3.6 (with python-devel)
* virtualenv
* sshpass
* [phpMyAdmin](https://www.phpmyadmin.net/) & [Apache server](https://httpd.apache.org) configured for [codeigniter](https://codeigniter.com) installation
* Password less sudo access to 'apache' user

### Install, configure and run on localhost

* Download and setup main script

``` bash
mkdir -p /script/virtualenv
cd /script
git clone https://github.com/sayanarijit/activity
cd activity
virtualenv -p $(which python3.6) /script/virtualenv/py3.6
/script/virtualenv/py3.6/bin/pip install -r requirements.txt
cp -var website/* /var/www/html/
mkdir -p /var/www/html/activity/application/logs
vim activity.py
```
* Import database
``` bash
mysql -u root -p < activity.sql
```
* Configure website
``` bash
vim /var/www/html/activity/application/config/database.php
```
* Give passwordless sudo access to 'apache' user by making the following entry in `/etc/sudoers`
``` bash
apache ALL=(ALL) NOPASSWD:ALL
```
* Run script
``` bash
sudo ./activity.py
```
* Access website at [http://localhost/activity](http://localhost/activity)
