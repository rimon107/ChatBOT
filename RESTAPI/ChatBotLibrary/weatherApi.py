import datetime
import json
import urllib.request


def time_converter(time):
    converted_time = datetime.datetime.fromtimestamp(
        int(time)
    ).strftime('%I:%M %p')
    return converted_time


def url_builder(city_id):
    user_api = 'e39c73df27a3aa745412ba969c843083'  # Obtain yours form: http://openweathermap.org/
    unit = 'metric'  # For Fahrenheit use imperial, for Celsius use metric, and the default is Kelvin.
    api = 'http://api.openweathermap.org/data/2.5/weather?q='     # Search for your city ID here: http://bulk.openweathermap.org/sample/city.list.json.gz

    full_api_url = api + city_id + '&mode=json&units=' + unit + '&APPID=' + user_api
    return full_api_url


def data_fetch(full_api_url):
    try:
        url = urllib.request.urlopen(full_api_url)
        output = url.read().decode('utf-8')
        raw_api_dict = json.loads(output)
        url.close()
        
        return raw_api_dict
    except:
        pass

def data_organizer(raw_api_dict):
    try:
        data = dict(
            city=raw_api_dict.get('name'),
            country=raw_api_dict.get('sys').get('country'),
            temp=raw_api_dict.get('main').get('temp'),
            temp_max=raw_api_dict.get('main').get('temp_max'),
            temp_min=raw_api_dict.get('main').get('temp_min'),
            humidity=raw_api_dict.get('main').get('humidity'),
            pressure=raw_api_dict.get('main').get('pressure'),
            sky=raw_api_dict['weather'][0]['main'],
            sunrise=time_converter(raw_api_dict.get('sys').get('sunrise')),
            sunset=time_converter(raw_api_dict.get('sys').get('sunset')),
            wind=raw_api_dict.get('wind').get('speed'),
            wind_deg=raw_api_dict.get('deg'),
            dt=time_converter(raw_api_dict.get('dt')),
            cloudiness=raw_api_dict.get('clouds').get('all')
        )
        return data
    except:
        data={}
        return data

#
# def data_output(data):
#     m_symbol = '\xb0' + 'C'
#     print('---------------------------------------')
#     print('Current weather in: {}, {}:'.format(data['city'], data['country']))
#     print(data['temp'], m_symbol, data['sky'])
#     print('Max: {}, Min: {}'.format(data['temp_max'], data['temp_min']))
#     print('')
#     print('Wind Speed: {}, Degree: {}'.format(data['wind'], data['wind_deg']))
#     print('Humidity: {}'.format(data['humidity']))
#     print('Cloud: {}'.format(data['cloudiness']))
#     print('Pressure: {}'.format(data['pressure']))
#     print('Sunrise at: {}'.format(data['sunrise']))
#     print('Sunset at: {}'.format(data['sunset']))
#     print('')
#     print('Last update from the server: {}'.format(data['dt']))
#     print('---------------------------------------')

#data_output(data_organizer(data_fetch(url_builder('London'))))


def data_output(data):
    print("in data_output")
    m_symbol = ' Degree ' + 'Celsius '

    print(m_symbol)

    res = ''
    print(res)
    res += '\n'
    print(res)
    res += 'Current weather in: {}, {}:'.format(data['city'], data['country'])
    print(res)
    res += '\n'
    res += 'Temperature: {} {}, Sky: {}:'.format(data['temp'], m_symbol, data['sky'])
    print(res)
    res += '\n'
    res += 'Max: {}, Min: {}'.format(data['temp_max'], data['temp_min'])
    res += '\n'
    res += ''
    res += '\n'
    res += 'Wind Speed: {}, Degree: {}'.format(data['wind'], data['wind_deg'])
    res += '\n'
    res += 'Humidity: {}'.format(data['humidity'])
    res += '\n'
    res += 'Cloud: {}'.format(data['cloudiness'])
    res += '\n'
    res += 'Pressure: {}'.format(data['pressure'])
    res += '\n'
    res += 'Sunrise at: {}'.format(data['sunrise'])
    res += '\n'
    res += 'Sunset at: {}'.format(data['sunset'])
    res += '\n'
    res += ''
    res += '\n'
    res += 'Last update from the server: {}'.format(data['dt'])
    res += '\n'
    res += ''
    res += '\n'
    print("res")
    print(res)
    return  res

