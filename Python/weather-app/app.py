from dotenv import load_dotenv
import os
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

load_dotenv()
API_KEY = os.getenv("WEATHER_API")

def temp(city):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": API_KEY, "q": city}
    response = requests.get(url, params=params)
    data = response.json()
    print(data['current']['temp_c'])
    temp = int(round(data['current']['temp_c']))
    return temp

def location(city):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": API_KEY, "q": city}
    response = requests.get(url, params=params)
    data = response.json()
    city_name = data['location']['name']
    return city_name

def rain(city):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": API_KEY, "q": city}
    response = requests.get(url, params=params)
    data = response.json()

    def_umbrella = [1186, 1189, 1192, 1195, 1243, 1246, 1276]
    maybe_umbrella = [1150, 1153, 1180, 1183, 1240, 1273]
    no_umbrella = [1063]

    if data['current']['condition']['code'] in def_umbrella:
        return "You NEED an umbrella and rain jacket"
    elif data['current']['condition']['code'] in maybe_umbrella:
        return "Consider getting an umbrella"
    elif data['current']['condition']['code'] in no_umbrella:
        return "No need for umbrella"
    else:
        return "No umbrella needed"

def feelslike(city):
    params = {"key": API_KEY, "q": city}
    url = "http://api.weatherapi.com/v1/current.json"
    response = requests.get(url, params=params)
    data = response.json()
    feels_like = data['current']['feelslike_c']

    if feels_like <= -10:
        return "Heavy winter coat, thermal layers, gloves, hat, scarf"
    elif feels_like <= 0:
        return "Winter coat, sweater, gloves, hat"
    elif feels_like <= 10:
        return "Jacket or coat, long sleeves, optional scarf"
    elif feels_like <= 15:
        return "Light jacket or hoodie, jeans or trousers"
    elif feels_like <= 20:
        return "Long sleeves or light sweater, optional jacket"
    elif feels_like <= 25:
        return "T-shirt or polo, light pants or shorts"
    elif feels_like <= 30:
        return "Short sleeves, shorts, breathable fabrics"
    else:
        return "Tank tops, shorts, sun protection (hat, sunglasses)"

#print(feelslike())

def cycling_difficulty(city):
    params = {"key": API_KEY, "q": city}
    url = "http://api.weatherapi.com/v1/current.json"
    response = requests.get(url, params=params)
    data = response.json()
    wind_kph = data['current']['wind_kph']

    if wind_kph <= 10:
        return "Easy ride — minimal wind resistance"
    elif wind_kph <= 20:
        return "Moderate — some resistance, manageable for most riders"
    elif wind_kph <= 30:
        return "Challenging — strong headwinds, tiring over long distances"
    elif wind_kph <= 40:
        return "Hard — expect significant effort, may need to slow down"
    elif wind_kph <= 50:
        return "Very hard — only for experienced cyclists, risk of instability"
    else:
        return "Extreme — unsafe for cycling, consider postponing"
#print(cycling_difficulty())

def alerts(city):
    params = {"key": API_KEY, "q": city}
    url = "http://api.weatherapi.com/v1//alerts.json"
    response = requests.get(url, params=params)
    alerts = response.json()

    alerts_list = alerts.get('alerts', {}).get('alert', [])

    if alerts_list:
        for alert in alerts_list:
            print("Event:", alert.get('event', 'N/A'))
            print("Severity:", alert.get('severity', 'N/A'))
            print("Certainty:", alert.get('certainty', 'N/A'))
            print("Areas affected:", alert.get('areas', 'N/A'))
            print("Starts on:", alert.get('effective', 'N/A'))
            print("Ends on:", alert.get('expires', 'N/A'))
    else:
        pass

#alerts()

@app.route("/", methods=["GET", "POST"])
def index():
    # defaults
    tempdef = locationdef = raindef = feelslikedef = cycling_difficultydef = alertsdef = ""
    city = "Paris"  # default city

    if request.method == "POST":
        city = request.form.get('city', 'Paris')
        tempdef = temp(city)
        locationdef = location(city)
        raindef = rain(city)
        feelslikedef = feelslike(city)
        cycling_difficultydef = cycling_difficulty(city)
        alertsdef = alerts(city)

    return render_template(
        "index.html",
        tempdef=tempdef,
        locationdef = locationdef,
        raindef=raindef, 
        feelslikedef=feelslikedef, 
        cycling_difficultydef=cycling_difficultydef, 
        alertsdef=alertsdef
    )

if __name__ == '__main__':
    app.run(debug=True)