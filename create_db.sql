SET SEARCH_PATH=daily;

DROP TABLE IF EXISTS rider_address CASCADE;
DROP TABLE IF EXISTS rider CASCADE;
DROP TABLE IF EXISTS ride CASCADE;
DROP TABLE IF EXISTS rider_metadata CASCADE;


CREATE TABLE IF NOT EXISTS rider_address (
    address_id INT GENERATED ALWAYS AS IDENTITY,
    house_no VARCHAR(20) NOT NULL,
    street_name VARCHAR(20) NOT NULL,
    city VARCHAR(20) NOT NULL,
    postcode VARCHAR(10) NOT NULL,
    PRIMARY KEY (address_id)
);

CREATE TABLE IF NOT EXISTS rider (
    rider_id INT NOT NULL,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    address_id INT NOT NULL,
    date_of_birth TIMESTAMP NOT NULL,
    email VARCHAR(50) NOT NULL,
    height_cm INT NOT NULL,
    weight_kg INT NOT NULL,
    account_creation_date TIMESTAMP NOT NULL,
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
