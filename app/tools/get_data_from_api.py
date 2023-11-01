# librerias

import requests as req
import json
import hashlib
import time
from Crypto.Cipher import AES
import binascii
import base64
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm
from tools.tools import Logger
import os


# variables globales

# create logger
logger = Logger('SpaceRetail Log').logger

PATH = os.path.dirname(os.path.abspath(__file__))


URL = 'https://analytics.spaceretail.es/observer/rest/'   # URL BASE


APP_ID = 20202020021  # Zaragoza


ZONES_CODES = {'zaragoza': 25501,
               'zona_delicias': 25502,
               'zona_casco': 25503,
               
               'mercado_delicias': 25895,
               'plaza_justicia': 25460,
               'plaza_san_felipe': 25453,
               'plaza_san_pedro_nolasco': 25456,
               'plaza_jardin': 25446,
               
               'zona_a': 25511,
               'zona_b': 25512,
               'zona_c': 25452,
               'zona_d': 25513,
               'zona_e': 25458,
               'zona_f': 25459,
               'zona_g': 25462,
               'zona_h': 25463,
               }


MONTHS = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
          5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
          9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

START_DATE = (datetime.today() - timedelta(days=100)
              ).strftime('%Y-%m-%d')  # 100 dias atras

END_DATE = datetime.today().strftime('%Y-%m-%d')   # hoy



def encode(text):
    """
    encode para creacion del hash de login
    """

    def pad(s): return s + chr(16 - len(s) % 16) * (16 - len(s) % 16)

    iv = hashlib.sha256(
        "54WMd+S:J\D_\Bf&z,pZ!Ga8c".encode('utf-8')).hexdigest()[0:16].encode()

    encrypted = AES.new(binascii.unhexlify("175f04c0fac277a9941220c4d115c1888326848930dbb6d39ef89130b1211167"),
                        AES.MODE_CBC, iv).encrypt(pad(text))

    return base64.b64encode(iv + encrypted)


def get_key():
    """
    creacion del hash de login

    param:
    now : datetime, e.g.'1693579358'

    return:
    KEY: key hash para login
    """

    global URL

    logger.info('Getting Hash Key...')

    USER = 'SRTech'
    PASSWORD = 'SRTech!1658'

    now = str(int(time.time()))

    HASH = encode((hashlib.sha1(PASSWORD.encode('utf-8')
                                ).hexdigest() + USER + now)).decode()

    PARAMS = {'params': json.dumps({'login': USER,
                                    'timestamp': now,
                                    'hash': HASH}),
              'method': 'authRest'}

    res = req.post(url=URL, data=PARAMS).json()

    logger.info('Done')

    if res['isError'] == False:
        return res['response']['data']['key']

    else:
        return 'Error generating hash key: ' + res['errorDesc']


def is_consolidated(date):
    
    """
    ¿El dato está consolidado?

    date = 'YYYY-MM-DD'
    """
    
    global URL, APP_ID

    KEY = get_key()
    
    PARAMS = {'params': json.dumps({'app_id': APP_ID, 
                                    'key': KEY,
                                    'date': date, 
                                   }), 
          
          'method': 'getDataState'}


    res = req.post(url=URL, data=PARAMS)

    return res.json()['response']['data'][0]['status']


