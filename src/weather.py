import requests
from xml.etree import ElementTree as ET

WEATHER_DOT_GOV_URL = "https://forecast.weather.gov/MapClick.php?lat=41.5053&lon=-73.9654&unit=0&lg=english&FcstType=dwml"

def loadWeather():
    # Placeholder for weather loading function
    weather_request = requests.get(WEATHER_DOT_GOV_URL)
    weather_request.raise_for_status()  # Raise an error for bad responses
    weather_xml = ET.fromstring(weather_request.content)
    # Parse the XML data

    todays_high_temp = None
    todays_low_temp = None
    todays_weather = None
    # Find the first 'temperature' element with type="maximum"
    for temperature in weather_xml.findall(".//temperature"):
        if temperature.get("type") == "maximum":
            todays_high_temp = temperature.find("value").text
            print(f"First maximum temperature value: {todays_high_temp}")
        if temperature.get("type") == "minimum":
            todays_low_temp = temperature.find("value").text
            print(f"First minimum temperature value: {todays_low_temp}")
    for weather in weather_xml.findall(".//weather"):
        todays_weather = weather.find("weather-conditions").get("weather-summary")
        print(f"First weather summary: {todays_weather}")
        break


if __name__ == "__main__":
    loadWeather()