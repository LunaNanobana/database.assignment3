CREATE TABLE "user_account" (
  user_id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  given_name VARCHAR(100) NOT NULL,
  surname VARCHAR(100) NOT NULL,
  city VARCHAR(100),
  phone_number VARCHAR(50),
  profile_description TEXT,
  password VARCHAR(255) NOT NULL
);

CREATE TABLE caregiver (
  caregiver_user_id INTEGER PRIMARY KEY REFERENCES user_account(user_id) ON DELETE CASCADE,
  photo TEXT,
  gender VARCHAR(10),
  caregiving_type VARCHAR(50),
  hourly_rate NUMERIC(6,2)
);

CREATE TABLE member (
  member_user_id INTEGER PRIMARY KEY REFERENCES user_account(user_id) ON DELETE CASCADE,
  house_rules TEXT,
  dependent_description TEXT
);

CREATE TABLE address (
  address_id SERIAL PRIMARY KEY,
  member_user_id INTEGER REFERENCES member(member_user_id) ON DELETE CASCADE,
  house_number VARCHAR(20),
  street VARCHAR(200),
  town VARCHAR(100)
);

CREATE TABLE job (
  job_id SERIAL PRIMARY KEY,
  member_user_id INTEGER REFERENCES member(member_user_id) ON DELETE CASCADE,
  required_caregiving_type VARCHAR(50),
  other_requirements TEXT,
  date_posted DATE DEFAULT CURRENT_DATE
);

CREATE TABLE job_application (
  application_id SERIAL PRIMARY KEY,
  caregiver_user_id INTEGER REFERENCES caregiver(caregiver_user_id) ON DELETE CASCADE,
  job_id INTEGER REFERENCES job(job_id) ON DELETE CASCADE,
  date_applied DATE DEFAULT CURRENT_DATE
);

CREATE TABLE appointment (
  appointment_id SERIAL PRIMARY KEY,
  caregiver_user_id INTEGER REFERENCES caregiver(caregiver_user_id) ON DELETE CASCADE,
  member_user_id INTEGER REFERENCES member(member_user_id) ON DELETE CASCADE,
  appointment_date DATE,
  appointment_time TIME,
  work_hours INTEGER,
  status VARCHAR(20)
);




INSERT INTO user_account (user_id,email, given_name, surname, city, phone_number, profile_description, password)
VALUES
(1,'arman@example.com','Arman','Armanov','Astana','+77770001111','Experienced caregiver specializing in elderly support and mobility assistance.','pass1'),
(2,'amina@example.com','Amina','Aminova','Astana','+77770002222','Compassionate caregiver who enjoys helping seniors with daily tasks.','pass2'),
(3,'john.doe@example.com','John','Doe','Almaty','+77770003333','Energetic babysitter with 3 years of experience working with children.','pass3'),
(4,'sara.k@example.com','Sara','Kairbekova','Astana','+77770004444','Creative and patient caregiver who loves working with toddlers.','p4'),
(5,'olga.n@example.com','Olga','Nurzhanova','Astana','+77770005555','Reliable caregiver with experience supporting elderly individuals.','p5'),
(6,'lia.p@example.com','Lia','Petrova','Astana','+77770006666','Babysitter passionate about early childhood development.','p6'),
(7,'mira.q@example.com','Mira','Qurbanbekova','Almaty','+77770007777','Caregiver with strong communication skills and a calm personality.','p7'),
(8,'zhan.r@example.com','Zhan','Rakhimov','Astana','+77770008888','Elderly care assistant with training in first aid and daily living support.','p8'),
(9,'dana.s@example.com','Dana','Sultanova','Astana','+77770009999','Playmate and babysitter who enjoys creative activities with kids.','p9'),
(10,'tima.t@example.com','Tima','Talgatov','Almaty','+77770001010','Caregiver focused on creating safe and engaging environments.','p10');


