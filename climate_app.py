import numpy as np

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes['measurement']
Station = Base.classes['station']

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp_stats_start/yyyy-mm-dd<br/>"
        f"/api/v1.0/temp_stats_start_end/yyyy-mm-dd/yyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns a list of precipitation data for one year beginning on 2016-08-23"""
    # Query all stations for precitation data for one year from beginning date
    begin_date = dt.date(2016, 8, 23)
    results = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date>=begin_date).all()
    session.close()

    prcp_list = [results]
    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of Station ID's with corresponding Station Names"""
    # Query all stations and return station id and name
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates and temperature observations of the most active station for the last year of data"""
    # Query station station_id USC00519281 for the last year of temperature observations
    station_id = 'USC00519281'
    begin_date = dt.date(2016, 8, 18)
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.station\
                    == station_id).filter(Measurement.date >= begin_date).order_by(Measurement.date).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_tobs
    all_tobs = []
    for station, date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/temp_stats_start/<start_date>/")
def temp_stats_start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the min temperature, the avg temperature, and the max temperature for a given start date"""
    # Query temperature observations for all stations with given start date   
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
     func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
  
    session.close()

    # Create a dictionary from the row data and append to a list of all_tobs
    temp_stats = []
    for result in results:
        dict_row = {}
        dict_row['Start Date'] = start_date
        dict_row['Minimum Temperature'] = (result[0])
        dict_row['Average Temperature'] = (result[1])
        dict_row['Maximum Temperature'] = (result[2])
        temp_stats.append(dict_row)

    return jsonify(temp_stats)


@app.route("/api/v1.0/temp_stats_start_end/<start_date>/<end_date>")
def temp_stats_start_end(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the min temperature, the avg temperature, and the max temperature for a given start date and end date"""
    # Query temperature observations for all stations with given start and end dates   
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
     func.max(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
  
    session.close()

    # Create a dictionary from the row data and append to a list of all_tobs
    temp_stats_end = []
    for result in results:
        dict_row = {}
        dict_row['Start Date'] = start_date
        dict_row['End Date'] = end_date
        dict_row['Minimum Temperature'] = (result[0])
        dict_row['Average Temperature'] = (result[1])
        dict_row['Maximum Temperature'] = (result[2])
        temp_stats_end.append(dict_row)

    return jsonify(temp_stats_end)


if __name__ == '__main__':
    app.run(debug=True)