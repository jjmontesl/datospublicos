
drop table if exists dates;
create table dates (
    id varchar(128) unique,
    date_year integer,
    date_quarter integer,
    date_month integer,
    date_day integer,
    date_week integer
);


drop table if exists pcpg_company;
create table pcpg_company (
    id varchar(200) unique,
    name varchar(200)
);


drop table if exists pcpg_process;
create table pcpg_process (

    id varchar(128) unique,
    
    procedure_purpose varchar(200),

    procedure_type varchar(200),
    procedure_type_label varchar(200),
    
    procedure_contract varchar(200),
    procedure_contract_label varchar(200),
    
    procedure_state varchar(200),
    procedure_state_label varchar(200),
    
    contractor_date_provisional varchar(200),
    contractor_date_final varchar(200),
    contractor_company_id varchar(200),
    
    procedure_amount real,
    contractor_amount real
);