INSERT INTO caregiver (caregiver_user_id, photo, gender, caregiving_type, hourly_rate)
VALUES
(1,'/photos/a1.jpg','male','elderly',9.50),
(3,'/photos/j1.jpg','male','babysitter',12.00),
(4,'/photos/s1.jpg','female','babysitter',8.00),
(5,'/photos/o1.jpg','female','playmate',11.00),
(6,'/photos/l1.jpg','female','elderly',7.50),
(7,'/photos/m1.jpg','female','babysitter',10.00),
(8,'/photos/z1.jpg','male','elderly',15.00),
(9,'/photos/d1.jpg','female','playmate',9.00),
(10,'/photos/t1.jpg','male','babysitter',13.00),
(2,'/photos/a2.jpg','female','elderly',6.00);


INSERT INTO member (member_user_id, house_rules, dependent_description)
VALUES
(2, 'No pets.', 'My mother, 78, needs help with daily activities'),
(1, 'No smoking. No pets.', '5-year old son'),
(4, 'No shoes indoors.', 'Toddler, 2 years'),
(5, 'No late nights', 'Elderly - mobility issues'),
(6, 'No pets. No smoking', 'Child - 4'),
(7, 'No pets', 'Elderly - Alzheimer care'),
(8, 'No pets', 'Child - likes painting'),
(9, 'No pets', 'Elderly - needs daytime assistance'),
(10, 'No pets', 'Child - special needs'),
(3, 'No pets','Elderly');

INSERT INTO address (member_user_id, house_number, street, town)
VALUES
(2,'12','Kabanbay Batyr','Astana'),
(1,'34','Saryarka','Astana'),
(4,'56','Abay','Astana'),
(5,'78','Kabanbay Batyr','Astana'),
(6,'90','Zhambyl','Astana'),
(7,'101','Tauelsizdik','Almaty'),
(8,'11','Kabanbay Batyr','Astana'),
(9,'22','Abylay','Almaty'),
(10,'33','Suleiman','Astana'),
(3,'44','Kabanbay Batyr','Astana');

INSERT INTO job (job_id, member_user_id, required_caregiving_type, other_requirements, date_posted)
VALUES
(1,2,'elderly','Must be experienced', '2025-11-01'),
(2,1,'babysitter','must be playful', '2025-11-02'),
(3,4,'babysitter','soft-spoken preferred', '2025-11-03'),
(4,5,'elderly','morning shifts only', '2025-11-04'),
(5,6,'babysitter','weekends only', '2025-11-05'),
(6,7,'elderly','no smoking, soft-spoken', '2025-11-06'),
(7,8,'playmate','arts & crafts', '2025-11-06'),
(8,9,'elderly','overnight possible', '2025-11-07'),
(9,10,'babysitter','3 hours per day', '2025-11-08'),
(10,3,'elderly','short commute', '2025-11-09');

INSERT INTO job_application (caregiver_user_id, job_id, date_applied)
VALUES
(1,1,'2025-11-02'),
(3,2,'2025-11-03'),
(4,3,'2025-11-04'),
(6,1,'2025-11-05'),
(5,5,'2025-11-06'),
(8,7,'2025-11-06'),
(9,4,'2025-11-07'),
(10,2,'2025-11-08'),
(2,1,'2025-11-08'),
(7,9,'2025-11-09');

INSERT INTO appointment (caregiver_user_id, member_user_id, appointment_date, appointment_time, work_hours, status)
VALUES
(1,2,'2025-11-10','09:00',3,'accepted'),
(3,1,'2025-11-12','14:00',4,'pending'),
(4,4,'2025-11-12','10:00',2,'accepted'),
(6,2,'2025-11-15','09:00',5,'declined'),
(5,7,'2025-11-16','08:00',3,'accepted'),
(8,9,'2025-11-17','10:00',2,'accepted'),
(9,3,'2025-11-18','12:00',3,'pending'),
(10,10,'2025-11-19','15:00',4,'accepted'),
(2,2,'2025-11-20','11:00',2,'accepted'),
(7,5,'2025-11-21','09:00',3,'accepted');
