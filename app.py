#Step 2 -- Climate App
#import dependencies
import numpy as np
import pandas as pd
import datetime as dt 

import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect 

from flask import Flask, jsonify 

#set up the database to query the data

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#start up Flask
app = Flask(__name__)

#set up Flask routes
#start with all avalable routes
@app.route("/")
def home ():
    """List all routes that available"""
    return(
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-01<br/>"
        f"/api/v1.0/2016-08-01/2017-08-01<br/>"
    )

#return the json rep for precipitation
@app.route('/api/v1.0/precipitation/')
def precipitation():
    #query to retrieve the precipitation levels across the last twelve months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()

    #turn the query into a dictionary
    prcp_dict = dict(precipitation_data)
    
    return jsonify(prcp_dict)

#return a JSON list of stations
@app.route('/api/v1.0/stations/')
def stations():
    active_stations = session.query(Station.station).all()
    stations_list = list(np.ravel(active_stations))

    return jsonify(stations_list)

#return a JSON list of temperature obsrvations of the most active station for the last year
@app.route('/api/v1.0/tobs/')
def tobs():
    station_tobs = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= '2016-08-23').group_by(Measurement.date).all()
    
    #create a dictionary using a for loop
    tobs_list = []
    for date, tobs in station_tobs:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

#return a JSON list of the min, max and avg of a temp on a given start date
@app.route('/api/v1.0/<start_date>/')
def start(start_date):
    start_temps = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date).all()

    #canonicalized = start_date.replace(" ", "").lower()

    date_list = []
    for min, max, avg in start_temps:
        date_dict = {}
        date_dict['min'] = min
        date_dict['max'] = max
        date_dict['avg'] = avg
        date_list.append(date_dict)
   
    return jsonify(date_list)

#return a JSON list of the min, max and avg for date between the start and end date incl
@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    start_end_date = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

#canonicalized = start.replace(" ", "").lower()

    date_list_end = []
    for min, max, avg in start_end_date:
        date_dict = {}
        date_dict['min'] = min
        date_dict['max'] = max
        date_dict['avg'] = avg
        date_list_end.append(date_dict)

    return jsonify(date_list_end)

session.close()

if __name__ == '__main__':
    app.run(debug = True)