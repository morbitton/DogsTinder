#!/usr/bin/env bash
os=$(awk -F= '/^NAME/{print $2}' /etc/os-release)


set_mysql() {
	systemctl enable $1
	systemctl start $1
}

if [ $os == '"Ubuntu"' ]
then
    apt-get update
    # !----------! Setting MySQL root user password root/root !----------!
    debconf-set-selections <<< 'mysql-server mysql-server/root_password password LoginPass@@12'
    debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password LoginPass@@12'
    # !----------! install python and mysql !----------!
    apt-get -y install python3-pip mysql-server mysql-client
    set_mysql "mysql"


fi
pip3 install -r /vagrant/requirements.txt

    new_pw='LoginPass@@12'
    mysql -u root -p"$new_pw" <<MYSQL_SCRIPT
    CREATE DATABASE DogsTinder;
    USE DogsTinder;
    create table users(username VARCHAR(25) NOT NULL, password VARCHAR(100) NOT NULL, repassword VARCHAR(100) NOT NULL,
    phone VARCHAR(11) NOT NULL, email VARCHAR(50) NOT NULL, create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY(username));
    create table dogs(dog_id int NOT NULL AUTO_INCREMENT, name VARCHAR(25) NOT NULL, age int NOT NULL, type VARCHAR(20) NOT NULL, 
    area VARCHAR(25) NOT NULL, details TEXT NOT NULL, pic BLOB NOT NULL, primary key(dog_id), foreign key(username) references users(username));
    INSERT into users(username,password,repassword,phone,email) VALUES('mor','1234','1234','050-8371798','morbitton1993@gmail.com');
    DESCRIBE users;
    DESCRIBE dogs;
MYSQL_SCRIPT

    chmod 755 /vagrant/app.py
    nohup python3 /vagrant/app.py > /dev/null 2>&1 &
