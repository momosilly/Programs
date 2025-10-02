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
    temp_c = int(round(data['current']['temp_c']))
    condition_text = data['current']['condition']['text']
    icon_url = "https:" + data['current']['condition']['icon']
    code = data['current']['condition']['code']
    is_day = data['current']['is_day']
    return {"temp": temp_c, "condition": condition_text, "icon_url": icon_url, "code": code, "isday": is_day}

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
    maybe_umbrella = [1150, 1153, 1180, 1183, 1240, 1273, 1063]

    if data['current']['condition']['code'] in def_umbrella:
        return "You NEED an umbrella and rain jacket"
    elif data['current']['condition']['code'] in maybe_umbrella:
        return "Consider getting an umbrella"
    else:
        return "No umbrella needed"

def feelslike(city):
    params = {"key": API_KEY, "q": city}
    url = "http://api.weatherapi.com/v1/current.json"
    response = requests.get(url, params=params)
    data = response.json()
    feels_like = data['current']['feelslike_c']

    if feels_like <= -10:
        advice = "Heavy winter coat, thermal layers, gloves, hat, scarf"
    elif feels_like <= 0:
        advice = "Winter coat, sweater, gloves, hat"
    elif feels_like <= 10:
        advice = "Jacket or coat, long sleeves, optional scarf"
    elif feels_like <= 15:
        advice = "Light jacket or hoodie, jeans or trousers"
    elif feels_like <= 20:
        advice = "Long sleeves or light sweater, optional jacket"
    elif feels_like <= 25:
        advice = "T-shirt or polo, light pants or shorts"
    elif feels_like <= 30:
        advice = "Short sleeves, shorts, breathable fabrics"
    else:
        advice = "Shorts, sun protection (hat, sunglasses)"
    return {"feelslike": feels_like, "advice": advice}
    

#print(feelslike())

def cycling_difficulty(city):
    params = {"key": API_KEY, "q": city}
    url = "http://api.weatherapi.com/v1/current.json"
    response = requests.get(url, params=params)
    data = response.json()
    wind_kph = data['current']['wind_kph']

    if wind_kph <= 10:
        cycle =  "Easy ride — minimal wind resistance"
    elif wind_kph <= 20:
        cycle = "Moderate — some resistance, manageable for most riders"
    elif wind_kph <= 30:
        cycle = "Challenging — strong headwinds, tiring over long distances"
    elif wind_kph <= 40:
        cycle = "Hard — expect significant effort, may need to slow down"
    elif wind_kph <= 50:
        cycle = "Very hard — only for experienced cyclists, risk of instability"
    else:
        cycle = "Extreme — unsafe for cycling, consider postponing"
    return {"cycle": cycle, "wind": wind_kph}

def alerts(city):
    params = {"key": API_KEY, "q": city}
    url = "http://api.weatherapi.com/v1//alerts.json"
    response = requests.get(url, params=params)
    alerts = response.json()

    alerts_list = alerts.get('alerts', {}).get('alert', [])

    result = []
    if alerts_list:
        for alert in alerts_list:
            result.append({
                "event": alert.get('event', 'N/A'),
                "severity": alert.get('severity', 'N/A'),
                "certainty": alert.get('certainty', 'N/A'),
                "areas": alert.get('areas', 'N/A'),
                "effective": alert.get('effective', 'N/A'),
                "expires": alert.get('expires', 'N/A')
            })
    else:
        pass
    return result

#alerts()

@app.route("/", methods=["GET", "POST"])
def index():
    # defaults
    tempdef = None 
    locationdef = None 
    raindef = None 
    feelslikedef = None 
    cycling_difficultydef = None
    alertsdef = None
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