import pandas as pd
import os
from tools.get_data_from_api import get_zones_data
from tools.get_weather_from_api import get_weather_data

PATH = os.path.dirname(os.path.abspath(__file__))


def extract_hourly_data():
    """
    Funcion para extraer todos los datos de los nodos, 
    unirlos con los datos climaticos y con los datos de 
    posicionamiento.
    """

    # ruta a los archivos csv de los datos de los nodos

    hourly_csv_path = PATH + '/../data/nodos/raw_nodos_hh.csv'

    get_zones_data(type='hh', save_path=hourly_csv_path)   # datos por horas

    data = pd.read_csv(hourly_csv_path)

    # datos geo
    geo_path = PATH + '/../data/geo/coordenadas_zonas.xlsx'

    data_geo = pd.read_excel(geo_path)

    data_geo['Sub - Zonas '] = data_geo['Sub - Zonas '].ffill()

    data_geo.columns = ['id', 'address', 'coordinates', 'zone']

    data_geo.zone = data_geo.zone.apply(lambda x: x.split(' - ')[0].strip().lower().replace(' ', '_')
                                        if len(x.split(' - ')) == 1
                                        else x.split(' - ')[1].strip().lower().replace(' ', '_'))

    data_geo.zone = data_geo.zone.str.replace('plz', 'plaza')

    data_geo.zone = data_geo.zone.str.replace(
        'jardin_vertical', 'plaza_jardin')

    data_geo.loc[0, 'coordinates'] = '41.65285, -0.90566'   # zaragoza centro

    data_geo['latitude'] = data_geo.coordinates.apply(
        lambda x: x.split(',')[0])

    data_geo['longitude'] = data_geo.coordinates.apply(
        lambda x: x.split(',')[1])

    data_geo.drop(columns=['coordinates'], inplace=True)

    data = data.merge(data_geo, left_on='zone', right_on='zone')

    
    # núnero de semana y fin de semana

    time_data = pd.to_datetime(data.timestamp)

    data['year'] = time_data.apply(lambda x: x.year)

    data['month'] = time_data.apply(lambda x: x.month)

    data['day'] = time_data.apply(lambda x: x.day)

    data['date'] = time_data.apply(lambda x: x.date())

    data['hour'] = time_data.apply(lambda x: x.hour)

    data.to_csv(PATH + '/../data/raw/raw_data_hourly.csv', index=False)


