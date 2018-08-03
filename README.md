# graybean
GELF logger for beanstalk tube stats

## Usage
You can just run it like so:

```sh
sudo pip3 install -r requirements.txt
graybean.py -b bean.example.com:11300 -g graylog.example.com:12201 -u -t default
```

or if you want to run it as a systemd unit just create a unit file something like this:

_/etc/systemd/system/graybean.service_
```
[Unit]
Description=graybean logger
After=multi-user.target

[Service]
Type=simple
ExecStart=/opt/graybean/graybean.py -b bean.example.com:11300 -g graylog.example.com:12201 -u -t default,my_tube
Restart=on-failure
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=graybean

[Install]
WantedBy=multi-user.target
```

and then of course:
```sh
sudo chmod 644 /etc/systemd/system/graybean.service
sudo systemctl daemon-reload
sudo systemctl enable graybean.service
sudo systemctl start graybean.service
```

and be sure to set up the syslog config:

_/etc/rsyslog.d/graybean.conf_
```
if $programname == 'graybean' then /var/log/graybean.log
& stop
```

and restart syslog:
```sh
sudo systemctl restart syslog
```
