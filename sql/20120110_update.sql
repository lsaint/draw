use web_app_db;
alter table web_upload_images ADD COLUMN shortchannel_id   INT not null default 0 AFTER topchannel;