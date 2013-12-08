
drop table if exists ccaa;
create table ccaa (
    id varchar(200) unique,
    ccaa_label varchar(200)
);

drop table if exists ccaa_census;
create table ccaa_census (
    id varchar(200) unique,
    
    date_year integer,
    ccaa_id integer,
    genre varchar(200),
    amount integer
    
);

drop table if exists ccaa_budget;
create table ccaa_budget (
    id varchar(128) unique,
    
    date_year integer,
    ccaa_id integer,
    function_code integer,
    function_label varchar(200),
    
    amount real,
    amount_per_capita real,
    amount_per_ccaa_capita real
);

drop table if exists pge_sections;
create table pge_sections (
    id varchar(200) unique,
    name varchar(200)
);

drop table if exists pge_organisms;
create table pge_organisms (
    id varchar(200) unique,
    pge_sections_id varchar(200),
    organism_type integer,
    
    name varchar(200)
);

drop table if exists pge_groups;
create table pge_groups (
    id varchar(200) unique,
    name varchar(200)
);

drop table if exists pge_concepts_l1;
create table pge_concepts_l1 (
    id varchar(200) unique,
    level1 varchar(200)
);
drop table if exists pge_concepts_l2;
create table pge_concepts_l2 (
    id varchar(200) unique,
    level1_id varchar(200),
    level2 varchar(200)
);
drop table if exists pge_concepts_l3;
create table pge_concepts_l3 (
    id varchar(200) unique,
    level2_id varchar(200),
    level3 varchar(200)
);
drop table if exists pge_concepts;
create table pge_concepts (
    id varchar(200) unique,
    level3_id varchar(200),
    name varchar(200)
);

drop table if exists pge_expenses;
create table pge_expenses (
    id varchar(128) unique,
    
    date_year integer,
    pge_organism_id varchar(200),
    pge_group_id varchar(200),
    pge_concept_id varchar(200),
    
    concept varchar(200),
    
    amount real,
    amount_per_capita real
);
