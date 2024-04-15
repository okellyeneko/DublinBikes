from flask import Flask, render_template, jsonify, url_for
from dbManager import engine
from sqlalchemy import text
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# conversion to Dublin time
utc_time = datetime.now(timezone.utc)
local_time = utc_time.astimezone(ZoneInfo("Europe/Dublin"))


app = Flask(__name__)

# Loading the models
model_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Models', 'pickle_files'))
models = {'bikes': {}, 'stands': {}}

for filename in os.listdir(model_dir):
    if filename.endswith('.pkl'):
        parts = filename.split('_')
        if len(parts) == 2 and parts[0] in ['bikes', 'stands']:
            model_type = parts[0]
            station_number = parts[1].split('.')[0] 
            if station_number.isdigit():
                station_number = int(station_number)
                filepath = os.path.join(model_dir, filename)
                with open(filepath, 'rb') as handle:
                    models[model_type][station_number] = pickle.load(handle)




for model_type in models:
    for station in models[model_type]:
        print(f"Loaded model for {model_type} at station {station}")
    if not models[model_type]:
        print(f"No models loaded for {model_type}")

def fetch_weather_data(date):
    city = "Dublin,IE"
    api_key = "dd05f29b3c673dec7f4a9df4f8cce8fd" 
    units = "metric"
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units={units}"
    response = requests.get(forecast_url)
    if response.status_code == 200:
        forecast_data = response.json()
        weather_data = []
        for entry in forecast_data['list']:
            forecast_time = datetime.fromtimestamp(entry['dt'], tz=timezone.utc)
            if forecast_time.date() == datetime.strptime(date, "%Y-%m-%d").date():
                weather_data.append({
                    'hour': forecast_time.hour,
                    'temperature': entry['main']['temp'],
                    'wind_speed': entry['wind']['speed'],
                    'rainfall': entry.get('rain', {}).get('3h', 0) / 3 if 'rain' in entry else 0,
                    'weather_description': entry['weather'][0]['main'].lower()
                })
        return weather_data
    return None

def map_weather_conditions(description):
    description = description.lower()
    return {
        'clear_sky': 1 if 'clear' in description else 0,
        'few_clouds': 1 if 'few clouds' in description else 0,
        'scattered_clouds': 1 if 'scattered clouds' in description else 0,
        'broken_clouds': 1 if 'broken clouds' in description else 0,
        'overcast_clouds': 1 if 'overcast clouds' in description else 0,
        'mist': 1 if 'mist' in description else 0,
        'fog': 1 if 'fog' in description else 0,
        'haze': 1 if 'haze' in description else 0,
        'drizzle': 1 if 'drizzle' in description else 0,
        'light_rain': 1 if 'light rain' in description else 0,
        'moderate_rain': 1 if 'moderate rain' in description else 0,
        'heavy_intensity_rain': 1 if 'heavy intensity rain' in description else 0,
        'shower_rain': 1 if 'shower rain' in description else 0,
        'thunderstorm_with_light_rain': 1 if 'thunderstorm with light rain' in description else 0,
    }


@app.route('/predictive_plot/<int:station_number>', methods=['POST'])
def predictive_plot(station_number):
    date = request.form.get('date')
    if not date:
        return jsonify({'error': 'Date not provided'}), 400

    weather_data = fetch_weather_data(date)
    if not weather_data:
        return jsonify({'error': 'Weather data not available for this date'}), 404

    results = {}
    for model_type in ['bikes', 'stands']:
        model = models[model_type].get(station_number)
        print(models)
        if model is None:
            print(f"No model found for {model_type} at station {station_number}")
            continue  # Skip if no model is found for this type

        day_of_week = datetime.strptime(date, "%Y-%m-%d").weekday()
        predictions = []
        forecast_hours = []  # Initialize an empty list for forecast hours
        for data in weather_data:
            conditions = map_weather_conditions(data['weather_description'])
            features = [
                data['temperature'],
                data['wind_speed'],
                data['rainfall'], 
                day_of_week,
                data['hour'],
                0,
                conditions['clear_sky'],
                conditions['few_clouds'],
                conditions['scattered_clouds'],
                conditions['broken_clouds'],
                conditions['overcast_clouds'],
                conditions['mist'],
                conditions['light_rain'],
                conditions['moderate_rain'],
                conditions['heavy_intensity_rain'],
                conditions['fog'],
                conditions['haze'],
                conditions['thunderstorm_with_light_rain']
            ]

            prediction = model.predict(np.array(features).reshape(1, -1))
            predictions.append(prediction[0])

            current_hour = min(data['hour'] for data in weather_data)  # Get the earliest hour in the weather data
            forecast_hours = [current_hour + i * 3 for i in range(len(predictions))]


        plot_path = generate_plot(predictions, forecast_hours, model_type)
        results[model_type] = plot_path

    return jsonify(results)


