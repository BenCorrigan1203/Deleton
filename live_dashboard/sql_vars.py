"""storing SQL as variables for use in pages"""

CURRENT_RIDER_SQL = """
SELECT first_name, last_name, gender, date_of_birth
FROM rider
JOIN ride on ride.rider_id = rider.rider_id
ORDER BY start_time DESC
LIMIT 1;"""

RECENT_RIDES_SQL = """
SELECT * FROM ride
JOIN rider ON rider.rider_id = ride.rider_id
WHERE AGE(ride.end_time, now()) <= INTERVAL '12 hours';"""