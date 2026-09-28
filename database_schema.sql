create database production_maintenance_db;
use  production_maintenance_db;

create table departments(
department_id int primary key auto_increment,
department_name varchar(100) not null unique
);

create table machines( 
machine_id int primary key auto_increment,
machine_name varchar(100) not null ,
department_id int not null,
machine_type varchar(100),
status varchar (50) default "running",
installation_date date ,
foreign key (department_id) references departments(department_id)
);

create table products (
product_id int primary key auto_increment,product_name varchar (100) not null unique,
product_type varchar(100),
unit varchar(20) default 'MT' 
);



create table shifts(
shift_id int primary key auto_increment ,
shift_name varchar (5) not null unique,
start_time time,
end_time time
);
 desc shifts;

create table production_records( 
production_id int primary key auto_increment,
 production_date date not null,
 shift_id int not null ,
 machine_id int not null,
 product_id int not null,
 target_qty decimal (10,2) not null,
 actual_qty decimal (10,2) not null,
 good_qty decimal (10,2) not null,
 rejected_qty decimal (10,2) default 0,
 foreign key (shift_id) references shifts(shift_id),
 foreign key(machine_id) references machines(machine_id),
 foreign key (product_id) references products(product_id));
 
create table breakdowns(
breakdown_id int primary key auto_increment,
machine_id int not null,
breakdown_date date not null,
start_time datetime not null ,
end_time datetime,
breakdown_reason varchar (255) not null,
root_cause varchar (255),
downtime_hours decimal(10,2),
foreign key(machine_id) references machines(machine_id)
);

create table maintenance_record(
maintenance_id int primary key auto_increment,
machine_id int not null ,
maintenance_date date not null ,
maintenance_type varchar(50) not null ,
description varchar(255) ,
technician_name varchar(100),
repair_hours  decimal (10,2),
maintenance_cost decimal(10,2) default 0,
foreign key (machine_id ) references machines(machine_id));
desc maintenance_record;

create table machine_schedule(
schedule_id int primary key auto_increment,
machine_id int not null,
maintenance_task varchar (255) not null,
frequency_days int not null ,
last_maintenance_date date ,
next_maintenance_date date not null,
status varchar(255) default 'Scheduled',
foreign key(machine_id) references machines(machine_id));

create table quality_records (
quality_id int primary key auto_increment,
production_id int not null ,
inspection_date date not null,
good_qty decimal(10,2) default 0,
rejection_reason varchar(255),
foreign key (production_id) references production_records(production_id));

insert into departments (department_name)
values
('Production'),
('Maintenance'),
('Quality'),
('Packaging'),
('Utilities');

select*from departments;

insert into  machines
(machine_name, department_id, machine_type, status, installation_date)
values
('Cattle Feed Hammer Mill', 1, 'Vertical Hammer Mill', 'Running', NULL),
('Poultry Feed Hammer Mill 1', 1, 'Horizontal Hammer Mill', 'Running', NULL),
('Poultry Feed Hammer Mill 2', 1, 'Horizontal Hammer Mill', 'Running', NULL),
('Double Shaft Paddle Mixer', 1, 'Mixer', 'Running', NULL),
('Steam Conditioning Chamber', 1, 'Conditioner', 'Running', NULL),
('Pellet Press', 1, 'Pellet Mill', 'Running', NULL),
('Counter Flow Cooler', 1, 'Cooler', 'Running', NULL),
('Rotary Screener', 1, 'Screener', 'Running', NULL),
('Crumbler', 1, 'Crumbler', 'Running', NULL),
('Packing Machine', 4, 'Packing Equipment', 'Running', NULL),
('Boiler 1', 5, 'Boiler', 'Running', '2021-06-30');

insert into products(product_name,product_type,unit) values
('Cattle feed','Cattle Feed','MT'),
('Poultry feed','Poultry Feed','MT');

insert into shifts(shift_name,start_time,end_time)
values 
('A', '07:00:00', '15:00:00'),
('B', '15:00:00', '23:00:00'),
('C', '23:00:00', '07:00:00');

SELECT * FROM products;
SELECT * FROM shifts;

INSERT INTO production_records
(production_date, shift_id, machine_id, product_id,
 target_qty, actual_qty, good_qty, rejected_qty)
VALUES
('2026-09-01', 1, 1, 1, 100.00, 95.00, 92.00, 3.00),
('2026-09-01', 2, 1, 1, 100.00, 98.00, 96.00, 2.00),
('2026-09-01', 3, 2, 2, 120.00, 115.00, 112.00, 3.00),
('2026-09-02', 1, 3, 1, 110.00, 105.00, 102.00, 3.00),
('2026-09-02', 2, 6, 2, 130.00, 125.00, 121.00, 4.00),
('2026-09-02', 3, 7, 2, 120.00, 118.00, 116.00, 2.00);

