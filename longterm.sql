DROP TABLE IF EXISTS rider;
DROP TABLE IF EXISTS ride_info;
DROP TABLE IF EXISTS user_address;
DROP TABLE IF EXISTS heart_rate;
DROP TABLE IF EXISTS rpm;
DROP TABLE IF EXISTS resistance;
DROP TABLE IF EXISTS power_w;

CREATE TABLE IF NOT EXISTS rider_address 
(address_id INT GENERATED ALWAYS AS IDENTITY,
house_num VARCHAR(5),
street VARCHAR(50) NOT NULL,
city VARCHAR(25) NOT NULL,
post_code VARCHAR(8) NOT NULL,
PRIMARY KEY (address_id));


CREATE TABLE IF NOT EXISTS rider
(rider_id INT GENERATED ALWAYS AS IDENTITY,
first_name VARCHAR(50) NOT NULL,
last_name VARCHAR(50) NOT NULL,
address_id INT NOT NULL,
dob DATE NOT NULL,
email VARCHAR(150) NOT NULL,
height_cm INT NOT NULL,
weight_kg INT NOT NULL,
account_created DATE NOT NULL,
PRIMARY KEY (rider_id),
FOREIGN KEY (address_id) REFERENCES rider_address(address_id));


CREATE TABLE IF NOT EXISTS heart_rate
(heart_rate_id INT GENERATED ALWAYS AS IDENTITY,
avg_heart_rate FLOAT NOT NULL,
max_heart_rate FLOAT NOT NULL,
min_heart_rate FLOAT NOT NULL,
PRIMARY KEY (heart_rate_id));

CREATE TABLE IF NOT EXISTS power_w 
(power_id INT GENERATED ALWAYS AS IDENTITY,
avg_power FLOAT NOT NULL,
max_power FLOAT NOT NULL,
min_power FLOAT NOT NULL,
PRIMARY KEY (power_id));

CREATE TABLE IF NOT EXISTS rpm
(rpm_id INT GENERATED ALWAYS AS IDENTITY,
avg_rpm FLOAT NOT NULL,
max_rpm FLOAT NOT NULL,
min_rpm FLOAT NOT NULL,
PRIMARY KEY (rpm_id));

CREATE TABLE IF NOT EXISTS resistance
(resistance_id INT GENERATED ALWAYS AS IDENTITY,
avg_resistance FLOAT NOT NULL,
max_resistance FLOAT NOT NULL,
min_resistance FLOAT NOT NULL,
PRIMARY KEY (resistance_id));

CREATE TABLE IF NOT EXISTS ride_info
(ride_info_id INT GENERATED ALWAYS AS IDENTITY,
start_time TIMESTAMP NOT NULL,
end_time TIMESTAMP NOT NULL,
rider_id INT NOT NULL,
bike_serial VARCHAR(50) NOT NULL,
heart_rate_id INT NOT NULL,
resistance_id INT NOT NULL,
rpm_id INT NOT NULL,
power_id INT NOT NULL,
PRIMARY KEY (ride_info_id),
FOREIGN KEY (rider_id) REFERENCES rider(rider_id),
FOREIGN KEY (heart_rate_id) REFERENCES heart_rate(heart_rate_id),
FOREIGN KEY (resistance_id) REFERENCES resistance(resistance_id),
FOREIGN KEY (rpm_id) REFERENCES rpm(rpm_id),
FOREIGN KEY (power_id) REFERENCES power_w(power_id)); 