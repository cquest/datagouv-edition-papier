DROP TABLE IF EXISTS datagouv_dataset ;
CREATE TABLE datagouv_dataset (
 id VARCHAR(24) NOT NULL, 
 title text, 
 slug text NOT NULL, 
 url text NOT NULL, 
 organization text, 
 organization_id varchar(24), 
 description text, 
 frequency text, 
 license text, 
 "temporal_coverage.start" DATE, 
 "temporal_coverage.end" DATE, 
 "spatial.granularity" text, 
 "spatial.zones" text, 
 private BOOLEAN, 
 featured BOOLEAN, 
 created_at TIMESTAMP WITHOUT TIME ZONE, 
 last_modified TIMESTAMP WITHOUT TIME ZONE, 
 tags text, 
 "metric.discussions" int, 
 "metric.followers" int, 
 "metric.reuses" int, 
 "metric.issues" int, 
 "metric.views" int
);
\copy datagouv_dataset from datasets-2019-03-16-08-38_out.csv with (format csv, header true)


CREATE TABLE datagouv_org (
 id VARCHAR(24) NOT NULL, 
 name text NOT NULL, 
 slug text NOT NULL, 
 url text NOT NULL, 
 description text NOT NULL, 
 logo text, 
 badges text, 
 created_at TIMESTAMP WITHOUT TIME ZONE, 
 last_modified TIMESTAMP WITHOUT TIME ZONE, 
 "metric.datasets" int NOT NULL, 
 "metric.members" int NOT NULL, 
 "metric.views" int NOT NULL, 
 "metric.permitted_reuses" int NOT NULL, 
 "metric.reuses" int NOT NULL, 
 "metric.dataset_views" int NOT NULL, 
 "metric.reuse_views" int NOT NULL, 
 "metric.followers" int NOT NULL, 
 "metric.resource_downloads" int NOT NULL
);

\copy datagouv_org from organizations-2019-03-16-12-29.csv with (format csv, header true, delimiter ';')
