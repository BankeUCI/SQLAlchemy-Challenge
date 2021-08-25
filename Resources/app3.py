from time import strftime
from flask import Flask, jsonify
import sqlite3
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
import pandas as pd
import numpy as np
import datetime as dt

#######################################################
# Database Setup
#######################################################

engine = create_engine("sqlite:///hawaii.sqlite") 

# Reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Classes automap found
#Base.classes.keys()
metadata = MetaData()

# Save reference to table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from python to the DB
session = Session(engine)

#############################################################
# Flask Setup
#############################################################

app = Flask(__name__)

################################
# Flask Routes
################################

@app.route("/")
def Home():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Calculating date range for previous year date and last date in database

def date_calc():
    latest_date = session.query(func.max(Measurement.date)).all()

    # One year date range
    today = dt.date.today()
    # format date
    latest_date_fmt = today.replace(year=int(latest_date[0][0][:4]),\
                                    month=int(latest_date[0][0][5:7]),\
                                    day=int(latest_date[0][0][8:]))
    
    # One year ago from latest_date
    year_ago = latest_date_fmt-dt.timedelta(days=365)
    year_end = latest_date_fmt-strftime("%Y-%m-%d")
    startdate_year = year_ago.strftime("%Y-%m-%d")

    year_list = [startdate_year, year_end]
    return(tuple(year_list))

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Start date and end date of previous year using date_calc function
    range = date_calc()
    end_date = range[1]
    start_date = range[0]

    # Converting query results to a dictionary using `date` as the key and `prcp` as the value
    results = session.query(Measurement.date, Measurement.station, Measurement.prcp).\
                            filter(Measurement.date <= end_date).\
                                filter(Measurement.date >= start_date).all()
   
    # Return the JSON representation of your dictionary.
    list = []
    for result in results:
        dict = {"Date":result[0],"Station":result[1],"Precipitation":result[2]}
        list.append(dict)
    return jsonify(list)

 # Returning a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station, Station.name).all()

    list=[]
    for station in stations:
        dict = {"Station ID:":stations[0], "Station Name": stations[1]}
        list.append(dict)

    return jsonify(list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Last year's most active station date and temperature query
    range = date_calc()
    end_date = range[1]
    start_date = range[0]

    tobs = session.query(Measurement.date, Measurement.tobs).\
                            filter(Measurement.date <= end_date).\
                            filter(Measurement.date >= start_date).all()
    list = []
    for temp in tobs:
        dict = {"date": temp[0], "tobs": temp[1]}
        list.append(dict)
    
    #JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(list)

# JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range

@app.route("/api/v1.0/<start>")
def tempstart(start):
    ##### When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).order_by(Measurement.date.desc()).all()

    print(f"MIN, MAX, AVG Temperatures")
    for temps in results:
        dict = {"Min Temp": results[0][0], "Avg Temp": results[0][1], "Max Temp": results[0][2]}
    return jsonify(dict)


@app.route("/api/v1.0/<start>/<end>")
def tempstartend(start,end):
    # Given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start, Measurement.date <= end).order_by(Measurement.date.desc()).all()
    for temps in results:
        dict = {"Mini Temp": results[0][0], "Avg Temp": results[0][1], "Max Temp": results[0][2]}
    return jsonify(dict)

if __name__ == '__main__':
    app.run(debug=True)
    

