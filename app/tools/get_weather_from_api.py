import pandas as pd
from datetime import datetime
import requests as req
import os
from tools.tools import Logger


logger = Logger('SpaceRetail Log').logger

PATH = os.path.dirname(os.path.abspath(__file__)) + '/../data/clima/weather_daily.csv'


def get_weather_data():

    global PATH

    logger.info('Getting Weather Data...')
    
    
    # carga datos existentes
    data_clima = pd.read_csv(PATH)
    
    
    # datos nuevos
    API_WEATHER_KEY = 'P9HJWPN5KJNUHN3D59EEQD93E'

    start_date = data_clima.datetime.max().split('T')[0]
    end_date = datetime.today().strftime('%Y-%m-%d')   # hoy
    
    URL = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/zaragoza/{start_date}/{end_date}?unitGroup=us&include=hours&key={API_WEATHER_KEY}&contentType=json'

    res = req.get(URL)
    
    if res.status_code==200:
        data = res.json()['days']
        data = [{k:str(v) for k,v in e.items()} for e in data]
        df = pd.DataFrame(data)
        data_clima = pd.concat([data_clima, df]).drop_duplicates()
    else:
        pass

    data_clima.to_csv(PATH, index=False)

    logger.info('Done')