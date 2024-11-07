ALTER TABLE fp_models 
ADD COLUMN model_type varchar(100) NOT NULL DEFAULT 'V1_MODEL';
ALTER TABLE fp_models 
ALTER COLUMN model_type SET DEFAULT '';