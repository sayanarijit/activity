# activity

Perform bulk server command execution and validations over ssh in an organised and efficient way.

### Demo

[Watch demo in youtube](https://youtu.be/WiU5vcbMvVU)

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
Defaults: apache !requiretty
apache ALL=(ALL) NOPASSWD:ALL
```

* Run script
``` bash
sudo ./activity.py
```
* Access website at [http://localhost/activity](http://localhost/activity)

### Screenshots

* Interactive command-line view

![a](https://github.com/sayanarijit/activity/blob/master/screenshots/a.png?raw=true)

* Executing command over ssh via command-line interactive mode

![b](https://github.com/sayanarijit/activity/blob/master/screenshots/b.png?raw=true)

* Command execution output in interactive command-line view

![c](https://github.com/sayanarijit/activity/blob/master/screenshots/c.png?raw=true)

* Web GUI - all in one view

![d](https://github.com/sayanarijit/activity/blob/master/screenshots/d.png?raw=true)

* Web GUI - individual reports view

![e](https://github.com/sayanarijit/activity/blob/master/screenshots/e.png?raw=true)


* Web GUI - OS validation

![f](https://github.com/sayanarijit/activity/blob/master/screenshots/f.png?raw=true)


* Web GUI - Disk check

![g](https://github.com/sayanarijit/activity/blob/master/screenshots/g.png?raw=true)


* Web GUI - Raw outputs

![h](https://github.com/sayanarijit/activity/blob/master/screenshots/h.png?raw=true)


* Web GUI - Perform validations with mouse clicks

![i](https://github.com/sayanarijit/activity/blob/master/screenshots/i.png?raw=true)
