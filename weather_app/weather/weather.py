from re import template
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session
from flask_sqlalchemy import SQLAlchemy

weather = Blueprint("weather", __name__, template_folder="templates")

db = SQLAlchemy()

class users(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String(100))
     cities = db.relationship("City", backref="owner")

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=017bb8adbbf4121ebb7fc38a24d4855b"
    r = requests.get(url).json()
    return r

@weather.route('/', methods=['POST'])
def index_post():

    new_city = request.form.get('city').title()
    err_msg = ""

    if new_city:
        existing_city = City.query.filter_by(name=new_city, user_id=session["usr_id"]).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod']==200:
                new_city_obj =  City(name=new_city, user_id=session["usr_id"])
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = "City does not exists in the world!"
        else:
            err_msg = 'City Already Exists!'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added succesfully')

    return redirect(url_for('weather.index_get'))

@weather.route('/')
def index_get():
    db.create_all()
    cities = City.query.filter_by(user_id=session["usr_id"]).all()

    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)

        try:
            weather = {
                'city': city.name,
                'temperature': float("{:.2f}".format(r['main']['temp'] - 273)),
                'description': r['weather'][0]['description'],
                'icon': r['weather'][0]['icon']
            }
            weather_data.append(weather)
        except:
            pass

    return render_template('weather.html', weather_data=weather_data)

@weather.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name, user_id=session['usr_id']).first()
    db.session.delete(city)
    db.session.commit()

    flash('Successfuly deleted {}'.format(city.name), 'success')
    return redirect(url_for('weather.index_get'))