def get_zones_data(type='hh', start_date=START_DATE, end_date=END_DATE, save_path=PATH + '/../data/nodos/raw_nodos.csv'):
    
    """
    Obtener datos por hora de las zonas
    """
    
    global URL, APP_ID, ZONES_CODES

    KEY = get_key()
    
    df_lst = []

    logger.info('Getting Data from API...')
    
    for k,v in tqdm(ZONES_CODES.items()):
    
        PARAMS = {'params': json.dumps({'app_id': APP_ID, 
                                        'key': KEY,
                                        'zone_id': v,
                                        'last': time.mktime(datetime.strptime(start_date, '%Y-%m-%d').timetuple()),
                                        'end': time.mktime(datetime.strptime(end_date, '%Y-%m-%d').timetuple()),
                                        'type': type,
                                        'profile': 0
                                    }), 

              'method': 'getZoneVisitsH'}


        res = req.post(url=URL, data=PARAMS)

        res_data = res.json()['response']['data']

        df = pd.DataFrame(res_data)

        df['zone'] = k
        
        df_lst.append(df)
        
    data = pd.concat(df_lst)

    data.timestamp = data.timestamp.str.replace(' ', 'T')

    data.recurrents = data.visitors_unique - data.new_visits

    data['ratio'] = data.visits / data.visitors_unique

    time_data = pd.to_datetime(data.timestamp)

    data['year'] = time_data.apply(lambda x: x.year)

    data['month'] = time_data.apply(lambda x: x.month)
    data['month_name'] = data.month.apply(lambda x: MONTHS[x])

    data['day'] = time_data.apply(lambda x: x.day)

    dayofweek_change = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
                        4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    
    data['dayofweek'] = time_data.apply(lambda x: x.dayofweek)
    data['dayofweek'] = data['dayofweek'].map(dayofweek_change)

    data['date'] = time_data.apply(lambda x: x.date())

    data['hour'] = time_data.apply(lambda x: x.hour)

    data.to_csv(save_path, index=False)

    logger.info('Data Saved.')


def get_flow_data_api(start_date, end_date):
    
    global APP_ID

    logger.info(f'Getting Flow Data {start_date} from API...')

    KEY = get_key()
    
    Q = {1: 1,2: 1,3: 1,
         4: 2,5: 2,6: 2,
         7: 3,8: 3,9: 3,
         10:4 ,11: 4,12: 4}
    
    date = start_date.split('-')
    year = int(date[0])
    month = int(date[1])
    
    PARAMS = {'params': json.dumps({'app_id': APP_ID, 
                                    'key': KEY,
                                    'periodicity': 'Month',
                                    'year': year,
                                    'month': month,
                                    'quarter': Q[month],
                                    'starting': start_date,
                                    'ending': end_date,
                                    'profile': 0
                                }), 
          
          'method': 'getSankeyPathData'}


    res = req.post(url=URL, data=PARAMS)


    df = pd.DataFrame(res.json()['response']['data']['raw_data'])[[0, 2, 5]]
    
    df.columns = ['start_zone', 'value', 'end_zone']
    
    
    change_zones = {
                   'Plaza 4 - Justicia': 'plaza_justicia',
                   'Plaza 2-San Felipe': 'plaza_san_felipe',
                   'Pza 3-San Pedro Nola': 'plaza_san_pedro_nolasco',
                   'Plaza 1-Jardin Verti': 'plaza_jardin',
                   'Zona A': 'zona_a',
                   'Zona B': 'zona_b',
                   'Zona C': 'zona_c',
                   'Zona D': 'zona_d',
                   'Zona E': 'zona_e',
                   'Zona F': 'zona_f',
                   'Zona G': 'zona_g',
                   'Zona H': 'zona_h',
                   }
    
    df.start_zone = df.start_zone.apply(lambda x: change_zones[x.strip()])
    df.end_zone = df.end_zone.apply(lambda x: change_zones[x.strip()])
    
    df['year'] = year
    df['month'] = month

    logger.info('Done.')
    
    return df


