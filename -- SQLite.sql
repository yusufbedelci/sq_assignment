-- SQLite
PRAGMA foreign_keys = ON;
INSERT INTO user (assigned_role_id, name, lastname, age, gender, weight, email, mobile, password)
VALUES (1,'Arief', '', 20, 'male',200,'test2@test.nl',0612341566,'test1234');


PRAGMA foreign_keys = ON;
INSERT INTO role (role_id,name)
VALUES (1,'admin');

PRAGMA foreign_keys = ON;
INSERT INTO user_role(user_id, role_id) VALUES (1,1);

INSERT INTO address (streetname, house_number, zipcode, city)
VALUES ('Bakerstreet', 102, 4010, 'New York');

INSERT INTO membership (user_id, registration_date)
VALUES (1,'1-6-2024');