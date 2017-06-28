#!/bin/bash


REPO_PATH=/home/ubuntu/httpserver

#deploy auth app
sudo rm -rf /var/www/authapp
sudo cp -R $REPO_PATH/authapp /var/www/authapp
sudo chmod 777 /var/www/authapp

#deploy crud app
sudo rm -rf /var/www/crudapp
sudo cp -R $REPO_PATH/crudapp /var/www/crudapp
sudo chmod 777 /var/www/crudapp

#deploy apache settings
sudo cp $REPO_PATH/deploy/000-default.conf /etc/apache2/sites-enabled/

sudo service apache2 reload
sudo service apache2 restart
