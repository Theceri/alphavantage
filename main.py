from enum import unique
from flask import Flask, request, render_template, redirect, url_for, session
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests, json
from datetime import datetime, timezone
from sqlalchemy.orm import backref
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy

# We are creating an instance of the flask application
app = Flask(__name__)

api_key = "EZKBB11OQDGS3BGK"

scheduler = BackgroundScheduler(daemon=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alphavantage.db'

db = SQLAlchemy(app)

# This is a model
class Data(db.Model):
    __tablename__ = 'data'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    data = db.Column(db.String(80))
    symbol = db.Column(db.String(80), unique=True, nullable=True)//
    data = db.Column(db.JSON(), unique=True)
    # open = db.Column(db.Numeric(20, 4))
    # high = db.Column(db.Numeric(20, 4))
    # low = db.Column(db.Numeric(20, 4))
    # close = db.Column(db.Numeric(20, 4))
    # volume = db.Column(db.Integer)
    created = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()
    print('The tables have been created')

@app.route('/')
def home():
    # get data from database
    data_json = Data.query.all()

    print('this is from the db', data_json)
    print('The program seems to be running')

    return render_template('index.html', stock_data = data_json['Weekly Time Series'])

def request_scheduler():
    try:
        # make a GET request to Alpha Vantage API
        r = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol=IBM&apikey=' + api_key)

        # store the data received from the API in a variable
        data = r.text

        # find out the type of data
        print(type(data))
        
        # since the type above is string, convert it to a dictionary - use json.loads when inputting data, use json.dumps when outputting data
        data_json = json.loads(data)

        # find out the type of data again
        print(type(data_json))

        print("from scheduler", data_json)

        # data = Forex(symbol=, open=, high=, low=, close=, volume=)

        # save to DB
        data = Data(symbol='IBM', data=json.dumps(data_json))
        db.session.add(data)
        db.session.commit()
    except Exception as e:
        print("Error in scheduler", e)


# create the scheduler job
scheduler.add_job(request_scheduler, 'interval', minutes=1)

#start the scheduler
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)