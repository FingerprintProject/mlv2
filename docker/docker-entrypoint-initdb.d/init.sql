-- public.fp_models definition

-- Drop table

-- DROP TABLE public.fp_models;

CREATE TABLE public.fp_models (
	id serial4 NOT NULL,
	"name" varchar(255) DEFAULT NULL::character varying NULL,
	"path" text NULL,
	is_active bool DEFAULT false NULL,
	created_at timestamptz DEFAULT now() NULL,
	hospital_id int4 NOT NULL,
	CONSTRAINT fp_models_pkey PRIMARY KEY (id)
);

CREATE INDEX idx_fp_models_id ON public.fp_models USING btree (id);

INSERT INTO public.fp_models (name,"path",is_active,created_at,hospital_id) VALUES
	 ('CRH PROD2024-09-06 16:00','wifi-localization-model-dev/15_1725613150_4159',false,'2024-09-06 23:00:00+07',15),
	 ('CRH PROD2024-09-06 16:10','wifi-localization-model-dev/15_1725613765_2100',false,'2024-09-06 16:10:00+07',15),
	 ('test2024-09-10 11:57','test',false,'2024-09-10 18:57:00+07',999),
	 ('CRH PROD2024-09-06 16:01','wifi-localization-model-dev/15_1725613233_8958',false,'2024-09-06 23:01:00+07',12),
	 ('CRH PROD2024-09-10 11:33','wifi-localization-model-dev/15_1725942752_6643',false,'2024-09-10 11:33:00+07',15),
	 ('CRH PROD2024-09-10 15:12','wifi-localization-model-dev/15_1725955882_6201',false,'2024-09-10 15:12:00+07',15),
	 ('CRH PROD2024-09-10 15:24','wifi-localization-model-dev/15_1725956581_4834',false,'2024-09-10 15:24:00+07',15),
	 ('CRH PROD2024-09-10 08:41','wifi-localization-model-dev/15_1725957525_2166',false,'2024-09-10 08:41:00+07',15),
	 ('CRH PROD2024-09-13 06:37','wifi-localization-model-dev/15_1726209326_7290',true,'2024-09-13 06:37:00+07',15),
	 ('step_exp_2024_08_132024-09-12 18:10','wifi-localization-model-dev/41_1726139418_9234',false,'2024-09-12 18:10:00+07',41);
INSERT INTO public.fp_models (name,"path",is_active,created_at,hospital_id) VALUES
	 ('step_exp_2024_08_132024-09-13 06:50','wifi-localization-model-dev/41_1726210247_8583',true,'2024-09-13 06:50:00+07',41),
	 ('asdasdsad','wifi-localization-model-dev/15_1725951320_1452',false,'2024-09-10 13:56:00+07',15);
