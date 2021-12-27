### Odoo FTP Cron job

Main goal:

The main goal of this small project is to read files and process them using a FTP or SFTP servers from Odoo.
Both servers are included in the docker-compose file for testing purposes.
Basically an Odoo Cron Job will download the files from the FTP servers and process them.

Instructions:

1 - docker-compose up

2 - Once everything is running, open a browser at http://127.0.0.1:8069

3 - Crete a new database with demo data

4 - Install the device manager module. This will add a new Device menu

  -  The device menu shows you a list of devices
  -  The config menu allows you to configure the types of device jobs
  -  The ftp demo connector connects to the docker-compose vsftp service

5 - You can wait until the cron job execution or run it manually from the device menu config

6 - It is possible to check the demo connectors from the FTP technical menu using the Developer Mode 

## License
[LGPL version 3 ](http://www.gnu.org/licenses/lgpl-3.0.en.html)