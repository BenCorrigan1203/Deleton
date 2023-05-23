DROP DATABASE deleton;

CREATE DATABASE deleton;

\c deleton

CREATE SCHEMA daily;

SET SEARCH_PATH=daily;

CREATE TABLE IF NOT EXISTS rider_address (
    address_id INT GENERATED ALWAYS AS IDENTITY,
    house_no VARCHAR(20),
    street_name VARCHAR(50),
    city VARCHAR(30),
    postcode VARCHAR(10),
    PRIMARY KEY (address_id),
    UNIQUE (house_no, street_name, city, postcode)
);

CREATE TABLE IF NOT EXISTS rider (
    rider_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    address_id INT NOT NULL,
    date_of_birth DATE NOT NULL,
    email VARCHAR(50) NOT NULL,
    height_cm INT NOT NULL,
    weight_kg INT NOT NULL,
    account_creation_date DATE NOT NULL,
    PRIMARY KEY (rider_id),
    FOREIGN KEY (address_id)
    REFERENCES rider_address(address_id)
);

CREATE TABLE IF NOT EXISTS ride (
    ride_id INT GENERATED ALWAYS AS IDENTITY,
    bike_serial VARCHAR(10) NOT NULL,
    rider_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    PRIMARY KEY (ride_id),
    FOREIGN KEY (rider_id)
    REFERENCES rider(rider_id)
);

CREATE TABLE IF NOT EXISTS ride_metadata (
    ride_metadata_id INT GENERATED ALWAYS AS IDENTITY,
    heart_rate INT NOT NULL,
    rpm INT NOT NULL,
    power DECIMAL NOT NULL,
    duration DECIMAL NOT NULL,
    resistance INT NOT NULL,
    recording_taken TIMESTAMP NOT NULL,
    ride_id INT NOT NULL,
    PRIMARY KEY (ride_metadata_id),
    FOREIGN KEY (ride_id)
    REFERENCES ride(ride_id)
);

CREATE SCHEMA historical;

SET SEARCH_PATH=historical;

CREATE TABLE IF NOT EXISTS rider_address 
(address_id INT NOT NULL,
house_no VARCHAR(20),
street_name VARCHAR(50),
city VARCHAR(25),
postcode VARCHAR(10),
PRIMARY KEY (address_id),
UNIQUE (house_no, street_name, city, postcode));


CREATE TABLE IF NOT EXISTS rider
(rider_id INT NOT NULL,
first_name VARCHAR(50) NOT NULL,
last_name VARCHAR(50) NOT NULL,
gender VARCHAR(10) NOT NULL,
address_id INT NOT NULL,
date_of_birth DATE NOT NULL,
email VARCHAR(150) NOT NULL,
height_cm INT NOT NULL,
weight_kg INT NOT NULL,
account_creation_date DATE NOT NULL,
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
