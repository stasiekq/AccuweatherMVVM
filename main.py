import PySimpleGUI as sg
import requests


class WeatherModel:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_city(self, endpoint, queried_name):
        url = endpoint.format(queried_name, self.api_key)
        response = requests.get(url)
        data = response.json()
        print(data)
        return data

    def fetch_data(self, endpoint, location_key):
        url = endpoint.format(location_key, self.api_key)
        response = requests.get(url)
        data = response.json()
        print (data)
        return data

    def fetch_neighbours(self, location_key):
        print(location_key)
        print(self.api_key)
        query_params = {
            "apikey": self.api_key,
            "language": "pl-pl",
        }
        response_neigh = requests.get("http://dataservice.accuweather.com/locations/v1/cities/neighbors/" + location_key, params=query_params)
        data_neigh = response_neigh.json()
        print(data_neigh)
        return data_neigh


class WeatherView:
    def __init__(self, window, model):
        self.window = window
        self.model = model

    def bind(self, key, value):
        self.window[key].update(value)


class WeatherViewModel:
    def __init__(self, model):
        self.model = model
        self.queried_name = ""
        self.location_key = ""
        self.place = ""
        self.weather = ""
        self.forecast = ""
        self.neighbours = ""

    def search_location(self, queried_name):

        print("kaka" + queried_name)
        data = self.model.fetch_city("http://dataservice.accuweather.com/locations/v1/cities/search", queried_name)
        print(data)
        if data:
            location_key = data[0]["Key"]
            place = data[0]["LocalizedName"]
            vm.update_location(location_key, place)


    def update_location(self, location_key, place):
        self.location_key = location_key
        self.place = place


    def update_current_weather(self):
        if not self.location_key:
            return

        weather_data = self.model.fetch_data('http://dataservice.accuweather.com/currentconditions/v1/{0}?apikey={1}', self.location_key)
        if weather_data:
            self.weather = f"Weather: {weather_data[0]['WeatherText']}\nTemperature: {weather_data[0]['Temperature']['Metric']['Value']}°C"
        else:
            self.weather = "Weather data not found"

    def update_tomorrow_weather(self):
        if not self.location_key:
            return

        forecast_data = self.model.fetch_data(self.location_key)
        if forecast_data:
            self.forecast = f"Day: {forecast_data['DailyForecasts'][0]['Day']['IconPhrase']}\nNight: {forecast_data['DailyForecasts'][0]['Night']['IconPhrase']}"
        else:
            self.forecast = "Forecast data not found"


    def update_neighbours(self, num_neighbours):
        if not self.location_key:
            return

        data = self.model.fetch_neighbours( self.location_key)
        print(data)

        neighbour_list  = []
        for i in range(len(data)):
            if i == num_neighbours:
                break
            neighbour_list.append(data[i]['LocalizedName'])
            print(data[i]['LocalizedName'])

        if data:
            neighbour_text = "Neighbouring places:\n"
            for name in neighbour_list:
                neighbour_text += name + "\n"
            self.neighbours = neighbour_text
        else:
            self.neighbours = "Neighbouring places not found"

# Dependency Injection
api_key = "DnR9ZZrPguPY9udOQpnrq64uUk7bJiff"
model = WeatherModel(api_key)
vm = WeatherViewModel(model)

# UI
sg.theme("LightGreen")
layout = [
    [sg.Text('Search by Name or Postal Code:'), sg.InputText(key='-SEARCH-')],
    [sg.Button('Search by Name'), sg.Button('Search by Postal Code')],
    [sg.Text('', key='-LOCATION-')],
    [sg.Button('Current Weather'), sg.Button('Tomorrow Weather')],
    [sg.Text('Number of Neighbouring Places:'),
     sg.Combo(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], key='-COMBO-', default_value='1'),
     sg.Button('Show Neighbouring Places')],
    [sg.Text('', size=(50, 2), key='-WEATHER-')],
    [sg.Text('', size=(50, 6), key='-FORECAST-')],
    [sg.Text('', size=(50, 6), key='-NEIGHBOURS-')],
]

window = sg.Window('Weather App', layout)

# Data Binding
data_binding = {
    '-LOCATION-': lambda: vm.place,
    '-WEATHER-': lambda: vm.weather,
    '-FORECAST-': lambda: vm.forecast,
    '-NEIGHBOURS-': lambda: vm.neighbours,
}

# Event Loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Search by Name':
        # vm.search_location(values['-SEARCH-'])
        name = values['-SEARCH-']
        response = requests.get(f"http://dataservice.accuweather.com/locations/v1/cities/search?q={name}&apikey={api_key}&language=pl-pl")
        data = response.json()
        if data:
            location_key = data[0]["Key"]
            place = data[0]["LocalizedName"]
            vm.update_location(location_key, place)

    if event == 'Search by Postal Code':
        postal = values['-SEARCH-']
        response = requests.get(f"http://dataservice.accuweather.com/locations/v1/postalcodes/search?q={postal}&apikey={api_key}&language=pl-pl")
        data = response.json()
        if data:
            location_key = data[0]["Key"]
            place = data[0]["LocalizedName"]
            vm.update_location(location_key, place)

    if event == 'Current Weather':
        vm.update_current_weather()

    if event == 'Tomorrow Weather':
        vm.update_tomorrow_weather()

    if event == 'Show Neighbouring Places':
        num_neighbours = values['-COMBO-']
        vm.update_neighbours(int(num_neighbours))

    for key, func in data_binding.items():
        window[key].update(func())

window.close()
