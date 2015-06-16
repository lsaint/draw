create database web_app_db CHARACTER SET utf8 COLLATE utf8_bin;

use web_app_db;

create table IF NOT EXISTS web_upload_images
(
       id                BIGINT(20) primary key auto_increment not null unique,
       uid               BIGINT(20) default 0,
       name              VARCHAR(60) not null,
       keyword           VARCHAR(24) not null,
       channel_id        BIGINT(20) default 0,
       topchannel        BIGINT(20) not null,
       shortchannel_id   INT not null default 0,
       location          VARCHAR(100) not null default 'static/images/',
       file_name         VARCHAR(60) not null,
       flag              TINYINT not null default 1,
       create_time       TIMESTAMP not null default now(),
       index(topchannel),
       index(flag),
       index(create_time)
) CHARACTER SET utf8 COLLATE utf8_bin;