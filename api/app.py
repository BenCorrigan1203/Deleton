from flask import Flask, request, jsonify

import helper_functions


# Makes sure that our Flask server refers to our file ("app.py")
app = Flask(__name__)

@app.route("/", methods=["GET"])
def get_home():
    '''Return HTML of the home page'''
    return 'Hello, Welcome to the Deleton API!'

@app.route("/ride/<int:ride_id>/", methods=["GET"])
def get_rides(ride_id: int) -> dict:
    '''Get a ride using a specific ID'''
    try:
        if request.method == "GET":
            rides = helper_functions.get_rides(ride_id)
            return rides
    except ValueError:
        return jsonify({"error": True, "Message": "Internal error."}), 500
    except Exception:
        return jsonify({"error": True, "Message": "Internal error."}), 405

@app.route("/rider/<int:rider_id>/", methods=["GET"])
def get_rider(rider_id: int) -> dict:
    '''Get riders information '''
    try:
        rider = helper_functions.get_riders(rider_id)
        data = {"Rider's Information": rider,"success": True}
        return data, 200
    except ValueError:
        return jsonify({"error": True, "Message": "Internal error."}), 500
    except Exception:
        return jsonify({"error": True, "Message": "Internal error."}), 405

@app.route("/rider/<int:rider_id>/rides/", methods=["GET"])
def get_rider_rides(rider_id: int) -> dict:
    '''Get all rides for a rider with a specific ID'''
    try:
        rider = helper_functions.get_all_riders_rides(rider_id)
        data = {"Rider's Rides": rider,"success": True}
        return data, 200
    except ValueError:
        return jsonify({"error": True, "Message": "Internal error."}), 500
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
                data = {"Todays Rides": rides_by_date,"success": True}
                return data, 200
            except ValueError:
                return jsonify({"error": True, "Message": "Internal error."}), 500
            except Exception:
                return jsonify({"error": True, "Message": "Internal error."}), 405
        else:
            try:
                daily_rides = helper_functions.get_daily_rides()
                data = {"Todays Rides": daily_rides,"success": True, "args": args}
                return data, 200
            except ValueError:
                return jsonify({"error": True, "Message": "Internal error.", "args": "args"}), 500
            except Exception:
                return jsonify({"error": True, "Message": "Internal error."}), 405

if __name__== '__main__':
    app.run(debug=True)