def extract_daily_data():
    """
    Funcion para extraer todos los datos de los nodos, 
    unirlos con los datos climaticos y con los datos de 
    posicionamiento.
    """

    # ruta a los archivos csv de los datos de los nodos

    daily_csv_path = PATH + '/../data/nodos/raw_nodos_dd.csv'

    get_zones_data(type='dd', save_path=daily_csv_path)   # datos por dias

    data_nodos = pd.read_csv(daily_csv_path)

    data_nodos.timestamp = data_nodos.timestamp.apply(lambda x: x.split('T')[0])



    # datos climaticos de zaragoza

    get_weather_data()

    data_clima = pd.read_csv(PATH + '/../data/clima/weather_daily.csv')

    data_clima['year'] = pd.to_datetime(
        data_clima.datetime).apply(lambda x: str(x.year))

    data_clima['month'] = pd.to_datetime(data_clima.datetime).apply(
        lambda x: str(x.month) if len(str(x.month)) == 2 else '0'+str(x.month))

    data_clima['day'] = pd.to_datetime(data_clima.datetime).apply(
        lambda x: str(x.day) if len(str(x.day)) == 2 else '0'+str(x.day))
    

    cambio_idioma = {'cloudy': 'nublado', 
                     'partly-cloudy-night': 'nublado', 
                     'partly-cloudy-day': 'nublado',
                     'clear-night': 'despejado', 
                     'clear-day': 'despejado', 
                     'fog': 'niebla', 
                     'rain': 'lluvia', 
                     'wind': 'viento',
                     'snow': 'nieve'}

    
    data_clima.icon = data_clima.icon.apply(lambda x: cambio_idioma[x])

    data_clima['datetime'] = data_clima.year + \
        '-'+data_clima.month+'-'+data_clima.day


    # mergeo dataframes
    data = data_clima.merge(
        data_nodos, left_on='datetime', right_on='timestamp')
    

    # datos geo
    geo_path = PATH + '/../data/geo/coordenadas_zonas.xlsx'

    data_geo = pd.read_excel(geo_path, engine='openpyxl')

    data_geo['Sub - Zonas '] = data_geo['Sub - Zonas '].ffill()

    data_geo.columns = ['id', 'address', 'coordinates', 'zone']

    data_geo.zone = data_geo.zone.apply(lambda x: x.split(' - ')[0].strip().lower().replace(' ', '_')
                                        if len(x.split(' - ')) == 1
                                        else x.split(' - ')[1].strip().lower().replace(' ', '_'))

    data_geo.zone = data_geo.zone.str.replace('plz', 'plaza')

    data_geo.zone = data_geo.zone.str.replace(
        'jardin_vertical', 'plaza_jardin')

    data_geo.loc[0, 'coordinates'] = '41.65285, -0.90566'   # zaragoza centro

    data_geo['latitude'] = data_geo.coordinates.apply(
        lambda x: x.split(',')[0])

    data_geo['longitude'] = data_geo.coordinates.apply(
        lambda x: x.split(',')[1])

    data_geo.drop(columns=['coordinates'], inplace=True)

    data = data.merge(data_geo, left_on='zone', right_on='zone')

    # festivos
    festivos_zaragoza = {'2022-12-06T00:00:00': 1,
                         '2022-12-08T00:00:00': 1,
                         '2022-12-26T00:00:00': 1,

                         '2023-01-02T00:00:00': 1,
                         '2023-01-06T00:00:00': 1,
                         '2023-01-30T00:00:00': 1,

                         '2023-03-03T00:00:00': 1,

                         '2023-04-06T00:00:00': 1,
                         '2023-04-07T00:00:00': 1,
                         '2023-04-24T00:00:00': 1,

                         '2023-05-01T00:00:00': 1,

                         '2023-08-15T00:00:00': 1,

                         '2023-10-12T00:00:00': 1,

                         '2023-11-01T00:00:00': 1,

                         '2023-12-06T00:00:00': 1,
                         '2023-12-08T00:00:00': 1,
                         '2023-12-26T00:00:00': 1,
                         }

    data['holidays'] = data.timestamp.apply(
        lambda x: festivos_zaragoza.get(x, 0))

    # núnero de semana y fin de semana

    time_data = pd.to_datetime(data.timestamp)

    data['year'] = time_data.apply(lambda x: x.year)

    data['month'] = time_data.apply(lambda x: x.month)

    data['day'] = time_data.apply(lambda x: x.day)

    data['date'] = time_data.apply(lambda x: x.date())

    data['week'] = time_data.apply(lambda x: x.week)

    data['weekday'] = time_data.apply(lambda x: x.weekday())

    data['weekend'] = time_data.apply(lambda x: 1 if x.weekday() > 4 else 0)

    data.to_csv(PATH + '/../data/raw/raw_data_daily.csv', index=False)


def extract_monthly_data():
    """
    Funcion para extraer todos los datos de los nodos, 
    unirlos con los datos climaticos y con los datos de 
    posicionamiento.
    """

    # ruta a los archivos csv de los datos de los nodos

    monthly_csv_path = PATH + '/../data/nodos/raw_nodos_mm.csv'

    get_zones_data(type='mm', save_path=monthly_csv_path)   # datos por mes

    data = pd.read_csv(monthly_csv_path)

    data.timestamp = data.timestamp.apply(lambda x: x.split('T')[0])

    # núnero de semana y fin de semana

    time_data = pd.to_datetime(data.timestamp)

    data['year'] = time_data.apply(lambda x: x.year)

    data['month'] = time_data.apply(lambda x: x.month)

    data['date'] = time_data.apply(lambda x: x.date())

    data.to_csv(PATH + '/../data/raw/raw_data_monthly.csv', index=False)



def extract_data():
    extract_hourly_data()
    extract_daily_data()
    extract_monthly_data()
