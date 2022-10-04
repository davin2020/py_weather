import requests
import json
import urllib.parse

from api_key import API_KEY
from operator import itemgetter

""" REQS
Our goal for this part is to make it so that your console application:

- Reads the locations from the site list and prints a list of locations for the user to choose from.
- Asks the user to input the location name they're interested in.
- Prints out the next weather forecast information for that location.
"""

KEY_NOT_FOUND = 0
SITELIST_URL = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/sitelist?key="

dict_locations = {} #dictionary of locations and ids

# should I try to catch any API errors due to no internet?
def main():
    parsedJson = get_url_data(SITELIST_URL)
    all_locations = parsedJson["Locations"]["Location"]

    # create new dict of locations and ids, then sort it by name so it can be printed in alphabetical order for user
    for locn in all_locations:
        location_name = locn["name"]
        location_id = locn["id"]
        dict_locations[location_name] = location_id

    sorted_list = sort_location_dict_by_name()
    print_sorted_locations(sorted_list)

    while True:
        user_location = read_input_location()
        location_id = get_id_from_name(user_location)
        if location_id != KEY_NOT_FOUND:
            print(f"\nWeather forecast for next 5 days for location {user_location.upper()} in 3 hour increments:")
            result = get_location_weather(location_id)
            print(result)
            break #exit the loop

# todo cater for lowercase words
def print_sorted_locations(newList):
    for item in newList:
        print(f" {item} ")

def read_input_location():
    option = input("Choose from one of the above locations and type your choice: ")
    return option

def sort_location_dict_by_name():
    newlist = sorted(dict_locations, key=itemgetter(0))
    return newlist

# will throw KeyError error if key doesnt exist in dict - id doesnt need to be int can be str
def get_id_from_name(name)->str:
    id = KEY_NOT_FOUND
    try:
        id = dict_locations[name]
    except KeyError:
        print("That location key can't be found, please try again")
    return id

# todo - add return types and type hinting
def get_location_weather(id):
    # makes url safer, makes special chars percentage encoded treatesd as single value, tho doesnt stop bad data - but would prevent user from putting in own ? symbol themselves
    # encode the url as its best practise not to trust user input - https://www.urlencoder.io/python/
    quoted_id = urllib.parse.quote(id)
    CITY_URL = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/" + quoted_id + "?res=3hourly&key="
    res = get_url_data(CITY_URL)
    periods = res["SiteRep"]["DV"]["Location"]["Period"]
    pretty_print_weather_date(periods)

def pretty_print_weather_date(time_period):
    for p in time_period:
        date = p["value"]
        print(f"\nDate: {date}")

        from_hour = 0000
        print(f"  Time        Weather Type:  Wind Gust:  Wind Speed:  Wind Dir:  Temp:  Feels Like:  Rel Humidity:  Vis:  Max UV:  Rain: ")
        # loop over the available time periods under 'Rep' - may be less than 8 for todays date
        for i in range(len(p["Rep"])):
            wind_direction = p["Rep"][i]["D"]
            feels_like = p["Rep"][i]["F"]
            wind_gust = p["Rep"][i]["G"]
            relative_humidity = p["Rep"][i]["H"]
            temperature = p["Rep"][i]["T"]
            visibility = p["Rep"][i]["V"]
            wind_speed = p["Rep"][i]["S"]
            max_uv = p["Rep"][i]["U"]
            # todo substitute in words instead of ids, using separate dict for weather_types
            weather_type = p["Rep"][i]["W"]
            rain_probability = p["Rep"][i]["Pp"]

            # todo - DATES add something about which part of day this is
            # temp dates for now - this works ok for full days, but if weather data starts partway thru the day, would be better to use $ value from json and turn into DateTime obj
            to_hour = from_hour + 180
            from_hour = from_hour + 180
            # take $ value and div by 60 eg 360 becomes 6am, last entry become 2100 etc
            from_hour_hr = int(from_hour/60)
            to_hour_hr = int(to_hour / 60)

            # better formatting/pretty print in cols (hours on left and values on right) with number indicating how wide in chars each col should be
            print(f"{from_hour_hr}00 - {to_hour_hr}00 :  {weather_type:->11}  {wind_gust:->10}  {wind_speed:.>11}  {wind_direction:.>10}  {temperature:->5}  {feels_like:->11}  {relative_humidity:.>13} {visibility:.>6}  {max_uv:->6}  {rain_probability:->4}")

def get_url_data(url):
    content = requests.get(url + API_KEY)
    parsedJson = json.loads(content.text)
    return parsedJson

if __name__ == '__main__':
    main()