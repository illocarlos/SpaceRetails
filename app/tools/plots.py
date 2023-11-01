import plotly
import plotly.graph_objects as go
import plotly.express as px
import json
import os

from flask import Markup

import pandas as pd

from scipy.stats import mode

from datetime import date, timedelta

PATH = os.path.dirname(os.path.abspath(__file__))


COLORS = ['#EF553B', '#B6E880', '#19d3f3', '#00cc96']


DAYS = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles',
        3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}


cambio_mes = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
              7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}


def percentage_indicator(value, reference):
    """
    Pinta las tarjetas de cada dashboard:

    value : float valor actual
    reference: float valor mes pasado

    return: json plot de la tarjeta
    """

    fig = go.Figure(go.Indicator(mode='delta+number',
                                 value=value,
                                 delta={'reference': reference,
                                        'relative': True},
                                 domain={'x': [0, 1], 'y': [0, 1]},
                                 gauge={'axis': {'range': [None, 100]}}))

    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                      'paper_bgcolor': 'rgba(0, 0, 0, 0)'})

    fig.update_layout(hovermode="x unified")

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def dashboard(zone):

    global cambio_mes

    data_mes = pd.read_csv(PATH + '/../data/raw/raw_data_monthly.csv')
    data_dia = pd.read_csv(PATH + '/../data/raw/raw_data_daily.csv')
    data_hora = pd.read_csv(PATH + '/../data/raw/raw_data_hourly.csv')
    data_arima = pd.read_csv(PATH + '/../data/raw/time_series_prediction.csv')

    data_mes = data_mes[data_mes.zone == zone]
    data_dia = data_dia[data_dia.zone == zone]
    data_hora = data_hora[data_hora.zone == zone]
    data_arima = data_arima[data_arima.zone == zone]

    visitors_unique, visits, new_visits, ratio, recurrents, avg_time, avg_time_zone = data_mes.iloc[-1][['visitors_unique',
                                                                                                        'visits',
                                                                                                         'new_visits',
                                                                                                         'ratio',
                                                                                                         'recurrents',
                                                                                                         'visittime_avg',
                                                                                                         'visit_time_zone_avg']]

    visitors_unique_last, visits_last, new_visits_last, ratio_last, recurrents_last, avg_time_last, avg_time_zone_last = data_mes.iloc[-2][['visitors_unique',
                                                                                                                                            'visits',
                                                                                                                                            'new_visits',
                                                                                                                                            'ratio',
                                                                                                                                            'recurrents',
                                                                                                                                            'visittime_avg',
                                                                                                                                            'visit_time_zone_avg']]

    grupo_dia = data_dia.groupby(['year', 'month']).agg({'visitors_unique': 'sum',
                                                        'visits': 'sum',
                                                         'new_visits': 'sum',
                                                         'ratio': 'mean',
                                                         'recurrents': 'sum',
                                                         'visittime_avg': 'mean',
                                                         'visit_time_zone_avg': 'mean',
                                                         'icon': lambda x: mode(x)[0][0],
                                                         }).reset_index()

    grupo_hora = data_hora.groupby(['year', 'month']).agg(
        {'visitors_unique': 'sum'}).reset_index()

    weather = grupo_dia.iloc[-1]['icon']

    # mejor dia
    best_day = data_dia[data_dia.month == grupo_dia.iloc[-1].month].groupby(
        'weekday').sum(numeric_only=True).visits.to_frame().reset_index()

    best_day_last = data_dia[data_dia.month == grupo_dia.iloc[-2].month].groupby(
        'weekday').sum(numeric_only=True).visits.to_frame().reset_index()

    mes = cambio_mes[grupo_dia.iloc[-1].month]

    best_day = best_day[best_day.visits ==
                        best_day.visits.max()].weekday.values[0]
    best_day_last = best_day_last[best_day_last.visits ==
                                  best_day_last.visits.max()].weekday.values[0]

    best_month_day = data_dia[data_dia.month == grupo_dia.iloc[-1].month].groupby('datetime').agg({'week': 'first',
                                                                                                   'weekday': 'first',
                                                                                                   'day': 'first',
                                                                                                   'visits': 'sum'})
    best_month_day = best_month_day[best_month_day.visits ==
                                    best_month_day.visits.max()]
    best_month_day = DAYS[best_month_day.iloc[0].weekday] + \
        f', {best_month_day.iloc[0].day}'

    # POR HORA
    # este mes
    best_hour = data_hora[data_hora.month == grupo_hora.iloc[-1].month].groupby(
        'hour').sum(numeric_only=True).visits.to_frame().reset_index()
    best_hour = best_hour[best_hour.visits ==
                          best_hour.visits.max()].hour.values[0]
    # mes pasado
    best_hour_last = data_hora[data_hora.month == grupo_hora.iloc[-2].month].groupby(
        'hour').sum(numeric_only=True).visits.to_frame().reset_index()
    best_hour_last = best_hour_last[best_hour_last.visits ==
                                    best_hour_last.visits.max()].hour.values[0]

    ## conversion dato ###

    visitors_unique = int(visitors_unique)
    visits = int(visits)
    new_visits = int(new_visits)
    ratio = round(ratio, 2)
    recurrents = int(recurrents)
    avg_time = round(avg_time/60, 2)
    avg_time_zone = round(avg_time_zone/60, 2)

    visitors_unique_last = int(visitors_unique_last)
    visits_last = int(visits_last)
    new_visits_last = int(new_visits_last)
    ratio_last = round(ratio_last, 2)
    recurrents_last = int(recurrents_last)
    avg_time_last = round(avg_time_last/60, 2)
    avg_time_zone_last = round(avg_time_zone_last/60, 2)

    ### plots ###
    unique_visitors_plot = percentage_indicator(
        visitors_unique, visitors_unique_last)
    visits_plot = percentage_indicator(visits, visits_last)
    new_visits_plot = percentage_indicator(new_visits, new_visits_last)
    ratio_plot = percentage_indicator(ratio, ratio_last)
    recurrents_plot = percentage_indicator(recurrents, recurrents_last)

    avg_time_plot = percentage_indicator(avg_time, avg_time_last)
    avg_time_zone_plot = percentage_indicator(
        avg_time_zone, avg_time_zone_last)

    temp_plot = Markup(
        f'<img src="../static/img/clima/{weather}.png" width=75 style="left: 72px;">')

    best_day_plot = DAYS[best_day]
    best_hour_plot = f'0{best_hour}:00 - 0{best_hour+1}:00' if best_hour < 9 else (
        f'0{best_hour}:00 - {best_hour+1}:00' if best_hour == 9 else f'{best_hour}:00 - {best_hour+1}:00')

    # bar_plot
    df_plot_bar = data_hora[(data_hora.year == grupo_hora.iloc[-1].year) &
                            (data_hora.month == grupo_hora.iloc[-1].month)].groupby('hour').sum(numeric_only=True).visits.to_frame().reset_index()

    df_plot_bar.columns = ['Hora', 'Visitas']

    bar_plot = px.bar(df_plot_bar, x='Hora', y='Visitas')
    bar_plot.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                            'xaxis_title': None,
                            'yaxis_title': 'Visitas por Hora',
                            'autosize': True})

    bar_plot.update_traces(marker_color=COLORS[2])
    bar_plot.update_yaxes(showticklabels=False)
    bar_plot = json.dumps(bar_plot, cls=plotly.utils.PlotlyJSONEncoder)

    # area plot
    df_area_plot = data_dia[['date', 'visits', 'new_visits',
                             'recurrents', 'visitors_unique']].sort_values(by='date')
    df_area_plot.columns = ['date', 'Totales',
                            'Nuevas', 'Recurrentes', 'Unicos']

    df_lst = []
    for c in df_area_plot.columns:

        if c == 'date':
            continue

        df = pd.DataFrame()

        df['Dia'] = df_area_plot.date

        df['Diario'] = df_area_plot[c]

        df['Campo'] = c

        df_lst.append(df)

    df_area_plot = pd.concat(df_lst)

    today = date.today()

    df_area_plot = df_area_plot[df_area_plot['Dia']
                                > str(today - timedelta(days=90))]

    # datos de predicciones
    data_arima = data_arima[['date', 'visits',
                             'new_visits', 'recurrents',
                             'visitors_unique']]

    data_arima = data_arima.groupby(
        'date').sum().reset_index().sort_values(by='date')

    data_arima.columns = ['timestamp', 'Totales',
                          'Nuevas', 'Recurrentes', 'Unicos']

    df_lst = []
    for c in data_arima.columns:

        if c == 'timestamp':
            continue

        df = pd.DataFrame()

        df['Dia'] = data_arima.timestamp

        df['Diario'] = data_arima[c]

        df['Campo'] = c

        df_lst.append(df)

    data_arima = pd.concat(df_lst)

    data_arima = data_arima[data_arima.Dia > df_area_plot.Dia.max()]

    # fechas grises en el grafico (preds)
    x0 = df_area_plot.Dia.max()
    x1 = data_arima.Dia.max()

    # union dataframes (verdad y prediccion)
    df_area_plot = pd.concat([df_area_plot, data_arima])

    area_plot = px.area(df_area_plot,
                        x='Dia', y='Diario',
                        color='Campo', line_group='Campo',
                        )

    area_plot.update_yaxes(showticklabels=False)
    area_plot.update_xaxes(title='')

    area_plot.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                             'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                             'yaxis_title': 'Evolutivo Diario',
                             'showlegend': False,
                             'legend': {'font': {'size': 10}, 'itemwidth': 30},
                             'autosize': True
                             })

    area_plot.add_vrect(x0=x0,
                        x1=x1,
                        annotation_text='Predicción',

                        annotation_position='top left',
                        fillcolor='rgba(30,30,30,0.3)',
                        opacity=.4,
                        line_width=0)

    area_plot.update_traces(marker_color='#048ab2', stackgroup=None,
                            fill='tozeroy', hoveron='points+fills',
                            )

    # cambio tamaño texto etiqueta prediccion
    area_plot.layout.annotations[0]['font_size'] = 10
    # cambio de color del grafico
    plot_data = [e for e in area_plot.data]
    plot_data.sort(key=lambda x: x['legendgroup'])
    for i, e in enumerate(plot_data):
        e['line']['color'] = COLORS[i]

    area_plot.data = plot_data

    area_plot = json.dumps(area_plot, cls=plotly.utils.PlotlyJSONEncoder)

    return [unique_visitors_plot,
            visits_plot,
            ratio_plot,
            recurrents_plot,
            avg_time_plot,
            temp_plot,
            best_day_plot,
            best_hour_plot,
            bar_plot,
            area_plot,
            mes,
            new_visits_plot,
            avg_time_zone_plot,
            best_month_day
            ]
