from flask import Flask, request, jsonify, render_template

import helper_functions


app = Flask(__name__)

def auth_required(function):
    '''Authentication decorator for API endpoints.'''
    def decorated(*args, **kwargs):
        api_key_auth = request.headers.get('API-Key')
        config = helper_functions.get_credentials()
        if api_key_auth in config.get("API_PASSWORD"):
            return function(*args, **kwargs)
        return jsonify({"Error": True, "Message": "Invalid API Key."}), 401
    return decorated

@app.route("/", methods=["GET"])
def get_home():
    '''Return HTML of the home page'''
    return render_template('index.html')

@app.route("/ride/<int:ride_id>/", methods=["GET"])
def get_rides(ride_id: int) -> dict:
    '''Get a ride using a specific ID'''
    try:
        if request.method == "GET":
            rides = helper_functions.get_rides(ride_id)
            if len(rides) == 0:
                return jsonify({"Ride Information":\
                                 "Currently no data to show.","success": True}), 200
            return rides
    except ValueError:
        return jsonify({"error": True, "Message": "Incorrect value entered."}), 500
    except Exception:
        return jsonify({"error": True, "Message": "Internal error."}), 405

@app.route("/ride/<int:ride_id>/", methods=["DELETE"])
@auth_required
def delete_rides(ride_id: int) -> dict:
    '''Delete a ride using a specific ID'''
    try:
        if request.method == "DELETE":
            helper_functions.get_rides(ride_id)
            return jsonify({"Deletion": True, "success": True}), 200
    except TypeError:
        return jsonify({"error": True, "Message": "Internal error."}), 500
    except Exception:
        return jsonify({"error": True, "Message": "Internal error."}), 405

@app.route("/rider/<int:rider_id>/", methods=["GET"])
def get_rider(rider_id: int) -> dict:
    '''Get riders information using a specific ID'''
    try:
        rider = helper_functions.get_riders(rider_id)
        if len(rider) == 0:
            return jsonify({"Rider's Information":\
                             "Currently no data to show.","success": True}), 200
        data = {"Rider's Information": rider,"success": True}
        return data, 200
    except ValueError:
        return jsonify({"error": True, "Message": "Incorrect value entered."}), 500
    except Exception:
        return jsonify({"error": True, "Message": "Internal error."}), 405

@app.route("/rider/<int:rider_id>/rides/", methods=["GET"])
def get_rider_rides(rider_id: int) -> dict:
    '''Get all rides for a rider using a specific ID'''
    try:
        rider = helper_functions.get_all_riders_rides(rider_id)
        if len(rider) == 0:
            return jsonify({"Rider's Rides":\
                             "Currently no data to show.","success": True}), 200
        data = {"Rider's Rides": rider,"success": True}
        return data, 200
    except ValueError:
        return jsonify({"error": True, "Message": "Incorrect value entered."}), 500
    except Exception:
        return jsonify({"error": True, "Message": "Internal error."}), 405

@app.route("/rider/<int:rider_id>/duration/", methods=["GET"])
def get_rider_rides_duration(rider_id: int) -> dict:
    '''Get all rides for a rider with a specific ID'''
    try:
        rider_durations = helper_functions.get_rider_durations(rider_id)
        if len(rider_durations) == 0:
            return jsonify({"Rider's Ride Durations":\
                             "Currently no data to show.","success": True}), 200
        data = {"Rider's Ride Durations": rider_durations,"success": True}
        return data, 200
    except ValueError:
        return jsonify({"error": True, "Message": "Incorrect value entered."}), 500
    except Exception:
        return jsonify({"error": True, "Message": "Internal error."}), 405

@app.route("/daily/", methods=["GET"])
def get_daily_rides_today() -> dict:
    '''Get all of the rides in the current day'''
    if request.method == "GET":
        args = request.args.get("date")
        if args is not None:
            try:
                rides_by_date = helper_functions.get_rides_by_date(args)
                if len(rides_by_date) == 0:
                    return jsonify({"Rides":\
                                     "Currently no data to show.","success": True}), 200
                data = {"Rides": rides_by_date,"success": True}
                return data, 200
            except ValueError:
                return jsonify({"error": True, "Message": "Incorrect value entered."}), 500
            except Exception:
                return jsonify({"error": True, "Message": "Internal error."}), 405
        else:
            try:
                daily_rides = helper_functions.get_daily_rides()
                if len(daily_rides) == 0:
                    return jsonify({"Todays Rides":\
                                     "Currently no data to show.","success": True}), 200
                data = {"Todays Rides": daily_rides,"success": True}
                return data, 200
            except ValueError:
                return jsonify({"error": True, "Message": "Incorrect value entered."}), 500
            except Exception:
                return jsonify({"error": True, "Message": "Internal error."}), 405

@app.route("/leaderboard/", methods=["GET"])
def get_leaderboard() -> dict:
    '''Get a leaderboard of most rides by riders'''
    try:
        if request.method == "GET":
            leaderboard = helper_functions.get_leaderboard()
            data = {"Leaderboard": leaderboard, "success": True}
            return data, 200
    except ValueError:
        return jsonify({"error": True, "Message": "Internal error."}), 500
    except Exception:
        return jsonify({"error": True, "Message": "Internal error."}), 405

@app.route("/city/", methods=["GET"])
def get_city_rides() -> dict:
    '''Get a rides in a specified city'''
    city = request.args.get("city")
    if city is not None:
        try:
            if request.method == "GET":
                city_rides = helper_functions.get_all_riders_rides(city)
                data = {f"Rides in {city}": city_rides, "success": True}
                return data, 200
        except ValueError:
            return jsonify({"error": True, "Message": "Internal error."}), 500
        except Exception:
            return jsonify({"error": True, "Message": "Internal error."}), 405
    else:
        try:
            cities = helper_functions.get_city()
            data = {"List of cities to search": cities, "success": True}
            return data, 200
        except ValueError:
            return jsonify({"error": True, "Message": "Internal error."}), 500
        except Exception:
            return jsonify({"error": True, "Message": "Internal error."}), 405



if __name__== '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