insert into breakdowns(machine_id,breakdown_date,start_time,end_time,breakdown_reason,root_cause,downtime_hours)
values
(1, '2026-09-01', '2026-09-01 10:30:00', '2026-09-01 12:00:00',
 'Excessive vibration', 'Worn bearing', 1.50),

(2, '2026-09-01', '2026-09-01 18:00:00', '2026-09-01 19:30:00',
 'Low grinding output', 'Screen blockage', 1.50),

(6, '2026-09-02', '2026-09-02 16:00:00', '2026-09-02 18:00:00',
 'Pellet quality variation', 'Die wear', 2.00),

(7, '2026-09-02', '2026-09-02 23:30:00', '2026-09-03 00:30:00',
 'High temperature', 'Cooling fan issue', 1.00);
 
 SHOW TABLES;
 
 
insert into maintenance_record
(machine_id, maintenance_date, maintenance_type,
 description, technician_name, repair_hours, maintenance_cost)
 values 
 (1, '2026-09-01', 'Corrective',
 'Replaced worn bearing and checked shaft alignment',
 'Rahul Patil', 2.00, 4500.00),

(2, '2026-09-01', 'Corrective',
 'Cleaned and replaced blocked screen',
 'Amit Jadhav', 1.50, 2500.00),

(6, '2026-09-02', 'Corrective',
 'Inspected pellet die and replaced worn die',
 'Suresh More', 2.50, 8500.00),

(7, '2026-09-03', 'Corrective',
 'Checked cooling fan and replaced damaged component',
 'Vijay Shinde', 1.50, 3200.00);
 
 SELECT * FROM maintenance_record;
 
 insert into machine_schedule(machine_id, maintenance_task, frequency_days,
 last_maintenance_date, next_maintenance_date, status)
 values 
 (1, 'Check hammer mill bearings and vibration', 30,
 '2026-08-01', '2026-08-31', 'Scheduled'),

(2, 'Inspect hammer mill screen and bearings', 30,
 '2026-08-05', '2026-09-04', 'Scheduled'),

(3, 'Inspect hammer mill screen and bearings', 30,
 '2026-08-05', '2026-09-04', 'Scheduled'),

(4, 'Inspect mixer paddles and gearbox', 30,
 '2026-08-10', '2026-09-09', 'Scheduled'),

(5, 'Inspect steam conditioning system', 30,
 '2026-08-10', '2026-09-09', 'Scheduled'),

(6, 'Inspect pellet die and rollers', 15,
 '2026-08-20', '2026-09-04', 'Scheduled'),
 (7, 'Inspect cooler fan and temperature system', 30,
 '2026-08-15', '2026-09-14', 'Scheduled'),

(8, 'Inspect screener mesh and drive system', 30,
 '2026-08-15', '2026-09-14', 'Scheduled'),

(9, 'Inspect crumbler rollers and bearings', 30,
 '2026-08-20', '2026-09-19', 'Scheduled'),

(10, 'Inspect packing machine and sealing unit', 30,
 '2026-08-20', '2026-09-19', 'Scheduled'),

(11, 'Inspect boiler safety and operating system', 30,
 '2026-08-01', '2026-08-31', 'Scheduled');
 
 insert into quality_records(production_id, inspection_date, good_qty, rejection_reason)
 values 
 (1, '2026-09-01', 92.00, 'Minor moisture variation'),
(2, '2026-09-01', 96.00, 'Minor particle size variation'),
(3, '2026-09-01', 112.00, 'Minor grinding variation'),
(4, '2026-09-02', 102.00, 'Minor moisture variation'),
(5, '2026-09-02', 121.00, 'Minor pellet quality variation'),
(6, '2026-09-02', 116.00, 'Minor cooling variation');

select 
production_id,
production_date,
target_qty,
actual_qty,
round((actual_qty/target_qty)*100,2) as efficiency_percentage
from production_records;

select pr.production_id,
pr.production_date,
m.machine_name,
p.product_name,
s.shift_name,
pr.target_qty,
pr.actual_qty,
ROUND((pr.actual_qty / pr.target_qty) * 100, 2) AS efficiency_percentage
from production_records pr 
join machines m 
	on pr.machine_id = m.machine_id
    join products p
    on pr.product_id = p.product_id
    join shifts s
    on pr.shift_id = s.shift_id;

USE production_maintenance_db;

USE production_maintenance_db;

SELECT 
    production_id,
    production_date,
    shift_id,
    machine_id,
    product_id,
    target_qty,
    actual_qty,
    good_qty,
    rejected_qty
FROM production_records
ORDER BY production_id DESC;

SELECT COUNT(*) AS total_records
FROM production_records;