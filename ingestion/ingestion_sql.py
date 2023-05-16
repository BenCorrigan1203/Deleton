"""file for storing sql commands as variable"""

ADDRESS_SQL = """INSERT INTO rider_address 
(house_no, street_name, city, postcode) 
VALUES (%s, %s, %s, %s)
ON CONFLICT DO NOTHING
RETURNING address_id;"""

RIDER_SQL = """INSERT INTO rider
(rider_id, first_name, last_name, gender, address_id, date_of_birth, email,
height_cm, weight_cm, account_creation_date)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING
"""

RIDE_SQL = """INSERT INTO ride
(bike_serial, rider_id, start_time)
VALUES (%s, %s, %s)
ON CONFLICT DO NOTHING
RETURNING ride_id"""

METADATA_SQL = """INSERT INTO ride_metadata
(heart_rate, rpm, power, duration, resistance, recording_taken, ride_id)
VALUES = %s"""