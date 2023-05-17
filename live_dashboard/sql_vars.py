"""storing SQL as variables for use in pages"""

CURRENT_RIDER_SQL = """
SELECT first_name, last_name, gender, date_of_birth
FROM rider
JOIN ride on ride.rider_id = rider.rider_id
ORDER BY start_time DESC
LIMIT 1;"""

RIDE_DATA_SQL = """
SELECT duration, heart_rate
FROM ride_metadata
ORDER BY recording_taken DESC
LIMIT 1;"""

HEART_RATE_SQL = """
SELECT heart_rate, duration
FROM ride_metadata
JOIN ride on ride.ride_id = ride_metadata.ride_id
WHERE ride_metadata.ride_id = (
SELECT ride_id
FROM ride_metadata
ORDER BY recording_taken DESC
LIMIT 1
);
"""

RPM_SQL = """
SELECT rpm, duration
FROM ride_metadata
JOIN ride on ride.ride_id = ride_metadata.ride_id
WHERE ride_metadata.ride_id = (
SELECT ride_id
FROM ride_metadata
ORDER BY recording_taken DESC
LIMIT 1
);
"""

POWER_SQL = """
SELECT power, duration
FROM ride_metadata
JOIN ride on ride.ride_id = ride_metadata.ride_id
WHERE ride_metadata.ride_id = (
SELECT ride_id
FROM ride_metadata
ORDER BY recording_taken DESC
LIMIT 1
);
"""

RESISTANCE_SQL = """
SELECT resistance, duration
FROM ride_metadata
JOIN ride on ride.ride_id = ride_metadata.ride_id
WHERE ride_metadata.ride_id = (
SELECT ride_id
FROM ride_metadata
ORDER BY recording_taken DESC
LIMIT 1
);
"""