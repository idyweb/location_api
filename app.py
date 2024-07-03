from flask import Flask, request, jsonify
import requests

from dotenv import load_dotenv
import os
import logging

load_dotenv()

app = Flask(__name__)

weather_api_key = os.getenv('WEATHER_API_KEY')

def get_client_ip():
    """Function to get the client's IP address from the request."""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        # In case of a proxy, get the original IP
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]

@app.route('/api/hello', methods=['GET'])
def hello():
    visitor_name = request.args.get('visitor_name')
    client_ip = get_client_ip()
    
    # Get location info from ipinfo.io
    ipinfo_response = requests.get(f'http://ipinfo.io/{client_ip}/json')
    if ipinfo_response.status_code != 200:
        return jsonify({"error": "Unable to get location information"}), 500

    location_data = ipinfo_response.json()
    location = location_data.get('city', 'Unknown')

    # Get weather info from OpenWeatherMap
    weather_response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}&units=metric')
    if weather_response.status_code != 200:
        logging.error(f"Weather API request failed: {weather_response.text}")  # Log the error response from the weather API
        return jsonify({"error": "Unable to get weather information"}), 500

    weather_data = weather_response.json()
    temperature = weather_data['main']['temp']
    
    greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {location}"
    
    response = {
        "client_ip": client_ip,
        "location": location,
        "greeting": greeting
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
