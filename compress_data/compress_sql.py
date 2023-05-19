

DAILY_SCHEMA = "daily"
HISTORICAL_SCHEMA = "historical"

ADDRESS_SQL = f"""
            INSERT INTO {HISTORICAL_SCHEMA}.rider_address (address_id, house_no, street_name, city, postcode)
            SELECT * FROM {DAILY_SCHEMA}.rider_address
            WHERE address_id IN(
                SELECT address_id FROM {DAILY_SCHEMA}.rider
                JOIN {DAILY_SCHEMA}.ride ON {DAILY_SCHEMA}.rider.rider_id = {DAILY_SCHEMA}.ride.rider_id
                WHERE ride.end_time >= now() - INTERVAL '24 hours'
            )
            ON CONFLICT DO NOTHING;"""

RIDER_SQL = f"""
            INSERT INTO {HISTORICAL_SCHEMA}.rider (rider_id, first_name, last_name, gender, address_id, date_of_birth, email, height_cm, weight_kg, account_creation_date)
            SELECT * FROM {DAILY_SCHEMA}.rider
            WHERE rider_id IN(
                SELECT rider.rider_id FROM {DAILY_SCHEMA}.rider
                JOIN {DAILY_SCHEMA}.ride ON {DAILY_SCHEMA}.rider.rider_id = {DAILY_SCHEMA}.ride.rider_id
                WHERE ride.end_time >= now() - INTERVAL '24 hours'
            )
            ON CONFLICT DO NOTHING;"""

METADATA_SQL = f"""
            SELECT
                AVG(ride_metadata.rpm) AS RPM_AVG,
                MAX(ride_metadata.rpm) AS RPM_MAX,
                MIN(ride_metadata.rpm) AS RPM_MIN,
                AVG(ride_metadata.resistance) AS resistance_AVG,
                MAX(ride_metadata.resistance) AS resistance_MAX,
                MIN(ride_metadata.resistance) AS resistance_MIN,
                AVG(ride_metadata.power) AS power_AVG,
                MAX(ride_metadata.power) AS power_MAX,
                MIN(ride_metadata.power) AS power_MIN,
                AVG(ride_metadata.heart_rate) AS heart_AVG,
                MAX(ride_metadata.heart_rate) AS heart_MAX,
                MIN(ride_metadata.heart_rate) AS heart_MIN,
                ride_metadata.ride_id
            FROM {DAILY_SCHEMA}.ride_metadata
            JOIN {DAILY_SCHEMA}.ride ON {DAILY_SCHEMA}.ride_metadata.ride_id = {DAILY_SCHEMA}.ride.ride_id
            WHERE ride.end_time >= now() - INTERVAL '24 hours'
            GROUP BY ride_metadata.ride_id;"""

RESISTANCE_SQL = f"""
                WITH ins AS (
                    INSERT INTO {HISTORICAL_SCHEMA}.resistance (avg_resistance, max_resistance, min_resistance)
                    VALUES (%s,%s,%s)
                    ON CONFLICT DO NOTHING
                    RETURNING resistance_id
                )
                SELECT resistance_id FROM ins
                UNION ALL
                    SELECT resistance_id FROM {HISTORICAL_SCHEMA}.resistance
                    WHERE avg_resistance = %s
                        AND max_resistance = %s
                        AND min_resistance = %s;"""

POWER_SQL = f"""
        WITH ins AS (
            INSERT INTO {HISTORICAL_SCHEMA}.power_w (avg_power, max_power, min_power)
            VALUES (%s,%s,%s)
            ON CONFLICT DO NOTHING
            RETURNING power_id
        )
        SELECT power_id FROM ins
        UNION ALL
            SELECT power_id FROM {HISTORICAL_SCHEMA}.power_w
            WHERE avg_power = %s
                AND max_power = %s
                AND min_power = %s;"""

HEART_SQL = f"""
        WITH ins AS (
            INSERT INTO {HISTORICAL_SCHEMA}.heart_rate (avg_heart_rate, max_heart_rate, min_heart_rate)
            VALUES (%s,%s,%s)
            ON CONFLICT DO NOTHING
            RETURNING heart_rate_id
            )
        SELECT heart_rate_id FROM ins
        UNION ALL
            SELECT heart_rate_id FROM {HISTORICAL_SCHEMA}.heart_rate
            WHERE avg_heart_rate = %s
                AND max_heart_rate = %s
                AND min_heart_rate = %s;"""

RPM_SQL = f"""
        WITH ins AS (
            INSERT INTO {HISTORICAL_SCHEMA}.rpm (avg_rpm, max_rpm, min_rpm)
            VALUES (%s,%s,%s)
            ON CONFLICT DO NOTHING
            RETURNING rpm_id
            )
        SELECT rpm_id FROM ins
        UNION ALL
            SELECT rpm_id FROM {HISTORICAL_SCHEMA}.rpm
            WHERE avg_rpm = %s
                AND max_rpm = %s
                AND min_rpm = %s;"""

RIDE_SQL = f"""SELECT start_time, end_time, rider_id, bike_serial FROM {DAILY_SCHEMA}.ride WHERE ride_id = %s"""

RIDE_INFO_SQL = f"""
            INSERT INTO {HISTORICAL_SCHEMA}.ride_info 
            (start_time, end_time, rider_id, bike_serial, heart_rate_id, resistance_id, power_id, rpm_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"""

DELETE_META_SQL = f"""
                DELETE FROM {DAILY_SCHEMA}.ride_metadata
                WHERE ride_id IN(
                    SELECT ride_id FROM {DAILY_SCHEMA}.ride
                    WHERE ride.end_time < now() - INTERVAL '12 hours' );

                DELETE FROM {DAILY_SCHEMA}.ride_metadata
                WHERE ride_id IN(
                    SELECT ride_id FROM {DAILY_SCHEMA}.ride
                    WHERE ride.start_time < now() - INTERVAL '12 hours'
                    AND ride.end_time IS NULL); 
               """

DELETE_RIDE_SQL = f"""
                DELETE FROM {DAILY_SCHEMA}.ride
                WHERE ride.end_time < now() - INTERVAL '12 hours';
                
                DELETE FROM {DAILY_SCHEMA}.ride
                WHERE ride.start_time < now() - INTERVAL '12 hours'
                AND ride.end_time IS NULL;"""