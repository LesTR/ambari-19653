# Simple ambari service for reproducing [AMBARI-19653](https://issues.apache.org/jira/browse/AMBARI-19653)

Tested on Ubuntu 14.04, Ambari 2.4.2.0-136 and HDP 2.4.

How to reproduce:
* stop ambari server (service ambari-server stop)
* clone this repository on ambari server into /var/lib/ambari-server/resources/stacks/HDP/2.4/services/AMBARI-19653
* create metainfo.xml symlink (see below) 
* start ambari server (service ambari-server start)
* use wizard for adding new service

### metainfo-clear.xml
Problem: all packages are installed on all nodes because of missing condition.
This is not acceptable behavior.

### metainfo-workaround.xml
Problem mentioned before is workerounded by copying install_packages + check_package_condition methods in package/scripts/workaround.py. There is replaced hardcoded calls of Script (line 36 for example)  

### License: 
Apache License version 2.0