def generate_plot(predictions, hours, model_type):
    plt.figure(figsize=(10, 5))
    plt.plot(hours, predictions, marker='o')
    plt.title(f'Predicted Number of {model_type.capitalize()} Available Throughout the Day')
    plt.xlabel('Hour of the Day')
    plt.ylabel(f'{model_type.capitalize()} Available')
    plt.grid(True)
    plt.xticks(hours)
    plot_filename = f'static/images/{model_type}_predictions_plot.png'
    plt.savefig(plot_filename)
    plt.close()
    return url_for('static', filename=os.path.basename(plot_filename))



from datetime import datetime


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/forecast')
def forecast():
    # Foreacst placeholders and urls
    city = "Dublin,IE"
    api_key = "dd05f29b3c673dec7f4a9df4f8cce8fd"
    units = "metric"
    current_weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}"
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units={units}"
    print(local_time)

    # Fetching the current weather info
    current_response = requests.get(current_weather_url)
    if current_response.status_code == 200:
        current_data = current_response.json()
        temp = current_data['main']['temp']
        desc = current_data['weather'][0]['description']
        wind = current_data['wind']['speed']
        rain = current_data.get('rain', {}).get('1h', 0)
        time = local_time.strftime("%Y-%m-%d %H:%M:%S")  # UTC now with timezone support
        icon = current_data['weather'][0]['icon']
    else:
        return render_template('forecast.html', error="Failed to fetch current weather data.")

    # Fetching the forecast
    forecast_response = requests.get(forecast_url)
    if forecast_response.status_code == 200:
        forecast_data = forecast_response.json()
        forecasts = forecast_data['list']

        # Daily forecasts
        daily_forecasts = []
        seen_dates = set()
        for entry in forecasts:
            forecast_date = datetime.fromtimestamp(entry['dt'], tz=timezone.utc).date()
            if forecast_date not in seen_dates:
                seen_dates.add(forecast_date)
                entry['display_date'] = forecast_date.strftime("%A, %B %d")
                daily_forecasts.append(entry)

    else:
        return render_template('forecast.html', error="Failed to fetch forecast data.")

    # template with all data
    return render_template('forecast.html', 
                           temp=temp, 
                           desc=desc, 
                           wind=wind, 
                           rain=rain, 
                           time=time, 
                           icon=icon,
                           hourly_forecasts=forecasts[:8], # Number of rows to show
                           daily_forecasts=daily_forecasts)

@app.route('/map')
def stations():
    try:
        with engine.connect() as connection:
        
            query = text("""SELECT station.number, status, bikes, stands, mechanicalBikes, electricalBikes, electricalInternalBatteryBikes, electricalRemovableBatteryBikes, address, banking, capacity, bonus, name, position_lat, position_lng, lastUpdate
                             FROM
                                availability, station
                             WHERE
                                timestamp = (SELECT MAX(timestamp) FROM dbikes.availability) AND availability.number = station.number
                             ORDER BY number;""")
            
            result = connection.execute(query)
            rows = result.fetchall()
            
            # Convert rows to a list of dictionaries
            stations = [{"number": row.number,
                        "lat": row.position_lat,
                        "lng": row.position_lng,
                        "name": row.name,
                        "address": row.address,
                        "card": row.banking,
                        "status": row.status, 
                        "bikes": row.bikes, 
                        "stands": row.stands, 
                        "mechbikes": row.mechanicalBikes, 
                        "elecbikes": row.electricalBikes, 
                        "elecinternal": row.electricalInternalBatteryBikes, 
                        "elecremoveable": row.electricalRemovableBatteryBikes, 
                        "lastupdate": row.lastUpdate} 
                        for row in rows]

            # Pass the stations data to the template
            return render_template('map.html', data=stations)
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    app.run(debug=True)


