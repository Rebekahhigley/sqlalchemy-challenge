# Import the dependencies.
import numpy as np
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from flask import Flask

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


#################################################
# Database Setup
#################################################
Base = automap_base()
# reflect an existing database into a new model
Base.prepare(autoload_with=engine, reflect=True)
# reflect the tables
Base.classes.keys()

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# # Create our session (link) from Python to the DB
# session = Session(engine)

#################################################
# Flask Setup
#################################################

# 2. Instantiate the Flask class to create an application instance
# __name__ is a special variable in Python that is automatically set to the name of the module in which it is used.
# Flask uses __name__ to know where to find other resources such as template files.
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#1.  /

# Start at the homepage.

# List all the available routes.
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/precipitation<br/>"
        f"/stations<br/>"
        f"/tobs<br/>"
        f"/start<br/>"
        f"/start/end"
    )

#2.  /api/v1.0/precipitation

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.

# Return the JSON representation of your dictionary.
@app.route("/precipitation")
def prcp():
    # Create a session (link) from Python to the DB
    session = Session(engine)
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcp_results= session.query(measurement.date, measurement.prcp).filter(measurement.date > previous_year).all()
    # results = session.query().all()
    session.close()
    # print(results)
    station_prcp = []  
    for date, prcp in prcp_results:
        station_prcp_dict= {}
        station_prcp_dict["date"] = date
        station_prcp_dict["prcp"] = prcp
        station_prcp.append(station_prcp_dict)
    return jsonify(station_prcp)


#3.  /api/v1.0/stations

# Return a JSON list of stations from the dataset.
@app.route("/stations")
def stations():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    station_results = session.query(station.station).all()
    session.close()

    station_results = list(np.ravel(station_results))
    return jsonify(station_results)

#4. /api/v1.0/tobs

# Query the dates and temperature observations of the most-active station for the previous year of data.

# Return a JSON list of temperature observations for the previous year.

@app.route("/tobs")
def temp():
    # create session
    session = Session(engine)
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobs_results = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date > previous_year).all()
    # results = session.query().all()
    session.close()
    # print(results)
    station_tobs = []  
    for date, tempeture in tobs_results:
        station_tobs_dict= {}
        station_tobs_dict["date"] = date
        station_tobs_dict["tobs"] = tempeture
        station_tobs.append(station_tobs_dict)
    return jsonify(station_tobs)


#5. /api/v1.0/<start> and /api/v1.0/<start>/<end>

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/<start>/<end>")
@app.route("/<start>")
def date(start = None, end = None):
    # create session
    session = Session(engine)
    start = dt.datetime.strptime(start, '%Y-%m-%d')

    if not end:
        analyse_temp = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date > start).all()
    else:
        end = dt.datetime.strptime(end, '%Y-%m-%d')
        analyse_temp = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date < end).filter(measurement.date > start).all()
    # results = session.query().all()
    session.close()
    # print(results)
    # print(start)
    # print(end)
    analyse = []  
    for tmin, tmax, tavg in analyse_temp:
        analyse_dict= {}
        analyse_dict["tmin"] = tmin
        analyse_dict["tavg"] = tavg
        analyse_dict["tmax"] = tmax
        analyse.append(analyse_dict)
    return jsonify(analyse)



# https://www.digitalocean.com/community/tutorials/python-string-to-datetime-strptime

if __name__ == "__main__":
    # app.run() starts the web server. 
    # The 'debug=True' argument enables debug mode, providing detailed error messages in the browser when things go wrong.
    app.run(debug=True)



