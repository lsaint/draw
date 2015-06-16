create database app_db CHARACTER SET utf8 COLLATE utf8_bin;

use app_db;

create table IF NOT EXISTS app_draw_channel_dictionary
(
       id                BIGINT(20) primary key auto_increment not null unique,
       word_str          VARCHAR(24) not null,
       word_number       TINYINT not null,
       word_category     SMALLINT not null,
       channel_id        BIGINT(20) not null,
       commit_uid        BIGINT(20) not null,
       commit_name       VARCHAR(60) not null,
       create_time       TIMESTAMP not null default now(),
       unique index(channel_id,word_str),
       index(word_number)
) CHARACTER SET utf8 COLLATE utf8_bin;

create table IF NOT EXISTS app_draw_channel_dictionary_history
(
       id                BIGINT(20) primary key auto_increment not null unique,
	   channel_id        BIGINT(20) not null,
       last_visit_time   TIMESTAMP not null default now()
) CHARACTER SET utf8 COLLATE utf8_bin;

create table IF NOT EXISTS app_draw_dictionary
(
       id                BIGINT(20) primary key auto_increment not null unique,
       word_str          VARCHAR(24) not null,
       word_number       TINYINT not null,
       word_category     SMALLINT not null,
       channel_id        BIGINT(20) default 0,
       commit_uid        BIGINT(20) default 0,
       commit_name       VARCHAR(60) default '',
       create_time       TIMESTAMP not null default now(),
       unique index(word_str),
       index(word_number),
       index(word_category)
) CHARACTER SET utf8 COLLATE utf8_bin;
#insert into app_draw_dictionary (word_str,word_number,word_category,commit_uid,commit_name,channel_id) values ('中国',2,0,1000,'Alan',2080);
#insert into app_draw_dictionary (word_str,word_number,word_category,commit_uid,commit_name,channel_id) values ('台湾',2,0,1000,'Alan',5080);
#insert into app_draw_dictionary (word_str,word_number,word_category,commit_uid,commit_name,channel_id) values ('红苹果',3,0,1000,'Alan',3080);
#insert into app_draw_dictionary (word_str,word_number,word_category,commit_uid,commit_name,channel_id) values ('月光光',3,0,1000,'Alan',4080);
#insert into app_draw_dictionary (word_str,word_number,word_category,commit_uid,commit_name,channel_id) values ('猪',1,0,1000,'Alan',2080);


create table IF NOT EXISTS app_pending_summit_draw_dictionary
(
       id                BIGINT(20) primary key auto_increment not null unique,
       word_str          VARCHAR(24) not null unique,
       word_number       TINYINT not null,
       word_category     SMALLINT not null,
       channel_id        BIGINT(20) not null,
       commit_uid        BIGINT(20) not null,
       commit_name       VARCHAR(60) not null,
       create_time       TIMESTAMP not null default now(),
       index(word_str)
) CHARACTER SET utf8 COLLATE utf8_bin;

create table IF NOT EXISTS user_score
(
    id                    BIGINT(20) primary key auto_increment not null unique,
    uid                   BIGINT(20) not null unique,
    draw_be_hitted_amount INT not null default 0,
    hitted_amount         INT not null default 0,
    good_item_amount      INT not null default 0,
    bad_item_amount       INT not null default 0,
    first_hitted_amount   INT not null default 0,
    master_draw_amount    INT not null default 0,
    round_amount          INT not null default 0,
    flower_amount         TINYINT not null default 0,
    egg_amount            TINYINT not null default 0,
    create_time           TIMESTAMP not null default now(),
    index(uid)
) CHARACTER SET utf8 COLLATE utf8_bin;