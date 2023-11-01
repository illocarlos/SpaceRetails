import pandas as pd

import folium

from folium.plugins import HeatMapWithTime as HMWT

from tools.tools import Logger

import os

PATH = os.path.dirname(os.path.abspath(__file__))

# create logger
logger = Logger('SpaceRetail Log').logger

def create_maps():

    logger.info('Creating HeatMap....')

    data = pd.read_csv(PATH + '/../data/raw/raw_data_hourly.csv')

    data = data[~data.zone.isin(['zaragoza', 'zona_delicias', 'zona_casco'])]

    data = data.sort_values(by='timestamp')

    # datos pata heatmap con tiempo

    columns_data = ['visits', 'new_visits','recurrents', 'visitors_unique']

    for c in columns_data:

        logger.info(f'Creating HeatMap {c}....')

        df_lst = [data.loc[data.timestamp == hour, ['latitude', 'longitude', c]]\
                    .groupby(['latitude', 'longitude']).sum().reset_index().values.tolist()
                
                for hour in data.timestamp.sort_values().unique()]


        mapa=folium.Map([41.652, -0.89], zoom_start=15)

        HMWT(df_lst, 
            radius=30, 
            gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}, 
            min_opacity=0.5, 
            max_opacity=0.8, 
            use_local_extrema=True,
            auto_play=True,
            display_index=True,
            index=data.timestamp.unique().tolist(),
            ).add_to(mapa) 


        mapa.save(PATH + f'/../static/maps/map_{c}.html')

    logger.info('HeatMaps Saved.')