def get_retention_data(month, year):
    
    """
    Obtener datos de retencion
    """
    
    global URL, APP_ID
    

    MONTH = {'Enero': '01', 'Febrero': '02', 'Marzo': '03', 'Abril': '04',
             'Mayo': '05', 'Junio': '06', 'Julio': '07', 'Agosto': '08',
             'Septiembre': '09', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12'}
    
    
    zones = ['Calle_Delicias', 'Casco_Historico']

    KEY = get_key()
    
    logger.info('Getting Data from API...')
    
    # ahora
    start_date = f'{year}-{MONTH[month]}-01'

    # mes anterior
    last_date = pd.to_datetime(start_date) - pd.DateOffset(months=1)
    last_date = last_date.strftime('%Y-%m-%d')

    # final mes
    end_date = pd.to_datetime(start_date) + pd.DateOffset(months=1) - pd.DateOffset(days=1)  # uso horario servidor, menos 1 dia, para pythonanywhere
    end_date = end_date.strftime('%Y-%m-%d')

    logger.info(f'Getting Retention Data {start_date} from API...')
    
    profiles = {'retention': 98, 'oportunity': 3}
    
    df_lst = []
    
    for k,v in profiles.items():
        
        PARAMS = {'params': json.dumps({'app_id': APP_ID, 
                                        'key': KEY,
                                        'start': time.mktime(datetime.strptime(last_date, '%Y-%m-%d').timetuple()),
                                        'end': time.mktime(datetime.strptime(end_date, '%Y-%m-%d').timetuple()),
                                        'profile_id': v
                                       }), 

                                  'method': 'getProfileResults'}


        res = req.post(url=URL, data=PARAMS)

        res_data = res.json()['response']['data']

        df = pd.DataFrame(res_data)
        
        df['type'] = k
        
        df = df[df.zone_name.isin(zones)]
        
        df_lst.append(df)
        
        
        
    data = pd.concat(df_lst)
    
    data.value = data.value*100
    
    data.timestamp = data.timestamp.apply(lambda x: x.split()[0])
    
    data.to_csv(PATH + f'/../reports/data/retention_data.csv')

    logger.info('Done.')


def get_hour_intervals(start_date, end_date):
    
    """
    Obtener datos de las zonas
    """
    
    global URL, APP_ID, ZONES_CODES
    
    KEY = get_key()
    
    PARAMS = {'params': json.dumps({'app_id': APP_ID, 
                                    'key': KEY,
                                    'last': time.mktime(datetime.strptime(start_date, '%Y-%m-%d').timetuple()),
                                    'end': time.mktime(datetime.strptime(end_date, '%Y-%m-%d').timetuple()),
                                    'type': 'mm',
                                    'c_factor': 1,
                                    'frequency': 'd'
                                   }), 

          'method': 'getVisitsHbyHoursInterval'}


    res = req.post(url=URL, data=PARAMS)

    res_data = res.json()['response']['data']['ranges']

    
    df = pd.DataFrame(res_data)

    df['date'] = df.day

    df['year'] = df.day.apply(lambda x: x.split('-')[0])
    df['month'] = df.day.apply(lambda x: x.split('-')[1])
    df['day'] = df.day.apply(lambda x: x.split('-')[2])

    df.to_csv(PATH + '/../reports/data/hour_range_data.csv', index=False)


def report_data_from_api(month, year):
    
    MONTH = {'Enero': '01', 'Febrero': '02', 'Marzo': '03', 'Abril': '04',
             'Mayo': '05', 'Junio': '06', 'Julio': '07', 'Agosto': '08',
             'Septiembre': '09', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12'}
    
    # ahora
    start_date = f'{year}-{MONTH[month]}-01'
    
    # mes anterior
    last_date = pd.to_datetime(start_date) - pd.DateOffset(months=1)
    last_date = last_date.strftime('%Y-%m-%d')
    
    # final mes
    end_date = pd.to_datetime(start_date) + pd.DateOffset(months=1) - pd.DateOffset(days=2)   # uso horario servidor, menos 2 dia, para pythonanywhere
    end_date = end_date.strftime('%Y-%m-%d')
    
    
    # zones data hourly
    get_zones_data(type='hh', 
                   start_date=last_date, 
                   end_date=end_date, 
                   save_path=PATH + '/../reports/data/raw_nodos_hh.csv')

    
    # zones data daily
    get_zones_data(type='dd', 
                   start_date=last_date, 
                   end_date=end_date, 
                   save_path=PATH + '/../reports/data/raw_nodos_dd.csv')


    # zones data monthly
    get_zones_data(type='mm', 
                   start_date=last_date, 
                   end_date=end_date, 
                   save_path=PATH + '/../reports/data/raw_nodos_mm.csv')


    
    # flow data
    df = get_flow_data_api(last_date, start_date)
    df2 = get_flow_data_api(start_date, end_date)
    flow_data = pd.concat([df, df2])
    flow_data.value = flow_data.value.apply(lambda x: round(x, 2))
    flow_data.to_csv(PATH + '/../reports/data/flow_data.csv', index=False)


    # retention data
    get_retention_data(month, year)


    # hour range data
    get_hour_intervals(last_date, end_date)





    
    
    



