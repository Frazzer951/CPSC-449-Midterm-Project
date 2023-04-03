CREATE DATABASE 449_db;

use 449_db;

CREATE TABLE
    IF NOT EXISTS `accounts` (
        `id` int NOT NULL AUTO_INCREMENT,
        `username` varchar(50) NOT NULL,
        `password` varchar(255) NOT NULL,
        `email` varchar(100) NOT NULL,
        `organisation` varchar(100) NOT NULL,
        `address` varchar (100) NOT NULL,
        `city` varchar (100) NOT NULL,
        `state` varchar (100) NOT NULL,
        `country` varchar (100) NOT NULL,
        `postalcode` varchar(100) NOT NULL,
        PRIMARY KEY (`id`)
    ) ENGINE = InnODB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8;