-- ALTER TABLE fp_models 
-- ADD COLUMN details jsonb,
-- ADD COLUMN instance_id varchar(100) NOT NULL DEFAULT 'V1';
-- ALTER TABLE fp_models 
-- ALTER COLUMN class_name SET DEFAULT '',
-- ALTER COLUMN instance_id SET DEFAULT '';

ALTER TABLE fp_models 
ADD COLUMN contents jsonb;