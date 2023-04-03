CREATE DATABASE 449_midterm_db;

use 449_midterm_db;

CREATE TABLE
    IF NOT EXISTS `users` (
        `public_id` int NOT NULL AUTO_INCREMENT,
        `username` varchar(50) NOT NULL,
        `password` varchar(255) NOT NULL,
        PRIMARY KEY (`public_id`)
    ) ENGINE = InnODB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8;
