CREATE SCHEMA staging;
CREATE SCHEMA analytics;

ALTER DATABASE roma9_db
SET search_path TO analytics, public;


