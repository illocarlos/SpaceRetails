from tools.tools import Logger, GenerateReport, get_color_arrow, change_number, change_diff
from tools.get_data_from_api import report_data_from_api
import pandas as pd
import os

# create logger
logger = Logger('SpaceRetail Log').logger

PATH = os.path.dirname(os.path.abspath(__file__))


def load_data_by_date(month, year):
        
    try:
        # load data
        data_mes = pd.read_csv(PATH + f'/../reports/data/raw_nodos_mm.csv')
        data_dia = pd.read_csv(PATH + f'/../reports/data/raw_nodos_dd.csv')
        data_hora = pd.read_csv(PATH + f'/../reports/data/raw_nodos_hh.csv')
        data_flow = pd.read_csv(PATH + f'/../reports/data/flow_data.csv')
        data_ret = pd.read_csv(PATH + f'/../reports/data/retention_data.csv')
        data_range = pd.read_csv(PATH + f'/../reports/data/hour_range_data.csv')
        
        
    except:
        
        report_data_from_api(month, year)
        
        data_mes = pd.read_csv(PATH + f'/../reports/data/raw_nodos_mm.csv')
        data_dia = pd.read_csv(PATH + f'/../reports/data/raw_nodos_dd.csv')
        data_hora = pd.read_csv(PATH + f'/../reports/data/raw_nodos_hh.csv')
        data_flow = pd.read_csv(PATH + f'/../reports/data/flow_data.csv')
        data_ret = pd.read_csv(PATH + f'/../reports/data/retention_data.csv')
        data_range = pd.read_csv(PATH + f'/../reports/data/hour_range_data.csv')
        
    
    return data_mes, data_dia, data_hora, data_flow, data_ret, data_range



def get_report_data(zone, data_mes, data_dia, data_hora):
    
    
    data_hora = data_hora[data_hora.zone == zone]
    data_dia = data_dia[data_dia.zone == zone]
    data_mes = data_mes[data_mes.zone == zone]


    # sacado de los datos mensuales
    # este mes
    visitors_unique, visits, ratio, avg_time = data_mes.iloc[-1][['visitors_unique', 'visits', 'ratio', 'visit_time_zone_avg']]

    # mes pasado
    visitors_unique_last, visits_last, ratio_last, avg_time_last = data_mes.iloc[-2][['visitors_unique', 'visits', 'ratio', 'visit_time_zone_avg']]
        
    
    
    # calculo y transformacion
    visitors_unique = int(visitors_unique)
    visits = int(visits)
    ratio = round(ratio, 2)

    
    visitors_unique_diff = round((visitors_unique - visitors_unique_last)/visitors_unique_last*100, 2)
    visits_diff = round((visits - visits_last)/visits_last*100, 2)
    ratio_diff = round((ratio - ratio_last)/ratio_last*100, 2)
    avg_time_diff = round((avg_time - avg_time_last)/avg_time_last*100, 2)
    

    hour_avg_time = avg_time/60/60  # a horas
    minute_avg_time = avg_time/60  # a minutos
    second_avg_time = (minute_avg_time - int(minute_avg_time))*60
    
    avg_time_hour = f'0{int(hour_avg_time)}:' if hour_avg_time>1 else '00:' 
    avg_time_minute = f'0{int(minute_avg_time)}:' if minute_avg_time<10 else  f'{int(minute_avg_time)}:'
    avg_time_second = f'0{int(second_avg_time)} m' if second_avg_time<10 else f'{int(second_avg_time)} m'
    
    avg_time = avg_time_hour+avg_time_minute+avg_time_second
    
    data = [change_number(visitors_unique), change_diff(visitors_unique_diff), 
            change_number(visits), change_diff(visits_diff),
            change_diff(ratio), change_diff(ratio_diff), 
            avg_time, change_diff(avg_time_diff)]

    

    # rango de horas
    rangos_horas = data_hora.groupby(['year', 'month', 'day', 'hour']).agg({'visits': 'sum'}).reset_index()
    
    this_month = rangos_horas[rangos_horas.month==rangos_horas.iloc[-1].month]
    last_month = rangos_horas[rangos_horas.month==rangos_horas.iloc[-1].month-1]
    
    this_month = this_month.groupby(pd.cut(this_month.hour, [0, 2, 9, 13, 16, 20, 25])).sum().visits.values
    this_month[-1] = this_month[-1]+this_month[0]
    this_month = this_month[1:]
    this_month = this_month/this_month.sum()*100
    
    last_month = last_month.groupby(pd.cut(last_month.hour, [0, 2, 9, 13, 16, 20, 25])).sum().visits.values
    last_month[-1] = last_month[-1]+last_month[0]
    last_month = last_month[1:]
    last_month = last_month/last_month.sum()*100
    
    diff = this_month-last_month
    
    this_month = [change_diff(round(e, 2)) for e in this_month]
    diff = [change_diff(round(e, 2)) for e in diff]
    
    
    data = data + this_month + diff

    data.append(visits_last)
    
    return data



### Calle Delicias Report
def create_delicias_report(month, year, DATA_MES, DATA_DIA, DATA_HORA, DATA_FLOW, DATA_RET):

        
    ### CARGA PDF PLANTILLA
    report = GenerateReport(PATH + '/../reports/templates/calle_delicias_zaragoza.pdf')
    original = report.template_pdf
    
    
    
    ### DATA GENERAL  
    data_general = get_report_data('zona_delicias', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors = data_general[0]
    unique_visitors_diff = data_general[1]
    unique_visitors_color, unique_visitors_arrow = get_color_arrow(unique_visitors_diff)

    # visitas unicos por mes y mes anterior
    unique_visits = data_general[2]
    unique_visits_diff = data_general[3]
    unique_visits_color, unique_visits_arrow = get_color_arrow(unique_visits_diff)

    # ratio por mes y mes anterior
    ratio = data_general[4]
    ratio_diff = data_general[5]
    ratio_color, ratio_arrow = get_color_arrow(ratio_diff)

    # tiempo medio por mes y mes anterior
    avg_time = data_general[6]
    avg_time_diff =  data_general[7]
    avg_time_color, avg_time_arrow = get_color_arrow(avg_time_diff)
    
    
    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data_general[8]
    two_to_nine_diff = data_general[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data_general[9]
    nine_to_one_diff = data_general[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data_general[10]
    one_to_four_diff = data_general[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data_general[11]
    four_to_eight_diff = data_general[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data_general[12]
    eight_to_two_diff = data_general[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)
    
    
    
    # DATO RETENCION TEMPORAL

    data_ret = DATA_RET[DATA_RET.zone_name=='Calle_Delicias']
    data_ret = data_ret.groupby(['timestamp', 'name']).mean(numeric_only=True).value.reset_index()

    under_week = data_ret[data_ret.name=='Less than 1 week'].iloc[1]['value']
    under_week_diff = change_diff(round(under_week - data_ret[data_ret.name=='Less than 1 week'].iloc[0]['value'], 2))
    under_week = change_diff(round(under_week, 2))
    under_week_color, under_week_arrow = get_color_arrow(under_week_diff)


    one_two_week = data_ret[data_ret.name=='Between 1 and 2 weeks'].iloc[1]['value']
    one_two_week_diff = change_diff(round(one_two_week - data_ret[data_ret.name=='Between 1 and 2 weeks'].iloc[0]['value'], 2))
    one_two_week = change_diff(round(one_two_week, 2))
    one_two_week_color, one_two_week_arrow = get_color_arrow(one_two_week_diff)


    under_month = data_ret[data_ret.name=='Less than 1 month'].iloc[1]['value']
    under_month_diff = change_diff(round(under_month - data_ret[data_ret.name=='Less than 1 month'].iloc[0]['value'], 2))
    under_month = change_diff(round(under_month, 2))
    under_month_color, under_month_arrow = get_color_arrow(under_month_diff)



    # SIGUIENTE RETENCION
    in_week = data_ret[data_ret.name=='Only weekdays'].iloc[1]['value']
    in_week_diff = change_diff(round(in_week - data_ret[data_ret.name=='Only weekdays'].iloc[0]['value'], 2))
    in_week = change_diff(round(in_week, 2))
    in_week_color, in_week_arrow = get_color_arrow(in_week_diff)


    all_week = data_ret[data_ret.name=='Both'].iloc[1]['value']
    all_week_diff = change_diff(round(all_week - data_ret[data_ret.name=='Both'].iloc[0]['value'], 2))
    all_week = change_diff(round(all_week, 2))
    all_week_color, all_week_arrow = get_color_arrow(all_week_diff)


    weekend = data_ret[data_ret.name=='Only weekend'].iloc[1]['value']
    weekend_diff = change_diff(round(weekend - data_ret[data_ret.name=='Only weekend'].iloc[0]['value'], 2))
    weekend = change_diff(round(weekend, 2))
    weekend_color, weekend_arrow = get_color_arrow(weekend_diff)
    
    
    
    
    # ZONAS
    data_a = get_report_data('zona_a', DATA_MES, DATA_DIA, DATA_HORA)
    data_jardin = get_report_data('plaza_jardin', DATA_MES, DATA_DIA, DATA_HORA)
    data_b = get_report_data('zona_b', DATA_MES, DATA_DIA, DATA_HORA)

    sum_visits = int(data_a[2].replace('.', '')) + int(data_jardin[2].replace('.', '')) + int(data_b[2].replace('.', ''))
    sum_visits_last = int(data_a[-1] + data_jardin[-1] + data_b[-1])

    zone_a = round(int(data_a[2].replace('.', ''))/ sum_visits * 100, 2)
    zone_a_diff = change_diff(round(zone_a - (data_a[-1]/sum_visits_last*100), 2))
    zone_a = change_diff(zone_a)
    zone_a_color, zone_a_arrow = get_color_arrow(zone_a_diff)


    plaza_jardin = round(int(data_jardin[2].replace('.', ''))/sum_visits*100, 2)
    plaza_jardin_diff = change_diff(round(plaza_jardin - (data_jardin[-1]/sum_visits_last*100), 2))
    plaza_jardin = change_diff(plaza_jardin)
    plaza_jardin_color, plaza_jardin_arrow = get_color_arrow(plaza_jardin_diff)

    
    zone_b = round(int(data_b[2].replace('.', ''))/sum_visits*100, 2)
    zone_b_diff = change_diff(round(zone_b - (data_b[-1]/sum_visits_last*100), 2))
    zone_b = change_diff(zone_b)
    zone_b_color, zone_b_arrow = get_color_arrow(zone_b_diff)



    # FLUJO
    zona_a_to_zone_b = DATA_FLOW[(DATA_FLOW.start_zone=='zona_a') & (DATA_FLOW.end_zone=='zona_b')].value.values[1]
    zona_a_to_zone_b_diff = zona_a_to_zone_b - DATA_FLOW[(DATA_FLOW.start_zone=='zona_a') & (DATA_FLOW.end_zone=='zona_b')].value.values[0]
    zona_a_to_zone_b = change_diff(round(zona_a_to_zone_b, 2))
    zona_a_to_zone_b_diff = change_diff(round(zona_a_to_zone_b_diff, 2))
    zona_a_to_zone_b_color, zona_a_to_zone_b_arrow = get_color_arrow(zona_a_to_zone_b_diff)


    plaza_to_zone_a = DATA_FLOW[(DATA_FLOW.start_zone=='plaza_jardin') & (DATA_FLOW.end_zone=='zona_a')].value.values[1]
    plaza_to_zone_a_diff = plaza_to_zone_a - DATA_FLOW[(DATA_FLOW.start_zone=='plaza_jardin') & (DATA_FLOW.end_zone=='zona_a')].value.values[0]
    plaza_to_zone_a = change_diff(round(plaza_to_zone_a, 2))
    plaza_to_zone_a_diff = change_diff(round(plaza_to_zone_a_diff, 2))
    plaza_to_zone_a_color, plaza_to_zone_a_arrow = get_color_arrow(plaza_to_zone_a_diff)


    plaza_to_zone_b = DATA_FLOW[(DATA_FLOW.start_zone=='plaza_jardin') & (DATA_FLOW.end_zone=='zona_b')].value.values[1]
    plaza_to_zone_b_diff = plaza_to_zone_b - DATA_FLOW[(DATA_FLOW.start_zone=='plaza_jardin') & (DATA_FLOW.end_zone=='zona_b')].value.values[0]
    plaza_to_zone_b = change_diff(round(plaza_to_zone_b, 2))
    plaza_to_zone_b_diff = change_diff(round(plaza_to_zone_b_diff, 2))
    plaza_to_zone_b_color, plaza_to_zone_b_arrow = get_color_arrow(plaza_to_zone_b_diff)


    zona_b_to_zone_a = DATA_FLOW[(DATA_FLOW.start_zone=='zona_b') & (DATA_FLOW.end_zone=='zona_a')].value.values[1]
    zona_b_to_zone_a_diff = zona_b_to_zone_a - DATA_FLOW[(DATA_FLOW.start_zone=='zona_b') & (DATA_FLOW.end_zone=='zona_a')].value.values[0]
    zona_b_to_zone_a = change_diff(round(zona_b_to_zone_a, 2))
    zona_b_to_zone_a_diff = change_diff(round(zona_b_to_zone_a_diff, 2))
    zona_b_to_zone_a_color, zona_b_to_zone_a_arrow = get_color_arrow(zona_b_to_zone_a_diff)

    
    
    ### PDF - PARTE GENERAL
    
    # pagina 0  (portada)
    report.add_text_to_page(original.pages[0], f'{month} {year}', (890,530))
    report.merge()
    
    # pagina 1  (portada)
    report.add_text_to_page(original.pages[1], f'{month} {year}', (220,970))
    report.merge()


    # pagina 2  (portada)
    report.add_text_to_page(original.pages[2], f'{month} {year}', (220,970))
    report.merge()

    
 
    # pagina 3  (hoja 1 - usuarios unicos)
    report.add_text_to_page(original.pages[3], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[3], f'{unique_visitors}', (840,400), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[3], f'{unique_visitors_arrow} {unique_visitors_diff} %', (880,320), fontsize=24, RGB=unique_visitors_color)
    report.merge()


    # pagina 4   (hoja 2 - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[4], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[4], f'{unique_visitors}', (380,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[4], f'{unique_visitors_arrow} {unique_visitors_diff} %', (425,390), fontsize=24, RGB=unique_visitors_color)
    report.add_text_to_page(original.pages[4], f'{unique_visits}', (1355,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[4], f'{unique_visits_arrow} {unique_visits_diff} %', (1395,390), fontsize=24, RGB=unique_visits_color)
    report.merge()
    
    
    

    # pagina 5    (hoja 3 - ratio)
    report.add_text_to_page(original.pages[5], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[5], f'{ratio}', (1020,357), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[5], f'{ratio_arrow} {ratio_diff} %', (925,250), fontsize=28, RGB=ratio_color)
    report.merge()


    # pagina 6    (hoja 4 - tiempo medio)
    report.add_text_to_page(original.pages[6], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[6], f'{avg_time}', (835,340), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[6], f'{avg_time_arrow} {avg_time_diff} %', (900,250), fontsize=28, RGB=avg_time_color)
    report.merge()


    # pagina 7   (hoja 5 - menos de 1 semana, 1-2 semana, menos de 1 mes)
    report.add_text_to_page(original.pages[7], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[7], f'{under_week} %', (270,470), fontsize=60, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[7], f'{under_week_arrow} {under_week_diff} %', (310,420), fontsize=28, RGB=under_week_color)
    report.add_text_to_page(original.pages[7], f'{one_two_week} %', (885,470), fontsize=60, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[7], f'{one_two_week_arrow} {one_two_week_diff} %', (910,420), fontsize=28, RGB=one_two_week_color)
    report.add_text_to_page(original.pages[7], f'{under_month} %', (1505,470), fontsize=60, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[7], f'{under_month_arrow} {under_month_diff} %', (1535,420), fontsize=28, RGB=under_month_color)
    report.merge()
    


    # pagina 8   (hoja 5 - entre semana, toda la semana, fin de semana)
    report.add_text_to_page(original.pages[8], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[8], f'{in_week} %', (280,420), fontsize=60, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[8], f'{in_week_arrow} {in_week_diff} %', (290,350), fontsize=28, RGB=in_week_color)
    report.add_text_to_page(original.pages[8], f'{all_week} %', (890,420), fontsize=60, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[8], f'{all_week_arrow} {all_week_diff} %', (900,350), fontsize=28, RGB=all_week_color)
    report.add_text_to_page(original.pages[8], f'{weekend} %', (1520,420), fontsize=60, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[8], f'{weekend_arrow} {weekend_diff} %', (1525,350), fontsize=28, RGB=weekend_color)
    report.merge()



    # pagina 9   (hoja 6 - por horas, rangos, escalera)
    report.add_text_to_page(original.pages[9], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[9], f'{two_to_nine} %', (160,310), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[9], f'{two_to_nine_arrow} {two_to_nine_diff} %', (170,270), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[9], f'{nine_to_one} %', (522,555), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[9], f'{nine_to_one_arrow} {nine_to_one_diff} %', (537,515), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[9], f'{one_to_four} %', (922,394), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[9], f'{one_to_four_arrow} {one_to_four_diff} %', (935,355), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[9], f'{four_to_eight} %', (1295,483), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[9], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1305,440), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[9], f'{eight_to_two} %', (1705,430), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[9], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1720,395), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    # pagina 10   (hoja 7 - 3 zonas desde arriba)
    report.add_text_to_page(original.pages[10], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[10], f'{unique_visits}', (1077,690), fontsize=35, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{zone_a} %', (470,415), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{zone_a_arrow} {zone_a_diff} %', (640,417), fontsize=28, RGB=zone_a_color)
    report.add_text_to_page(original.pages[10], f'{plaza_jardin} %', (908,415), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{plaza_jardin_arrow} {plaza_jardin_diff} %', (905,360), fontsize=28, RGB=plaza_jardin_color)
    report.add_text_to_page(original.pages[10], f'{zone_b} %', (1220,415), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{zone_b_arrow} {zone_b_diff} %', (1370,417), fontsize=28, RGB=zone_b_color)
    report.merge()
    
    
    # pagina 11   (hoja 7 - 3 zonas desde arriba más flujo)
    report.add_text_to_page(original.pages[11], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[11], f'{zone_a} %', (470,415), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{zone_a_arrow} {zone_a_diff} %', (640,417), fontsize=28, RGB=zone_a_color)
    report.add_text_to_page(original.pages[11], f'{plaza_jardin} %', (908,405), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{plaza_jardin_arrow} {plaza_jardin_diff} %', (905,350), fontsize=28, RGB=plaza_jardin_color)
    report.add_text_to_page(original.pages[11], f'{zone_b} %', (1220,415), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{zone_b_arrow} {zone_b_diff} %', (1370,417), fontsize=28, RGB=zone_b_color)
    report.add_text_to_page(original.pages[11], f'{zona_b_to_zone_a} %', (915,665), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{zona_b_to_zone_a_arrow} {zona_b_to_zone_a_diff} %', (915,630), fontsize=28, RGB=zona_b_to_zone_a_color)
    report.add_text_to_page(original.pages[11], f'{zona_a_to_zone_b} %', (910,205), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{zona_a_to_zone_b_arrow} {zona_a_to_zone_b_diff} %', (895,170), fontsize=28, RGB=zona_a_to_zone_b_color)
    report.add_text_to_page(original.pages[11], f'{plaza_to_zone_b} %', (1100,350), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{plaza_to_zone_b_arrow} {plaza_to_zone_b_diff} %', (1105,315), fontsize=28, RGB=plaza_to_zone_b_color)
    report.add_text_to_page(original.pages[11], f'{plaza_to_zone_a} %', (705,350), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{plaza_to_zone_a_arrow} {plaza_to_zone_a_diff} %', (710,315), fontsize=28, RGB=plaza_to_zone_a_color)
    report.merge()
    
    
    
    ####### ZONA A
    data = get_report_data('zona_a', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors_zone = data[0]
    unique_visitors_zone_diff = data[1]
    unique_visitors_zone_color, unique_visitors_zone_arrow = get_color_arrow(unique_visitors_zone_diff)

    # visitas unicos por mes y mes anterior
    unique_visits_zone = data[2]
    unique_visits_zone_diff = data[3]
    unique_visits_zone_color, unique_visits_zone_arrow = get_color_arrow(unique_visits_zone_diff)

    # ratio por mes y mes anterior
    ratio_zone = data[4]
    ratio_zone_diff = data[5]
    ratio_zone_color, ratio_zone_arrow = get_color_arrow(ratio_zone_diff)

    # tiempo medio por mes y mes anterior
    avg_time_zone = data[6]
    avg_time_zone_diff =  data[7]
    avg_time_zone_color, avg_time_zone_arrow = get_color_arrow(avg_time_zone_diff)


    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data[8]
    two_to_nine_diff = data[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data[9]
    nine_to_one_diff = data[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data[10]
    one_to_four_diff = data[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data[11]
    four_to_eight_diff = data[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data[12]
    eight_to_two_diff = data[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)

    
    # pagina 12   (portada zona a)
    report.add_text_to_page(original.pages[12], '', (220,970))
    report.merge()


    # pagina 13   (zona a - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[13], f'{unique_visitors_zone}', (410,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[13], f'{unique_visitors_zone_arrow} {unique_visitors_zone_diff} %', (435,390), fontsize=24, RGB=unique_visitors_zone_color)
    report.add_text_to_page(original.pages[13], f'{unique_visits_zone}', (1355,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[13], f'{unique_visits_zone_arrow} {unique_visits_zone_diff} %', (1400,390), fontsize=24, RGB=unique_visits_zone_color)
    report.merge()


    # pagina 14   (zona a - ratio)
    report.add_text_to_page(original.pages[14], f'{ratio_zone}', (1020,362), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[14], f'{ratio_zone_arrow} {ratio_zone_diff} %', (930,255), fontsize=28, RGB=ratio_zone_color)
    report.merge()
    
    
    # pagina 15   (zona a - tiempo medio)
    report.add_text_to_page(original.pages[15], f'{avg_time_zone}', (840,345), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[15], f'{avg_time_zone_arrow} {avg_time_zone_diff} %', (905,250), fontsize=28, RGB=avg_time_zone_color)
    report.merge()



    # pagina 16   (zona a - escalera)
    report.add_text_to_page(original.pages[16], f'{two_to_nine} %', (145,285), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[16], f'{two_to_nine_arrow} {two_to_nine_diff} %', (155,250), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[16], f'{nine_to_one} %', (522,480), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[16], f'{nine_to_one_arrow} {nine_to_one_diff} %', (537,445), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[16], f'{one_to_four} %', (922,360), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[16], f'{one_to_four_arrow} {one_to_four_diff} %', (935,320), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[16], f'{four_to_eight} %', (1365,405), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[16], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1378,363), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[16], f'{eight_to_two} %', (1730,347), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[16], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1735,305), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    
    
    ####### ZONA B
    data = get_report_data('zona_b', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors_zone = data[0]
    unique_visitors_zone_diff = data[1]
    unique_visitors_zone_color, unique_visitors_zone_arrow = get_color_arrow(unique_visitors_zone_diff)

    # visitas unicos por mes y mes anterior
    unique_visits_zone = data[2]
    unique_visits_zone_diff = data[3]
    unique_visits_zone_color, unique_visits_zone_arrow = get_color_arrow(unique_visits_zone_diff)

    # ratio por mes y mes anterior
    ratio_zone = data[4]
    ratio_zone_diff = data[5]
    ratio_zone_color, ratio_zone_arrow = get_color_arrow(ratio_zone_diff)

    # tiempo medio por mes y mes anterior
    avg_time_zone = data[6]
    avg_time_zone_diff =  data[7]
    avg_time_zone_color, avg_time_zone_arrow = get_color_arrow(avg_time_zone_diff)


    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data[8]
    two_to_nine_diff = data[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data[9]
    nine_to_one_diff = data[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data[10]
    one_to_four_diff = data[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data[11]
    four_to_eight_diff = data[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data[12]
    eight_to_two_diff = data[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)

    
    # pagina 17   (portada zona b)
    report.add_text_to_page(original.pages[17], f'{month} {year}', (220,970))
    report.merge()


    # pagina 18   (zona b - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[18], f'{unique_visitors_zone}', (400,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[18], f'{unique_visitors_zone_arrow} {unique_visitors_zone_diff} %', (425,390), fontsize=24, RGB=unique_visitors_zone_color)
    report.add_text_to_page(original.pages[18], f'{unique_visits_zone}', (1355,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[18], f'{unique_visits_zone_arrow} {unique_visits_zone_diff} %', (1400,390), fontsize=24, RGB=unique_visits_zone_color)
    report.merge()


    # pagina 19   (zona b - ratio)
    report.add_text_to_page(original.pages[19], f'{ratio_zone}', (1020,352), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[19], f'{ratio_zone_arrow} {ratio_zone_diff} %', (930,255), fontsize=28, RGB=ratio_zone_color)
    report.merge()


    # pagina 20   (zona b - tiempo medio)
    report.add_text_to_page(original.pages[20], f'{avg_time_zone}', (840,345), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[20], f'{avg_time_zone_arrow} {avg_time_zone_diff} %', (905,250), fontsize=28, RGB=avg_time_zone_color)
    report.merge()
    
    
    # pagina 21   (zona b - escalera)
    report.add_text_to_page(original.pages[21], f'{two_to_nine} %', (145,317), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[21], f'{two_to_nine_arrow} {two_to_nine_diff} %', (155,280), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[21], f'{nine_to_one} %', (515,543), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[21], f'{nine_to_one_arrow} {nine_to_one_diff} %', (525,505), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[21], f'{one_to_four} %', (922,430), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[21], f'{one_to_four_arrow} {one_to_four_diff} %', (940,390), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[21], f'{four_to_eight} %', (1365,485), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[21], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1373,449), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[21], f'{eight_to_two} %', (1710,355), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[21], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1720,320), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    
    
    ####### ZONA PLAZA JARDIN VERTICAL
    data = get_report_data('plaza_jardin', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors_zone = data[0]
    unique_visitors_zone_diff = data[1]
    unique_visitors_zone_color, unique_visitors_zone_arrow = get_color_arrow(unique_visitors_zone_diff)

    # visitas unicos por mes y mes anterior
    unique_visits_zone = data[2]
    unique_visits_zone_diff = data[3]
    unique_visits_zone_color, unique_visits_zone_arrow = get_color_arrow(unique_visits_zone_diff)

    # ratio por mes y mes anterior
    ratio_zone = data[4]
    ratio_zone_diff = data[5]
    ratio_zone_color, ratio_zone_arrow = get_color_arrow(ratio_zone_diff)

    # tiempo medio por mes y mes anterior
    avg_time_zone = data[6]
    avg_time_zone_diff =  data[7]
    avg_time_zone_color, avg_time_zone_arrow = get_color_arrow(avg_time_zone_diff)


    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data[8]
    two_to_nine_diff = data[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data[9]
    nine_to_one_diff = data[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data[10]
    one_to_four_diff = data[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data[11]
    four_to_eight_diff = data[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data[12]
    eight_to_two_diff = data[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)
    
    
    # pagina 22   (portada zona plaza)
    report.add_text_to_page(original.pages[22], '', (220,970))
    report.merge()


    # pagina 23   (zona plaza - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[23], f'{unique_visitors_zone}', (400,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[23], f'{unique_visitors_zone_arrow} {unique_visitors_zone_diff} %', (425,390), fontsize=24, RGB=unique_visitors_zone_color)
    report.add_text_to_page(original.pages[23], f'{unique_visits_zone}', (1355,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[23], f'{unique_visits_zone_arrow} {unique_visits_zone_diff} %', (1400,390), fontsize=24, RGB=unique_visits_zone_color)
    report.merge()


    # pagina 24   (zona plaza - ratio)
    report.add_text_to_page(original.pages[24], f'{ratio_zone}', (1020,362), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[24], f'{ratio_zone_arrow} {ratio_zone_diff} %', (930,255), fontsize=28, RGB=ratio_zone_color)
    report.merge()


    # pagina 25   (zona plaza - tiempo medio)
    report.add_text_to_page(original.pages[25], f'{avg_time_zone}', (840,345), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[25], f'{avg_time_zone_arrow} {avg_time_zone_diff} %', (905,250), fontsize=28, RGB=avg_time_zone_color)
    report.merge()
    
    
    # pagina 26   (zona plaza - escalera)
    report.add_text_to_page(original.pages[26], f'{two_to_nine} %', (137,307), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[26], f'{two_to_nine_arrow} {two_to_nine_diff} %', (140,273), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[26], f'{nine_to_one} %', (535,510), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[26], f'{nine_to_one_arrow} {nine_to_one_diff} %', (545,475), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[26], f'{one_to_four} %', (940,360), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[26], f'{one_to_four_arrow} {one_to_four_diff} %', (957,320), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[26], f'{four_to_eight} %', (1320,435), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[26], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1330,395), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[26], f'{eight_to_two} %', (1690,350), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[26], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1700,315), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    
    
    ##### CONCLUSIONES 


    # pagina 27   (conclusiones tipo)
    report.add_text_to_page(original.pages[27], f'{month} {year}', (890,530))
    report.merge()

    # pagina 28   (conclusiones tipo zona a - portada)
    report.add_text_to_page(original.pages[28], '', (890,530))
    report.merge()

    # pagina 29   (conclusiones tipo zona a - portada)
    report.add_text_to_page(original.pages[29], '', (890,530))
    report.merge()
    
    
    # pagina 30   (conclusiones tipo zona a - primera parte)
    # DATOS
    data_zone_a_daily = DATA_DIA[(DATA_DIA.zone=='zona_a') & (DATA_DIA.month_name==month)]
    data_zone_a_hourly = DATA_HORA[(DATA_HORA.zone=='zona_a') & (DATA_HORA.month_name==month)]

    best_day_new_unique = data_zone_a_daily[data_zone_a_daily.visitors_unique==data_zone_a_daily.visitors_unique.max()]
    best_day_new_unique_users = f'{best_day_new_unique.dayofweek.values[0]} {best_day_new_unique.day.values[0]} de {month}'
    new_unique_users = int(best_day_new_unique.visitors_unique.values[0])
    new_unique_users_diff = change_diff(round(new_unique_users/data_zone_a_daily.visitors_unique.sum()*100, 2))
    new_unique_users = change_number(new_unique_users)
    unique_users = change_number(int(data_zone_a_daily.visitors_unique.sum()))

    best_hour_new_unique = data_zone_a_hourly.sort_values(by='visitors_unique', ascending=False)
    best_hour_new_unique_users = best_hour_new_unique.iloc[0]['timestamp'].split('T')[1][:-3]
    hour_new_unique_users = change_number(int(best_hour_new_unique.iloc[0]['visitors_unique']))

    second_hour_new_unique_users = best_hour_new_unique.iloc[1]['timestamp'].split('T')[1][:-3]
    hour_second_unique_users = change_number(int(best_hour_new_unique.iloc[1]['visitors_unique']))

    avg_hour_new_unique_users = change_diff(round(data_zone_a_hourly.groupby('hour')['visitors_unique'].mean().mean(), 2))


    best_day_recurrent = data_zone_a_daily[data_zone_a_daily.recurrents==data_zone_a_daily.recurrents.max()]
    best_day_recurrent_users = f'{best_day_recurrent.dayofweek.values[0]} {best_day_recurrent.day.values[0]} de {month}'
    recurrent_users = int(best_day_recurrent.recurrents.values[0])
    recurrent_users_diff = change_diff(round(recurrent_users/data_zone_a_daily.recurrents.sum()*100, 2))
    recurrent_users = change_number(recurrent_users)
    second_unique_visits = change_number(int(data_zone_a_daily.recurrents.sum()))

    best_hour_recurrent = data_zone_a_hourly.sort_values(by='recurrents', ascending=False)
    best_hour_recurrent_users = best_hour_recurrent.iloc[0]['timestamp'].split('T')[1][:-3]
    hour_recurrent_users = change_number(int(best_hour_recurrent.iloc[0]['recurrents']))

    second_hour_recurrent_users = best_hour_recurrent.iloc[1]['timestamp'].split('T')[1][:-3]
    hour_second_recurrent_users = change_number(int(best_hour_recurrent.iloc[1]['recurrents']))

    avg_hour_recurrent_users = change_diff(round(data_zone_a_hourly.groupby('hour')['recurrents'].mean().mean(), 2))
    

    # add to pdf
    # UUN
    report.add_text_to_page(original.pages[30], best_day_new_unique_users, (195,740), fontsize=23)
    report.add_text_to_page(original.pages[30], f'{new_unique_users}', (1410,740), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{new_unique_users_diff}', (1735,740), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{unique_users}', (505,710), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{best_hour_new_unique_users}', (1022,676), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{hour_new_unique_users}', (1185,676), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{second_hour_new_unique_users}', (915,642), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{hour_second_unique_users}', (1200,642), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{avg_hour_new_unique_users}', (570,610), fontsize=25)


    # UUR
    report.add_text_to_page(original.pages[30], best_day_recurrent_users, (200,417), fontsize=23)
    report.add_text_to_page(original.pages[30], f'{recurrent_users}', (1355,415), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{recurrent_users_diff}', (1670,415), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{second_unique_visits}', (555,380), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{best_hour_recurrent_users}', (1130,350), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{hour_recurrent_users}', (1315,350), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{second_hour_recurrent_users}', (790,317), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{hour_second_recurrent_users}', (1110,317), fontsize=25)
    report.add_text_to_page(original.pages[30], f'{avg_hour_recurrent_users}', (580,283), fontsize=25)

    report.merge()
    
    # pagina 31   (conclusiones tipo zona a - segunda parte)
    # ordenado por dias, mejor
    questions = data_zone_a_daily.sort_values(by='visits', ascending=False).reset_index(drop=True)

    first_question = f'{questions.loc[0, "dayofweek"]} {questions.loc[0, "day"]} de {month} - {int(questions.loc[0, "visits"])} visitas.'
    second_question = f'{questions.loc[1, "dayofweek"]} {questions.loc[1, "day"]} de {month} - {int(questions.loc[1, "visits"])} visitas.'
    third_question = f'{questions.loc[2, "dayofweek"]} {questions.loc[2, "day"]} de {month} - {int(questions.loc[2, "visits"])} visitas.'
    forth_question = f'{questions.loc[3, "dayofweek"]} {questions.loc[3, "day"]} de {month} - {int(questions.loc[3, "visits"])} visitas.'


    report.add_text_to_page(original.pages[31], f'{first_question}', (700,674), fontsize=35)
    report.add_text_to_page(original.pages[31], f'{second_question}', (700,576), fontsize=35)
    report.add_text_to_page(original.pages[31], f'{third_question}', (700,478), fontsize=35)
    report.add_text_to_page(original.pages[31], f'{forth_question}', (700,380), fontsize=35)
    report.merge()




    # pagina 32   (conclusiones tipo zona a - tercera parte)
    # ordenado por dias, peor

    questions = data_zone_a_daily.sort_values(by='visits', ascending=True).reset_index(drop=True)

    first_question = f'{questions.loc[0, "dayofweek"]} {questions.loc[0, "day"]} de {month} - {int(questions.loc[0, "visits"])} visitas.'
    second_question = f'{questions.loc[1, "dayofweek"]} {questions.loc[1, "day"]} de {month} - {int(questions.loc[1, "visits"])} visitas.'
    third_question = f'{questions.loc[2, "dayofweek"]} {questions.loc[2, "day"]} de {month} - {int(questions.loc[2, "visits"])} visitas.'
    forth_question = f'{questions.loc[3, "dayofweek"]} {questions.loc[3, "day"]} de {month} - {int(questions.loc[3, "visits"])} visitas.'


    report.add_text_to_page(original.pages[32], f'{first_question}', (700,678), fontsize=35)
    report.add_text_to_page(original.pages[32], f'{second_question}', (700,580), fontsize=35)
    report.add_text_to_page(original.pages[32], f'{third_question}', (700,482), fontsize=35)
    report.add_text_to_page(original.pages[32], f'{forth_question}', (700,384), fontsize=35)
    report.merge()
    
   
    # pagina 33  (conclusiones tipo zona b - portada)
    report.add_text_to_page(original.pages[33], '', (890,530))
    report.merge()




    # pagina 34   (conclusiones tipo zona b - primera parte)
    # datos
    data_zone_a_daily = DATA_DIA[(DATA_DIA.zone=='zona_b') & (DATA_DIA.month_name==month)]
    data_zone_a_hourly = DATA_HORA[(DATA_HORA.zone=='zona_b') & (DATA_HORA.month_name==month)]

    best_day_new_unique = data_zone_a_daily[data_zone_a_daily.visitors_unique==data_zone_a_daily.visitors_unique.max()]
    best_day_new_unique_users = f'{best_day_new_unique.dayofweek.values[0]} {best_day_new_unique.day.values[0]} de {month}'
    new_unique_users = int(best_day_new_unique.visitors_unique.values[0])
    new_unique_users_diff = change_diff(round(new_unique_users/data_zone_a_daily.visitors_unique.sum()*100, 2))
    new_unique_users = change_number(new_unique_users)
    unique_users = change_number(int(data_zone_a_daily.visitors_unique.sum()))

    best_hour_new_unique = data_zone_a_hourly.sort_values(by='visitors_unique', ascending=False)
    best_hour_new_unique_users = best_hour_new_unique.iloc[0]['timestamp'].split('T')[1][:-3]
    hour_new_unique_users = change_number(int(best_hour_new_unique.iloc[0]['visitors_unique']))

    second_hour_new_unique_users = best_hour_new_unique.iloc[1]['timestamp'].split('T')[1][:-3]
    hour_second_unique_users = change_number(int(best_hour_new_unique.iloc[1]['visitors_unique']))

    avg_hour_new_unique_users = change_diff(round(data_zone_a_hourly.groupby('hour')['visitors_unique'].mean().mean(), 2))


    best_day_recurrent = data_zone_a_daily[data_zone_a_daily.recurrents==data_zone_a_daily.recurrents.max()]
    best_day_recurrent_users = f'{best_day_recurrent.dayofweek.values[0]} {best_day_recurrent.day.values[0]} de {month}'
    recurrent_users = int(best_day_recurrent.recurrents.values[0])
    recurrent_users_diff = change_diff(round(recurrent_users/data_zone_a_daily.recurrents.sum()*100, 2))
    recurrent_users = change_number(recurrent_users)
    second_unique_visits = change_number(int(data_zone_a_daily.recurrents.sum()))

    best_hour_recurrent = data_zone_a_hourly.sort_values(by='recurrents', ascending=False)
    best_hour_recurrent_users = best_hour_recurrent.iloc[0]['timestamp'].split('T')[1][:-3]
    hour_recurrent_users = change_number(int(best_hour_recurrent.iloc[0]['recurrents']))

    second_hour_recurrent_users = best_hour_recurrent.iloc[1]['timestamp'].split('T')[1][:-3]
    hour_second_recurrent_users = change_number(int(best_hour_recurrent.iloc[1]['recurrents']))

    avg_hour_recurrent_users = change_diff(round(data_zone_a_hourly.groupby('hour')['recurrents'].mean().mean(), 2))

    
    # add to pdf
    # UUN
    report.add_text_to_page(original.pages[34], best_day_new_unique_users, (195,758), fontsize=23)
    report.add_text_to_page(original.pages[34], f'{new_unique_users}', (1310,758), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{new_unique_users_diff}', (1645,758), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{unique_users}', (490,722), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{best_hour_new_unique_users}', (1025,691), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{hour_new_unique_users}', (1180,691), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{second_hour_new_unique_users}', (895,657), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{hour_second_unique_users}', (1185,657), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{avg_hour_new_unique_users}', (570,625), fontsize=25)


    # UUR
    report.add_text_to_page(original.pages[34], best_day_recurrent_users, (200,449), fontsize=23)
    report.add_text_to_page(original.pages[34], f'{recurrent_users}', (1355,449), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{recurrent_users_diff}', (1670,449), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{second_unique_visits}', (550,413), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{best_hour_recurrent_users}', (1133,382), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{hour_recurrent_users}', (1310,382), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{second_hour_recurrent_users}', (770,347), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{hour_second_recurrent_users}', (1090,347), fontsize=25)
    report.add_text_to_page(original.pages[34], f'{avg_hour_recurrent_users}', (573,315), fontsize=25)

    report.merge()
    
    # pagina 35   (conclusiones tipo zona b - segunda parte)
    # ordenado por dias, mejor

    questions = data_zone_a_daily.sort_values(by='visits', ascending=False).reset_index(drop=True)

    first_question = f'{questions.loc[0, "dayofweek"]} {questions.loc[0, "day"]} de {month} - {int(questions.loc[0, "visits"])} visitas.'
    second_question = f'{questions.loc[1, "dayofweek"]} {questions.loc[1, "day"]} de {month} - {int(questions.loc[1, "visits"])} visitas.'
    third_question = f'{questions.loc[2, "dayofweek"]} {questions.loc[2, "day"]} de {month} - {int(questions.loc[2, "visits"])} visitas.'
    forth_question = f'{questions.loc[3, "dayofweek"]} {questions.loc[3, "day"]} de {month} - {int(questions.loc[3, "visits"])} visitas.'


    report.add_text_to_page(original.pages[35], f'{first_question}', (700,674), fontsize=35)
    report.add_text_to_page(original.pages[35], f'{second_question}', (700,576), fontsize=35)
    report.add_text_to_page(original.pages[35], f'{third_question}', (700,478), fontsize=35)
    report.add_text_to_page(original.pages[35], f'{forth_question}', (700,380), fontsize=35)
    report.merge()
    
    # pagina 36   (conclusiones tipo zona b - tercera parte)
    # ordenado por dias, peor

    questions = data_zone_a_daily.sort_values(by='visits', ascending=True).reset_index(drop=True)

    first_question = f'{questions.loc[0, "dayofweek"]} {questions.loc[0, "day"]} de {month} - {int(questions.loc[0, "visits"])} visitas.'
    second_question = f'{questions.loc[1, "dayofweek"]} {questions.loc[1, "day"]} de {month} - {int(questions.loc[1, "visits"])} visitas.'
    third_question = f'{questions.loc[2, "dayofweek"]} {questions.loc[2, "day"]} de {month} - {int(questions.loc[2, "visits"])} visitas.'
    forth_question = f'{questions.loc[3, "dayofweek"]} {questions.loc[3, "day"]} de {month} - {int(questions.loc[3, "visits"])} visitas.'

    report.add_text_to_page(original.pages[36], f'{first_question}', (692,696), fontsize=35)
    report.add_text_to_page(original.pages[36], f'{second_question}', (692,598), fontsize=35)
    report.add_text_to_page(original.pages[36], f'{third_question}', (692,502), fontsize=35)
    report.add_text_to_page(original.pages[36], f'{forth_question}', (692,405), fontsize=35)
    report.merge()




    # pagina 37   ()
    report.add_text_to_page(original.pages[37], f'{month} {year}', (890,530))
    report.merge()
    
    
    ### GUARDAR REPORTE 
    report.generate(PATH + f'/../reports/calle_delicias_zaragoza_{month}_{year}.pdf')



### Casco Historico Report
def create_casco_historico_report(month, year, DATA_MES, DATA_DIA, DATA_HORA, DATA_FLOW, DATA_RET):
    
    
    ### CARGA PDF PLANTILLA
    report = GenerateReport(PATH + '/../reports/templates/casco_historico_zaragoza.pdf')
    original = report.template_pdf


    
    ##### DATOS GENERALES CASCO HISTORICO
    data_general = get_report_data('zona_casco', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors = data_general[0]
    unique_visitors_diff = data_general[1]
    unique_visitors_color, unique_visitors_arrow = get_color_arrow(unique_visitors_diff)

    # visitas unicos por mes y mes anterior
    unique_visits = data_general[2]
    unique_visits_diff = data_general[3]
    unique_visits_color, unique_visits_arrow = get_color_arrow(unique_visits_diff)

    # ratio por mes y mes anterior
    ratio = data_general[4]
    ratio_diff = data_general[5]
    ratio_color, ratio_arrow = get_color_arrow(ratio_diff)

    # tiempo medio por mes y mes anterior
    avg_time = data_general[6]
    avg_time_diff =  data_general[7]
    avg_time_color, avg_time_arrow = get_color_arrow(avg_time_diff)
    
    
    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data_general[8]
    two_to_nine_diff = data_general[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data_general[9]
    nine_to_one_diff = data_general[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data_general[10]
    one_to_four_diff = data_general[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data_general[11]
    four_to_eight_diff = data_general[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data_general[12]
    eight_to_two_diff = data_general[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)
    
    
    
    # DATO RETENCION TEMPORAL

    data_ret = DATA_RET[DATA_RET.zone_name=='Casco_Historico']
    data_ret = data_ret.groupby(['timestamp', 'name']).mean(numeric_only=True).value.reset_index()

    under_week = data_ret[data_ret.name=='Less than 1 week'].iloc[1]['value']
    under_week_diff = change_diff(round(under_week - data_ret[data_ret.name=='Less than 1 week'].iloc[0]['value'], 2))
    under_week = change_diff(round(under_week, 2))
    under_week_color, under_week_arrow = get_color_arrow(under_week_diff)


    one_two_week = data_ret[data_ret.name=='Between 1 and 2 weeks'].iloc[1]['value']
    one_two_week_diff = change_diff(round(one_two_week - data_ret[data_ret.name=='Between 1 and 2 weeks'].iloc[0]['value'], 2))
    one_two_week = change_diff(round(one_two_week, 2))
    one_two_week_color, one_two_week_arrow = get_color_arrow(one_two_week_diff)


    under_month = data_ret[data_ret.name=='Less than 1 month'].iloc[1]['value']
    under_month_diff = change_diff(round(under_month - data_ret[data_ret.name=='Less than 1 month'].iloc[0]['value'], 2))
    under_month = change_diff(round(under_month, 2))
    under_month_color, under_month_arrow = get_color_arrow(under_month_diff)



    # SIGUIENTE RETENCION
    in_week = data_ret[data_ret.name=='Only weekdays'].iloc[1]['value']
    in_week_diff = change_diff(round(in_week - data_ret[data_ret.name=='Only weekdays'].iloc[0]['value'], 2))
    in_week = change_diff(round(in_week, 2))
    in_week_color, in_week_arrow = get_color_arrow(in_week_diff)


    all_week = data_ret[data_ret.name=='Both'].iloc[1]['value']
    all_week_diff = change_diff(round(all_week - data_ret[data_ret.name=='Both'].iloc[0]['value'], 2))
    all_week = change_diff(round(all_week, 2))
    all_week_color, all_week_arrow = get_color_arrow(all_week_diff)


    weekend = data_ret[data_ret.name=='Only weekend'].iloc[1]['value']
    weekend_diff = change_diff(round(weekend - data_ret[data_ret.name=='Only weekend'].iloc[0]['value'], 2))
    weekend = change_diff(round(weekend, 2))
    weekend_color, weekend_arrow = get_color_arrow(weekend_diff)
    
    
    
    
    # ZONAS
    data_c = get_report_data('zona_c', DATA_MES, DATA_DIA, DATA_HORA)
    data_d = get_report_data('zona_d', DATA_MES, DATA_DIA, DATA_HORA)
    data_e = get_report_data('zona_e', DATA_MES, DATA_DIA, DATA_HORA)
    data_f = get_report_data('zona_f', DATA_MES, DATA_DIA, DATA_HORA)
    data_g = get_report_data('zona_g', DATA_MES, DATA_DIA, DATA_HORA)
    data_h = get_report_data('zona_h', DATA_MES, DATA_DIA, DATA_HORA)
    
    data_felipe = get_report_data('plaza_san_felipe', DATA_MES, DATA_DIA, DATA_HORA)
    data_pedro = get_report_data('plaza_san_pedro_nolasco', DATA_MES, DATA_DIA, DATA_HORA)
    data_justicia = get_report_data('plaza_justicia', DATA_MES, DATA_DIA, DATA_HORA)

    
    sum_visits = int(data_c[2].replace('.', '')) + int(data_d[2].replace('.', '')) + int(data_e[2].replace('.', ''))+ \
                 int(data_f[2].replace('.', '')) + int(data_g[2].replace('.', '')) + int(data_h[2].replace('.', ''))+ \
                 int(data_felipe[2].replace('.', '')) + int(data_pedro[2].replace('.', '')) + int(data_justicia[2].replace('.', ''))
                 
    sum_visits_last = int(data_c[-1] + data_d[-1] + data_e[-1] + data_f[-1] + data_g[-1] + data_h[-1] + data_felipe[-1] + data_pedro[-1] + data_justicia[-1])


    zone_c = round(int(data_c[2].replace('.', ''))/ sum_visits * 100, 2)
    zone_c_diff = change_diff(round(zone_c - (data_c[-1]/sum_visits_last*100), 2))
    zone_c = change_diff(zone_c)
    zone_c_color, zone_c_arrow = get_color_arrow(zone_c_diff)


    zone_d = round(int(data_d[2].replace('.', ''))/ sum_visits * 100, 2)
    zone_d_diff = change_diff(round(zone_d - (data_d[-1]/sum_visits_last*100), 2))
    zone_d = change_diff(zone_d)
    zone_d_color, zone_d_arrow = get_color_arrow(zone_d_diff)


    zone_e = round(int(data_e[2].replace('.', ''))/ sum_visits * 100, 2)
    zone_e_diff = change_diff(round(zone_e - (data_e[-1]/sum_visits_last*100), 2))
    zone_e = change_diff(zone_e)
    zone_e_color, zone_e_arrow = get_color_arrow(zone_e_diff)


    zone_f = round(int(data_f[2].replace('.', ''))/ sum_visits * 100, 2)
    zone_f_diff = change_diff(round(zone_f - (data_f[-1]/sum_visits_last*100), 2))
    zone_f = change_diff(zone_f)
    zone_f_color, zone_f_arrow = get_color_arrow(zone_f_diff)


    zone_g = round(int(data_g[2].replace('.', ''))/ sum_visits * 100, 2)
    zone_g_diff = change_diff(round(zone_g - (data_g[-1]/sum_visits_last*100), 2))
    zone_g = change_diff(zone_g)
    zone_g_color, zone_g_arrow = get_color_arrow(zone_g_diff)


    zone_h = round(int(data_h[2].replace('.', ''))/ sum_visits * 100, 2)
    zone_h_diff = change_diff(round(zone_h - (data_h[-1]/sum_visits_last*100), 2))
    zone_h = change_diff(zone_h)
    zone_h_color, zone_h_arrow = get_color_arrow(zone_h_diff)


    plaza_justicia = round(int(data_justicia[2].replace('.', ''))/int(unique_visits.replace('.', ''))*100, 2)
    plaza_justicia_diff = change_diff(round(plaza_justicia - (data_justicia[-1]/sum_visits_last*100), 2))
    plaza_justicia = change_diff(plaza_justicia)
    plaza_justicia_color, plaza_justicia_arrow = get_color_arrow(plaza_justicia_diff)

    plaza_felipe = round(int(data_felipe[2].replace('.', ''))/int(unique_visits.replace('.', ''))*100, 2)
    plaza_felipe_diff = change_diff(round(plaza_felipe - (data_felipe[-1]/sum_visits_last*100), 2))
    plaza_felipe = change_diff(plaza_felipe)
    plaza_felipe_color, plaza_felipe_arrow = get_color_arrow(plaza_felipe_diff)

    plaza_pedro = round(int(data_pedro[2].replace('.', ''))/int(unique_visits.replace('.', ''))*100, 2)
    plaza_pedro_diff = change_diff(round(plaza_pedro - (data_pedro[-1]/sum_visits_last*100), 2))
    plaza_pedro = change_diff(plaza_pedro)
    plaza_pedro_color, plaza_pedro_arrow = get_color_arrow(plaza_justicia_diff)
    
    
    # FLUJO
    zona_f_to_zone_g = DATA_FLOW[(DATA_FLOW.start_zone=='zona_f') & (DATA_FLOW.end_zone=='zona_g')].value.values[1]
    zona_f_to_zone_g_diff = zona_f_to_zone_g - DATA_FLOW[(DATA_FLOW.start_zone=='zona_f') & (DATA_FLOW.end_zone=='zona_g')].value.values[0]
    zona_f_to_zone_g = change_diff(round(zona_f_to_zone_g, 2))
    zona_f_to_zone_g_diff = change_diff(round(zona_f_to_zone_g_diff, 2))
    zona_f_to_zone_g_color, zona_f_to_zone_g_arrow = get_color_arrow(zona_f_to_zone_g_diff)


    zona_f_to_plaza_justicia = DATA_FLOW[(DATA_FLOW.start_zone=='zona_f') & (DATA_FLOW.end_zone=='plaza_justicia')].value.values[1]
    zona_f_to_plaza_justicia_diff = zona_f_to_plaza_justicia - DATA_FLOW[(DATA_FLOW.start_zone=='zona_f') & (DATA_FLOW.end_zone=='plaza_justicia')].value.values[0]
    zona_f_to_plaza_justicia = change_diff(round(zona_f_to_plaza_justicia, 2))
    zona_f_to_plaza_justicia_diff = change_diff(round(zona_f_to_plaza_justicia_diff, 2))
    zona_f_to_plaza_justicia_color, zona_f_to_plaza_justicia_arrow = get_color_arrow(zona_f_to_plaza_justicia_diff)


    zona_h_to_zone_g = DATA_FLOW[(DATA_FLOW.start_zone=='zona_h') & (DATA_FLOW.end_zone=='zona_g')].value.values[1]
    zona_h_to_zone_g_diff = zona_h_to_zone_g - DATA_FLOW[(DATA_FLOW.start_zone=='zona_h') & (DATA_FLOW.end_zone=='zona_g')].value.values[0]
    zona_h_to_zone_g = change_diff(round(zona_h_to_zone_g, 2))
    zona_h_to_zone_g_diff = change_diff(round(zona_h_to_zone_g_diff, 2))
    zona_h_to_zone_g_color, zona_h_to_zone_g_arrow = get_color_arrow(zona_h_to_zone_g_diff)
    
    
    zona_h_to_plaza_justicia = DATA_FLOW[(DATA_FLOW.start_zone=='zona_h') & (DATA_FLOW.end_zone=='plaza_justicia')].value.values[1]
    zona_h_to_plaza_justicia_diff = zona_h_to_plaza_justicia - DATA_FLOW[(DATA_FLOW.start_zone=='zona_h') & (DATA_FLOW.end_zone=='plaza_justicia')].value.values[0]
    zona_h_to_plaza_justicia = change_diff(round(zona_h_to_plaza_justicia, 2))
    zona_h_to_plaza_justicia_diff = change_diff(round(zona_h_to_plaza_justicia_diff, 2))
    zona_h_to_plaza_justicia_color, zona_h_to_plaza_justicia_arrow = get_color_arrow(zona_h_to_plaza_justicia_diff)


    zona_c_to_plaza_felipe = DATA_FLOW[(DATA_FLOW.start_zone=='zona_c') & (DATA_FLOW.end_zone=='plaza_san_felipe')].value.values[1]
    zona_c_to_plaza_felipe_diff = zona_c_to_plaza_felipe - DATA_FLOW[(DATA_FLOW.start_zone=='zona_c') & (DATA_FLOW.end_zone=='plaza_san_felipe')].value.values[0]
    zona_c_to_plaza_felipe = change_diff(round(zona_c_to_plaza_felipe, 2))
    zona_c_to_plaza_felipe_diff = change_diff(round(zona_c_to_plaza_felipe_diff, 2))
    zona_c_to_plaza_felipe_color, zona_c_to_plaza_felipe_arrow = get_color_arrow(zona_c_to_plaza_felipe_diff)



    zona_e_to_plaza_felipe = DATA_FLOW[(DATA_FLOW.start_zone=='zona_e') & (DATA_FLOW.end_zone=='plaza_san_felipe')].value.values[1]
    zona_e_to_plaza_felipe_diff = zona_e_to_plaza_felipe - DATA_FLOW[(DATA_FLOW.start_zone=='zona_e') & (DATA_FLOW.end_zone=='plaza_san_felipe')].value.values[0]
    zona_e_to_plaza_felipe = change_diff(round(zona_e_to_plaza_felipe, 2))
    zona_e_to_plaza_felipe_diff = change_diff(round(zona_e_to_plaza_felipe_diff, 2))
    zona_e_to_plaza_felipe_color, zona_e_to_plaza_felipe_arrow = get_color_arrow(zona_e_to_plaza_felipe_diff)


    zona_e_to_plaza_pedro = DATA_FLOW[(DATA_FLOW.start_zone=='zona_e') & (DATA_FLOW.end_zone=='plaza_san_pedro_nolasco')].value.values[1]
    zona_e_to_plaza_pedro_diff = zona_e_to_plaza_pedro - DATA_FLOW[(DATA_FLOW.start_zone=='zona_e') & (DATA_FLOW.end_zone=='plaza_san_pedro_nolasco')].value.values[0]
    zona_e_to_plaza_pedro = change_diff(round(zona_e_to_plaza_pedro, 2))
    zona_e_to_plaza_pedro_diff = change_diff(round(zona_e_to_plaza_pedro_diff, 2))
    zona_e_to_plaza_pedro_color, zona_e_to_plaza_pedro_arrow = get_color_arrow(zona_e_to_plaza_pedro_diff)


    zona_e_to_zone_d = DATA_FLOW[(DATA_FLOW.start_zone=='zona_e') & (DATA_FLOW.end_zone=='zona_d')].value.values[1]
    zona_e_to_zone_d_diff = zona_e_to_zone_d - DATA_FLOW[(DATA_FLOW.start_zone=='zona_e') & (DATA_FLOW.end_zone=='zona_d')].value.values[0]
    zona_e_to_zone_d = change_diff(round(zona_e_to_zone_d, 2))
    zona_e_to_zone_d_diff = change_diff(round(zona_e_to_zone_d_diff, 2))
    zona_e_to_zone_d_color, zona_e_to_zone_d_arrow = get_color_arrow(zona_e_to_zone_d_diff)
    
    
    
    ##### PDF


    # pagina 0  (portada)
    report.add_text_to_page(original.pages[0], f'{month} {year}', (890,530))
    report.merge()


    # pagina 1  (portada)
    report.add_text_to_page(original.pages[1], f'{month} {year}', (220,980))
    report.merge()


    # pagina 2  (portada)
    report.add_text_to_page(original.pages[2], f'{month} {year}', (235,970))
    report.merge()



    # pagina 3  (hoja 1 - usuarios unicos)
    report.add_text_to_page(original.pages[3], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[3], f'{unique_visitors}', (830,400), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[3], f'{unique_visitors_arrow} {unique_visitors_diff} %', (880,320), fontsize=24, RGB=unique_visitors_color)
    report.merge()
    
    
    # pagina 4   (hoja 2 - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[4], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[4], f'{unique_visitors}', (370,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[4], f'{unique_visitors_arrow} {unique_visitors_diff} %', (425,390), fontsize=24, RGB=unique_visitors_color)
    report.add_text_to_page(original.pages[4], f'{unique_visits}', (1345,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[4], f'{unique_visits_arrow} {unique_visits_diff} %', (1390,390), fontsize=24, RGB=unique_visits_color)
    report.merge()


    # pagina 5    (hoja 3 - ratio)
    report.add_text_to_page(original.pages[5], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[5], f'{ratio}', (1015,354), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[5], f'{ratio_arrow} {ratio_diff} %', (915,250), fontsize=28, RGB=ratio_color)
    report.merge()


    # pagina 6    (hoja 4 - tiempo medio)
    report.add_text_to_page(original.pages[6], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[6], f'{avg_time}', (835,340), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[6], f'{avg_time_arrow} {avg_time_diff} %', (890,250), fontsize=28, RGB=avg_time_color)
    report.merge()

    
    # pagina 7   (hoja 5 - menos de 1 semana, 1-2 semana, menos de 1 mes)
    report.add_text_to_page(original.pages[7], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[7], f'{under_week} %', (270,470), fontsize=60, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[7], f'{under_week_arrow} {under_week_diff} %', (310,420), fontsize=28, RGB=under_week_color)
    report.add_text_to_page(original.pages[7], f'{one_two_week} %', (885,470), fontsize=60, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[7], f'{one_two_week_arrow} {one_two_week_diff} %', (910,420), fontsize=28, RGB=one_two_week_color)
    report.add_text_to_page(original.pages[7], f'{under_month} %', (1505,470), fontsize=60, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[7], f'{under_month_arrow} {under_month_diff} %', (1535,420), fontsize=28, RGB=under_month_color)
    report.merge()



    # pagina 8   (hoja 5 - entre semana, toda la semana, fin de semana)
    report.add_text_to_page(original.pages[8], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[8], f'{in_week} %', (280,420), fontsize=60, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[8], f'{in_week_arrow} {in_week_diff} %', (290,350), fontsize=28, RGB=in_week_color)
    report.add_text_to_page(original.pages[8], f'{all_week} %', (890,420), fontsize=60, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[8], f'{all_week_arrow} {all_week_diff} %', (900,350), fontsize=28, RGB=all_week_color)
    report.add_text_to_page(original.pages[8], f'{weekend} %', (1520,420), fontsize=60, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[8], f'{weekend_arrow} {weekend_diff} %', (1525,350), fontsize=28, RGB=weekend_color)
    report.merge()



    # pagina 9   (hoja 6 - por horas, rangos, escalera)
    report.add_text_to_page(original.pages[9], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[9], f'{two_to_nine} %', (160,310), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[9], f'{two_to_nine_arrow} {two_to_nine_diff} %', (178,270), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[9], f'{nine_to_one} %', (528,547), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[9], f'{nine_to_one_arrow} {nine_to_one_diff} %', (538,512), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[9], f'{one_to_four} %', (910,394), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[9], f'{one_to_four_arrow} {one_to_four_diff} %', (920,355), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[9], f'{four_to_eight} %', (1295,478), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[9], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1305,440), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[9], f'{eight_to_two} %', (1700,450), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[9], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1710,412), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    
    # pagina 10   (hoja 7 - zonas desde arriba)
    report.add_text_to_page(original.pages[10], f'{month} {year}', (220,970))
    report.add_text_to_page(original.pages[10], f'{unique_visits}', (1060,690), fontsize=35, RGB=[255, 255, 255])

    report.add_text_to_page(original.pages[10], f'{zone_f} %', (340,515), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{zone_f_arrow} {zone_f_diff} %', (342,490), fontsize=18, RGB=zone_f_color)
    report.add_text_to_page(original.pages[10], f'{plaza_justicia} %', (475,510), fontsize=20, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{plaza_justicia_arrow} {plaza_justicia_diff} %', (480,485), fontsize=16, RGB=plaza_justicia_color)
    report.add_text_to_page(original.pages[10], f'{zone_g} %', (630,515), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{zone_g_arrow} {zone_g_diff} %', (730,515), fontsize=18, RGB=zone_g_color)
    report.add_text_to_page(original.pages[10], f'{zone_h} %', (950,515), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{zone_h_arrow} {zone_h_diff} %', (950,490), fontsize=18, RGB=zone_h_color)

    report.add_text_to_page(original.pages[10], f'{zone_c} %', (375,262), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{zone_c_arrow} {zone_c_diff} %', (375,232), fontsize=18, RGB=zone_c_color)
    report.add_text_to_page(original.pages[10], f'{plaza_felipe} %', (533,260), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{plaza_felipe_arrow} {plaza_felipe_diff} %', (533,230), fontsize=18, RGB=plaza_felipe_color)
    report.add_text_to_page(original.pages[10], f'{zone_d} %', (850,262), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{zone_d_arrow} {zone_d_diff} %', (980,262), fontsize=18, RGB=zone_d_color)
    report.add_text_to_page(original.pages[10], f'{plaza_pedro} %', (1285,300), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{plaza_pedro_arrow} {plaza_pedro_diff} %', (1285,270), fontsize=18, RGB=plaza_pedro_color)
    report.add_text_to_page(original.pages[10], f'{zone_e} %', (1450,275), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[10], f'{zone_e_arrow} {zone_e_diff} %', (1550,277), fontsize=18, RGB=zone_e_color)

    report.merge()
    
    
    
    # pagina 11   (hoja 8 -  zonas norte desde arriba más flujo)
    report.add_text_to_page(original.pages[11], f'{month} {year}', (220,970))

    report.add_text_to_page(original.pages[11], f'{zone_c} %', (375,262), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{zone_c_arrow} {zone_c_diff} %', (375,232), fontsize=18, RGB=zone_c_color)
    report.add_text_to_page(original.pages[11], f'{plaza_felipe} %', (533,260), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{plaza_felipe_arrow} {plaza_felipe_diff} %', (533,230), fontsize=18, RGB=plaza_felipe_color)
    report.add_text_to_page(original.pages[11], f'{zone_d} %', (850,262), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{zone_d_arrow} {zone_d_diff} %', (980,262), fontsize=18, RGB=zone_d_color)
    report.add_text_to_page(original.pages[11], f'{plaza_pedro} %', (1285,300), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{plaza_pedro_arrow} {plaza_pedro_diff} %', (1285,270), fontsize=18, RGB=plaza_pedro_color)
    report.add_text_to_page(original.pages[11], f'{zone_e} %', (1450,275), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{zone_e_arrow} {zone_e_diff} %', (1550,277), fontsize=18, RGB=zone_e_color)


    report.add_text_to_page(original.pages[11], f'{zona_c_to_plaza_felipe} %', (420,455), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{zona_c_to_plaza_felipe_arrow} {zona_c_to_plaza_felipe_diff} %', (420,424), fontsize=18, RGB=zona_c_to_plaza_felipe_color)
    report.add_text_to_page(original.pages[11], f'{zona_e_to_plaza_felipe} %', (1023,93), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{zona_e_to_plaza_felipe_arrow} {zona_e_to_plaza_felipe_diff} %', (1023,70), fontsize=18, RGB=zona_e_to_plaza_felipe_color)
    report.add_text_to_page(original.pages[11], f'{zona_e_to_plaza_pedro} %', (1480,117), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{zona_e_to_plaza_pedro_arrow} {zona_e_to_plaza_pedro_diff} %', (1480,93), fontsize=18, RGB=zona_e_to_plaza_pedro_color)
    report.add_text_to_page(original.pages[11], f'{zona_e_to_zone_d} %', (1210,550), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[11], f'{zona_e_to_zone_d_arrow} {zona_e_to_zone_d_diff} %', (1210,520), fontsize=18, RGB=zona_e_to_zone_d_color)

    report.merge()
    
    
    
    # pagina 12   (hoja 9 - zonas sur desde arriba más flujo)
    report.add_text_to_page(original.pages[12], f'{month} {year}', (220,970))

    report.add_text_to_page(original.pages[12], f'{zone_f} %', (340,515), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[12], f'{zone_f_arrow} {zone_f_diff} %', (342,490), fontsize=18, RGB=zone_f_color)
    report.add_text_to_page(original.pages[12], f'{plaza_justicia} %', (475,510), fontsize=20, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[12], f'{plaza_justicia_arrow} {plaza_justicia_diff} %', (480,485), fontsize=16, RGB=plaza_justicia_color)
    report.add_text_to_page(original.pages[12], f'{zone_g} %', (630,515), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[12], f'{zone_g_arrow} {zone_g_diff} %', (730,515), fontsize=18, RGB=zone_g_color)
    report.add_text_to_page(original.pages[12], f'{zone_h} %', (950,515), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[12], f'{zone_h_arrow} {zone_h_diff} %', (950,490), fontsize=18, RGB=zone_h_color)


    report.add_text_to_page(original.pages[12], f'{zona_f_to_zone_g} %', (495,720), fontsize=20, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[12], f'{zona_f_to_zone_g_arrow} {zona_f_to_zone_g_diff} %', (500,690), fontsize=16, RGB=zona_f_to_zone_g_color)
    report.add_text_to_page(original.pages[12], f'{zona_h_to_zone_g} %', (865,720), fontsize=20, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[12], f'{zona_h_to_zone_g_arrow} {zona_h_to_zone_g_diff} %', (867,690), fontsize=16, RGB=zona_h_to_zone_g_color)
    report.add_text_to_page(original.pages[12], f'{zona_f_to_plaza_justicia} %', (345,340), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[12], f'{zona_f_to_plaza_justicia_arrow} {zona_f_to_plaza_justicia_diff} %', (342,310), fontsize=18, RGB=zona_f_to_plaza_justicia_color)
    report.add_text_to_page(original.pages[12], f'{zona_h_to_plaza_justicia} %', (730,337), fontsize=22, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[12], f'{zona_h_to_plaza_justicia_arrow} {zona_h_to_plaza_justicia_diff} %', (727,303), fontsize=18, RGB=zona_h_to_plaza_justicia_color)

    report.merge()
    
    
    
    
    ####### ZONA C
    
    data = get_report_data('zona_c', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors_zone = data[0]
    unique_visitors_zone_diff = data[1]
    unique_visitors_zone_color, unique_visitors_zone_arrow = get_color_arrow(unique_visitors_zone_diff)

    # visitas unicos por mes y mes anterior
    unique_visits_zone = data[2]
    unique_visits_zone_diff = data[3]
    unique_visits_zone_color, unique_visits_zone_arrow = get_color_arrow(unique_visits_zone_diff)

    # ratio por mes y mes anterior
    ratio_zone = data[4]
    ratio_zone_diff = data[5]
    ratio_zone_color, ratio_zone_arrow = get_color_arrow(ratio_zone_diff)

    # tiempo medio por mes y mes anterior
    avg_time_zone = data[6]
    avg_time_zone_diff =  data[7]
    avg_time_zone_color, avg_time_zone_arrow = get_color_arrow(avg_time_zone_diff)


    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data[8]
    two_to_nine_diff = data[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data[9]
    nine_to_one_diff = data[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data[10]
    one_to_four_diff = data[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data[11]
    four_to_eight_diff = data[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data[12]
    eight_to_two_diff = data[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)
    
    
    
    # pagina 13   (portada zona c)
    report.add_text_to_page(original.pages[13], '', (220,970))
    report.merge()


    # pagina 14   (zona c - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[14], f'{unique_visitors_zone}', (405,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[14], f'{unique_visitors_zone_arrow} {unique_visitors_zone_diff} %', (430,390), fontsize=24, RGB=unique_visitors_zone_color)
    report.add_text_to_page(original.pages[14], f'{unique_visits_zone}', (1355,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[14], f'{unique_visits_zone_arrow} {unique_visits_zone_diff} %', (1400,390), fontsize=24, RGB=unique_visits_zone_color)
    report.merge()


    # pagina 15   (zona c - ratio)
    report.add_text_to_page(original.pages[15], f'{ratio_zone}', (1020,360), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[15], f'{ratio_zone_arrow} {ratio_zone_diff} %', (930,255), fontsize=28, RGB=ratio_zone_color)
    report.merge()


    # pagina 16   (zona c - tiempo medio)
    report.add_text_to_page(original.pages[16], f'{avg_time_zone}', (840,345), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[16], f'{avg_time_zone_arrow} {avg_time_zone_diff} %', (905,250), fontsize=28, RGB=avg_time_zone_color)
    report.merge()
    
    
    # pagina 17   (zona c - escalera)
    report.add_text_to_page(original.pages[17], f'{two_to_nine} %', (163,305), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[17], f'{two_to_nine_arrow} {two_to_nine_diff} %', (173,270), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[17], f'{nine_to_one} %', (502,540), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[17], f'{nine_to_one_arrow} {nine_to_one_diff} %', (517,505), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[17], f'{one_to_four} %', (910,450), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[17], f'{one_to_four_arrow} {one_to_four_diff} %', (923,410), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[17], f'{four_to_eight} %', (1305,465), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[17], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1318,433), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[17], f'{eight_to_two} %', (1700,430), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[17], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1705,400), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    ####### ZONA D
    
    data = get_report_data('zona_d', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors_zone = data[0]
    unique_visitors_zone_diff = data[1]
    unique_visitors_zone_color, unique_visitors_zone_arrow = get_color_arrow(unique_visitors_zone_diff)

    # visitas unicos por mes y mes anterior
    unique_visits_zone = data[2]
    unique_visits_zone_diff = data[3]
    unique_visits_zone_color, unique_visits_zone_arrow = get_color_arrow(unique_visits_zone_diff)

    # ratio por mes y mes anterior
    ratio_zone = data[4]
    ratio_zone_diff = data[5]
    ratio_zone_color, ratio_zone_arrow = get_color_arrow(ratio_zone_diff)

    # tiempo medio por mes y mes anterior
    avg_time_zone = data[6]
    avg_time_zone_diff =  data[7]
    avg_time_zone_color, avg_time_zone_arrow = get_color_arrow(avg_time_zone_diff)


    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data[8]
    two_to_nine_diff = data[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data[9]
    nine_to_one_diff = data[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data[10]
    one_to_four_diff = data[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data[11]
    four_to_eight_diff = data[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data[12]
    eight_to_two_diff = data[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)
    
    
    # pagina 18   (portada zona d)
    report.add_text_to_page(original.pages[18], '', (220,970))
    report.merge()


    # pagina 19   (zona d - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[19], f'{unique_visitors_zone}', (385,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[19], f'{unique_visitors_zone_arrow} {unique_visitors_zone_diff} %', (425,390), fontsize=24, RGB=unique_visitors_zone_color)
    report.add_text_to_page(original.pages[19], f'{unique_visits_zone}', (1355,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[19], f'{unique_visits_zone_arrow} {unique_visits_zone_diff} %', (1400,390), fontsize=24, RGB=unique_visits_zone_color)
    report.merge()


    # pagina 20   (zona d - ratio)
    report.add_text_to_page(original.pages[20], f'{ratio_zone}', (1020,360), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[20], f'{ratio_zone_arrow} {ratio_zone_diff} %', (930,255), fontsize=28, RGB=ratio_zone_color)
    report.merge()


    # pagina 21   (zona d - tiempo medio)
    report.add_text_to_page(original.pages[21], f'{avg_time_zone}', (840,345), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[21], f'{avg_time_zone_arrow} {avg_time_zone_diff} %', (905,250), fontsize=28, RGB=avg_time_zone_color)
    report.merge()

    
    
    # pagina 22   (zona d - escalera)
    report.add_text_to_page(original.pages[22], f'{two_to_nine} %', (163,305), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[22], f'{two_to_nine_arrow} {two_to_nine_diff} %', (173,270), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[22], f'{nine_to_one} %', (502,540), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[22], f'{nine_to_one_arrow} {nine_to_one_diff} %', (517,505), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[22], f'{one_to_four} %', (910,425), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[22], f'{one_to_four_arrow} {one_to_four_diff} %', (923,390), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[22], f'{four_to_eight} %', (1305,457), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[22], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1318,425), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[22], f'{eight_to_two} %', (1700,453), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[22], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1705,420), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    
    ####### ZONA E
    
    data = get_report_data('zona_e', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors_zone = data[0]
    unique_visitors_zone_diff = data[1]
    unique_visitors_zone_color, unique_visitors_zone_arrow = get_color_arrow(unique_visitors_zone_diff)

    # visitas unicos por mes y mes anterior
    unique_visits_zone = data[2]
    unique_visits_zone_diff = data[3]
    unique_visits_zone_color, unique_visits_zone_arrow = get_color_arrow(unique_visits_zone_diff)

    # ratio por mes y mes anterior
    ratio_zone = data[4]
    ratio_zone_diff = data[5]
    ratio_zone_color, ratio_zone_arrow = get_color_arrow(ratio_zone_diff)

    # tiempo medio por mes y mes anterior
    avg_time_zone = data[6]
    avg_time_zone_diff =  data[7]
    avg_time_zone_color, avg_time_zone_arrow = get_color_arrow(avg_time_zone_diff)


    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data[8]
    two_to_nine_diff = data[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data[9]
    nine_to_one_diff = data[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data[10]
    one_to_four_diff = data[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data[11]
    four_to_eight_diff = data[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data[12]
    eight_to_two_diff = data[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)
    
    
    # pagina 23   (portada zona e)
    report.add_text_to_page(original.pages[23], '', (220,970))
    report.merge()


    # pagina 24   (zona e - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[24], f'{unique_visitors_zone}', (395,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[24], f'{unique_visitors_zone_arrow} {unique_visitors_zone_diff} %', (425,390), fontsize=24, RGB=unique_visitors_zone_color)
    report.add_text_to_page(original.pages[24], f'{unique_visits_zone}', (1355,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[24], f'{unique_visits_zone_arrow} {unique_visits_zone_diff} %', (1400,390), fontsize=24, RGB=unique_visits_zone_color)
    report.merge()


    # pagina 25   (zona e - ratio)
    report.add_text_to_page(original.pages[25], f'{ratio_zone}', (1020,360), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[25], f'{ratio_zone_arrow} {ratio_zone_diff} %', (930,255), fontsize=28, RGB=ratio_zone_color)
    report.merge()


    # pagina 26   (zona e - tiempo medio)
    report.add_text_to_page(original.pages[26], f'{avg_time_zone}', (840,345), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[26], f'{avg_time_zone_arrow} {avg_time_zone_diff} %', (905,250), fontsize=28, RGB=avg_time_zone_color)
    report.merge()



    # pagina 27   (zona e - escalera)
    report.add_text_to_page(original.pages[27], f'{two_to_nine} %', (163,305), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[27], f'{two_to_nine_arrow} {two_to_nine_diff} %', (173,270), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[27], f'{nine_to_one} %', (517,540), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[27], f'{nine_to_one_arrow} {nine_to_one_diff} %', (532,505), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[27], f'{one_to_four} %', (905,405), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[27], f'{one_to_four_arrow} {one_to_four_diff} %', (918,370), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[27], f'{four_to_eight} %', (1301,467), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[27], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1314,435), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[27], f'{eight_to_two} %', (1700,453), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[27], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1705,420), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    
    ####### ZONA F
    
    data = get_report_data('zona_f', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors_zone = data[0]
    unique_visitors_zone_diff = data[1]
    unique_visitors_zone_color, unique_visitors_zone_arrow = get_color_arrow(unique_visitors_zone_diff)

    # visitas unicos por mes y mes anterior
    unique_visits_zone = data[2]
    unique_visits_zone_diff = data[3]
    unique_visits_zone_color, unique_visits_zone_arrow = get_color_arrow(unique_visits_zone_diff)

    # ratio por mes y mes anterior
    ratio_zone = data[4]
    ratio_zone_diff = data[5]
    ratio_zone_color, ratio_zone_arrow = get_color_arrow(ratio_zone_diff)

    # tiempo medio por mes y mes anterior
    avg_time_zone = data[6]
    avg_time_zone_diff =  data[7]
    avg_time_zone_color, avg_time_zone_arrow = get_color_arrow(avg_time_zone_diff)


    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data[8]
    two_to_nine_diff = data[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data[9]
    nine_to_one_diff = data[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data[10]
    one_to_four_diff = data[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data[11]
    four_to_eight_diff = data[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data[12]
    eight_to_two_diff = data[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)
    
    
    
    # pagina 28   (portada zona f)
    report.add_text_to_page(original.pages[28], '', (220,970))
    report.merge()


    # pagina 29   (zona f - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[29], f'{unique_visitors_zone}', (380,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[29], f'{unique_visitors_zone_arrow} {unique_visitors_zone_diff} %', (425,390), fontsize=24, RGB=unique_visitors_zone_color)
    report.add_text_to_page(original.pages[29], f'{unique_visits_zone}', (1375,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[29], f'{unique_visits_zone_arrow} {unique_visits_zone_diff} %', (1400,390), fontsize=24, RGB=unique_visits_zone_color)
    report.merge()


    # pagina 30   (zona f - ratio)
    report.add_text_to_page(original.pages[30], f'{ratio_zone}', (1020,360), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[30], f'{ratio_zone_arrow} {ratio_zone_diff} %', (930,255), fontsize=28, RGB=ratio_zone_color)
    report.merge()


    # pagina 31   (zona f - tiempo medio)
    report.add_text_to_page(original.pages[31], f'{avg_time_zone}', (840,345), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[31], f'{avg_time_zone_arrow} {avg_time_zone_diff} %', (905,250), fontsize=28, RGB=avg_time_zone_color)
    report.merge()



    # pagina 32   (zona f - escalera)
    report.add_text_to_page(original.pages[32], f'{two_to_nine} %', (163,305), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[32], f'{two_to_nine_arrow} {two_to_nine_diff} %', (173,270), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[32], f'{nine_to_one} %', (517,540), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[32], f'{nine_to_one_arrow} {nine_to_one_diff} %', (532,505), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[32], f'{one_to_four} %', (905,400), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[32], f'{one_to_four_arrow} {one_to_four_diff} %', (918,365), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[32], f'{four_to_eight} %', (1301,482), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[32], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1314,450), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[32], f'{eight_to_two} %', (1700,438), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[32], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1705,405), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    
    ####### ZONA G
    
    data = get_report_data('zona_g', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors_zone = data[0]
    unique_visitors_zone_diff = data[1]
    unique_visitors_zone_color, unique_visitors_zone_arrow = get_color_arrow(unique_visitors_zone_diff)

    # visitas unicos por mes y mes anterior
    unique_visits_zone = data[2]
    unique_visits_zone_diff = data[3]
    unique_visits_zone_color, unique_visits_zone_arrow = get_color_arrow(unique_visits_zone_diff)

    # ratio por mes y mes anterior
    ratio_zone = data[4]
    ratio_zone_diff = data[5]
    ratio_zone_color, ratio_zone_arrow = get_color_arrow(ratio_zone_diff)

    # tiempo medio por mes y mes anterior
    avg_time_zone = data[6]
    avg_time_zone_diff =  data[7]
    avg_time_zone_color, avg_time_zone_arrow = get_color_arrow(avg_time_zone_diff)


    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data[8]
    two_to_nine_diff = data[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data[9]
    nine_to_one_diff = data[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data[10]
    one_to_four_diff = data[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data[11]
    four_to_eight_diff = data[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data[12]
    eight_to_two_diff = data[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)
    
    
    # pagina 33   (portada zona g)
    report.add_text_to_page(original.pages[33], '', (220,970))
    report.merge()


    # pagina 34   (zona g - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[34], f'{unique_visitors_zone}', (380,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[34], f'{unique_visitors_zone_arrow} {unique_visitors_zone_diff} %', (425,390), fontsize=24, RGB=unique_visitors_zone_color)
    report.add_text_to_page(original.pages[34], f'{unique_visits_zone}', (1375,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[34], f'{unique_visits_zone_arrow} {unique_visits_zone_diff} %', (1400,390), fontsize=24, RGB=unique_visits_zone_color)
    report.merge()


    # pagina 35   (zona g - ratio)
    report.add_text_to_page(original.pages[35], f'{ratio_zone}', (1020,360), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[35], f'{ratio_zone_arrow} {ratio_zone_diff} %', (930,255), fontsize=28, RGB=ratio_zone_color)
    report.merge()


    # pagina 36   (zona g - tiempo medio)
    report.add_text_to_page(original.pages[36], f'{avg_time_zone}', (840,345), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[36], f'{avg_time_zone_arrow} {avg_time_zone_diff} %', (905,250), fontsize=28, RGB=avg_time_zone_color)
    report.merge()



    # pagina 37   (zona g - escalera)
    report.add_text_to_page(original.pages[37], f'{two_to_nine} %', (163,305), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[37], f'{two_to_nine_arrow} {two_to_nine_diff} %', (173,270), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[37], f'{nine_to_one} %', (517,540), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[37], f'{nine_to_one_arrow} {nine_to_one_diff} %', (532,505), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[37], f'{one_to_four} %', (925,400), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[37], f'{one_to_four_arrow} {one_to_four_diff} %', (938,365), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[37], f'{four_to_eight} %', (1301,477), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[37], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1314,445), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[37], f'{eight_to_two} %', (1700,448), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[37], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1705,415), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    
    
    ####### ZONA H
    
    data = get_report_data('zona_h', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors_zone = data[0]
    unique_visitors_zone_diff = data[1]
    unique_visitors_zone_color, unique_visitors_zone_arrow = get_color_arrow(unique_visitors_zone_diff)

    # visitas unicos por mes y mes anterior
    unique_visits_zone = data[2]
    unique_visits_zone_diff = data[3]
    unique_visits_zone_color, unique_visits_zone_arrow = get_color_arrow(unique_visits_zone_diff)

    # ratio por mes y mes anterior
    ratio_zone = data[4]
    ratio_zone_diff = data[5]
    ratio_zone_color, ratio_zone_arrow = get_color_arrow(ratio_zone_diff)

    # tiempo medio por mes y mes anterior
    avg_time_zone = data[6]
    avg_time_zone_diff =  data[7]
    avg_time_zone_color, avg_time_zone_arrow = get_color_arrow(avg_time_zone_diff)


    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data[8]
    two_to_nine_diff = data[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data[9]
    nine_to_one_diff = data[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data[10]
    one_to_four_diff = data[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data[11]
    four_to_eight_diff = data[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data[12]
    eight_to_two_diff = data[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)
    
    
    # pagina 38   (portada zona h)
    report.add_text_to_page(original.pages[38], '', (220,970))
    report.merge()


    # pagina 39   (zona h - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[39], f'{unique_visitors_zone}', (380,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[39], f'{unique_visitors_zone_arrow} {unique_visitors_zone_diff} %', (425,390), fontsize=24, RGB=unique_visitors_zone_color)
    report.add_text_to_page(original.pages[39], f'{unique_visits_zone}', (1375,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[39], f'{unique_visits_zone_arrow} {unique_visits_zone_diff} %', (1400,390), fontsize=24, RGB=unique_visits_zone_color)
    report.merge()


    # pagina 40   (zona h - ratio)
    report.add_text_to_page(original.pages[40], f'{ratio_zone}', (1020,360), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[40], f'{ratio_zone_arrow} {ratio_zone_diff} %', (930,255), fontsize=28, RGB=ratio_zone_color)
    report.merge()


    # pagina 41   (zona h - tiempo medio)
    report.add_text_to_page(original.pages[41], f'{avg_time_zone}', (840,345), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[41], f'{avg_time_zone_arrow} {avg_time_zone_diff} %', (905,250), fontsize=28, RGB=avg_time_zone_color)
    report.merge()



    # pagina 42   (zona h - escalera)
    report.add_text_to_page(original.pages[42], f'{two_to_nine} %', (163,330), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[42], f'{two_to_nine_arrow} {two_to_nine_diff} %', (173,295), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[42], f'{nine_to_one} %', (514,560), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[42], f'{nine_to_one_arrow} {nine_to_one_diff} %', (529,525), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[42], f'{one_to_four} %', (915,430), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[42], f'{one_to_four_arrow} {one_to_four_diff} %', (928,395), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[42], f'{four_to_eight} %', (1311,497), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[42], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1324,465), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[42], f'{eight_to_two} %', (1700,478), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[42], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1705,445), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    
    ####### PLAZA SAN FELIPE
    
    data = get_report_data('plaza_san_felipe', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors_zone = data[0]
    unique_visitors_zone_diff = data[1]
    unique_visitors_zone_color, unique_visitors_zone_arrow = get_color_arrow(unique_visitors_zone_diff)

    # visitas unicos por mes y mes anterior
    unique_visits_zone = data[2]
    unique_visits_zone_diff = data[3]
    unique_visits_zone_color, unique_visits_zone_arrow = get_color_arrow(unique_visits_zone_diff)

    # ratio por mes y mes anterior
    ratio_zone = data[4]
    ratio_zone_diff = data[5]
    ratio_zone_color, ratio_zone_arrow = get_color_arrow(ratio_zone_diff)

    # tiempo medio por mes y mes anterior
    avg_time_zone = data[6]
    avg_time_zone_diff =  data[7]
    avg_time_zone_color, avg_time_zone_arrow = get_color_arrow(avg_time_zone_diff)


    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data[8]
    two_to_nine_diff = data[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data[9]
    nine_to_one_diff = data[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data[10]
    one_to_four_diff = data[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data[11]
    four_to_eight_diff = data[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data[12]
    eight_to_two_diff = data[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)
    
    
    
    # pagina 43   (portada plaza san felipe)
    report.add_text_to_page(original.pages[43], '', (220,970))
    report.merge()


    # pagina 44   (plaza san felipe - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[44], f'{unique_visitors_zone}', (380,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[44], f'{unique_visitors_zone_arrow} {unique_visitors_zone_diff} %', (425,390), fontsize=24, RGB=unique_visitors_zone_color)
    report.add_text_to_page(original.pages[44], f'{unique_visits_zone}', (1355,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[44], f'{unique_visits_zone_arrow} {unique_visits_zone_diff} %', (1400,390), fontsize=24, RGB=unique_visits_zone_color)
    report.merge()


    # pagina 45   (plaza san felipe - ratio)
    report.add_text_to_page(original.pages[45], f'{ratio_zone}', (1020,360), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[45], f'{ratio_zone_arrow} {ratio_zone_diff} %', (930,255), fontsize=28, RGB=ratio_zone_color)
    report.merge()


    # pagina 46   (plaza san felipe - tiempo medio)
    report.add_text_to_page(original.pages[46], f'{avg_time_zone}', (840,345), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[46], f'{avg_time_zone_arrow} {avg_time_zone_diff} %', (905,250), fontsize=28, RGB=avg_time_zone_color)
    report.merge()



    # pagina 47   (plaza san felipe - escalera)
    report.add_text_to_page(original.pages[47], f'{two_to_nine} %', (113,240), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[47], f'{two_to_nine_arrow} {two_to_nine_diff} %', (123,205), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[47], f'{nine_to_one} %', (514,530), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[47], f'{nine_to_one_arrow} {nine_to_one_diff} %', (529,495), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[47], f'{one_to_four} %', (915,420), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[47], f'{one_to_four_arrow} {one_to_four_diff} %', (928,385), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[47], f'{four_to_eight} %', (1326,507), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[47], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1339,475), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[47], f'{eight_to_two} %', (1710,400), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[47], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1715,365), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    
    
    
    ####### PLAZA SAN PEDRO NOLASCO
    
    data = get_report_data('plaza_san_pedro_nolasco', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors_zone = data[0]
    unique_visitors_zone_diff = data[1]
    unique_visitors_zone_color, unique_visitors_zone_arrow = get_color_arrow(unique_visitors_zone_diff)

    # visitas unicos por mes y mes anterior
    unique_visits_zone = data[2]
    unique_visits_zone_diff = data[3]
    unique_visits_zone_color, unique_visits_zone_arrow = get_color_arrow(unique_visits_zone_diff)

    # ratio por mes y mes anterior
    ratio_zone = data[4]
    ratio_zone_diff = data[5]
    ratio_zone_color, ratio_zone_arrow = get_color_arrow(ratio_zone_diff)

    # tiempo medio por mes y mes anterior
    avg_time_zone = data[6]
    avg_time_zone_diff =  data[7]
    avg_time_zone_color, avg_time_zone_arrow = get_color_arrow(avg_time_zone_diff)


    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data[8]
    two_to_nine_diff = data[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data[9]
    nine_to_one_diff = data[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data[10]
    one_to_four_diff = data[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data[11]
    four_to_eight_diff = data[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data[12]
    eight_to_two_diff = data[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)
    
    
    # pagina 48   (portada plaza san pedro)
    report.add_text_to_page(original.pages[48], '', (220,970))
    report.merge()


    # pagina 49   (plaza san pedro - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[49], f'{unique_visitors_zone}', (380,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[49], f'{unique_visitors_zone_arrow} {unique_visitors_zone_diff} %', (425,390), fontsize=24, RGB=unique_visitors_zone_color)
    report.add_text_to_page(original.pages[49], f'{unique_visits_zone}', (1375,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[49], f'{unique_visits_zone_arrow} {unique_visits_zone_diff} %', (1400,390), fontsize=24, RGB=unique_visits_zone_color)
    report.merge()


    # pagina 50   (plaza san pedro - ratio)
    report.add_text_to_page(original.pages[50], f'{ratio_zone}', (1020,365), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[50], f'{ratio_zone_arrow} {ratio_zone_diff} %', (930,255), fontsize=28, RGB=ratio_zone_color)
    report.merge()


    # pagina 51   (plaza san pedro - tiempo medio)
    report.add_text_to_page(original.pages[51], f'{avg_time_zone}', (840,345), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[51], f'{avg_time_zone_arrow} {avg_time_zone_diff} %', (905,250), fontsize=28, RGB=avg_time_zone_color)
    report.merge()



    # pagina 52   (plaza san pedro - escalera)
    report.add_text_to_page(original.pages[52], f'{two_to_nine} %', (163,315), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[52], f'{two_to_nine_arrow} {two_to_nine_diff} %', (173,280), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[52], f'{nine_to_one} %', (519,555), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[52], f'{nine_to_one_arrow} {nine_to_one_diff} %', (524,520), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[52], f'{one_to_four} %', (925,420), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[52], f'{one_to_four_arrow} {one_to_four_diff} %', (937,385), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[52], f'{four_to_eight} %', (1311,497), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[52], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1324,465), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[52], f'{eight_to_two} %', (1700,458), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[52], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1705,425), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    
    
    ####### PLAZA JUSTICIA
    
    data = get_report_data('plaza_justicia', DATA_MES, DATA_DIA, DATA_HORA)
    
    # visitantes unicos por mes y mes anterior
    unique_visitors_zone = data[0]
    unique_visitors_zone_diff = data[1]
    unique_visitors_zone_color, unique_visitors_zone_arrow = get_color_arrow(unique_visitors_zone_diff)

    # visitas unicos por mes y mes anterior
    unique_visits_zone = data[2]
    unique_visits_zone_diff = data[3]
    unique_visits_zone_color, unique_visits_zone_arrow = get_color_arrow(unique_visits_zone_diff)

    # ratio por mes y mes anterior
    ratio_zone = data[4]
    ratio_zone_diff = data[5]
    ratio_zone_color, ratio_zone_arrow = get_color_arrow(ratio_zone_diff)

    # tiempo medio por mes y mes anterior
    avg_time_zone = data[6]
    avg_time_zone_diff =  data[7]
    avg_time_zone_color, avg_time_zone_arrow = get_color_arrow(avg_time_zone_diff)


    # Franjas horarias por mes 
    # 02:00 - 09:00
    two_to_nine = data[8]
    two_to_nine_diff = data[13]
    two_to_nine_color, two_to_nine_arrow = get_color_arrow(two_to_nine_diff)

    # 09:00 - 13:00
    nine_to_one = data[9]
    nine_to_one_diff = data[14]
    nine_to_one_color, nine_to_one_arrow = get_color_arrow(nine_to_one_diff)

    # 13:00 - 16:00
    one_to_four = data[10]
    one_to_four_diff = data[15]
    one_to_four_color, one_to_four_arrow = get_color_arrow(one_to_four_diff)

    # 16:00 - 20:00
    four_to_eight = data[11]
    four_to_eight_diff = data[16]
    four_to_eight_color, four_to_eight_arrow = get_color_arrow(four_to_eight_diff)

    # 20:00 - 02:00
    eight_to_two = data[12]
    eight_to_two_diff = data[17]
    eight_to_two_color, eight_to_two_arrow = get_color_arrow(eight_to_two_diff)
    
    
    
    # pagina 53   (portada plaza justicia)
    report.add_text_to_page(original.pages[53], '', (220,970))
    report.merge()


    # pagina 54   (plaza justicia - usuarios unicos vs visitas)
    report.add_text_to_page(original.pages[54], f'{unique_visitors_zone}', (380,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[54], f'{unique_visitors_zone_arrow} {unique_visitors_zone_diff} %', (425,390), fontsize=24, RGB=unique_visitors_zone_color)
    report.add_text_to_page(original.pages[54], f'{unique_visits_zone}', (1375,450), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[54], f'{unique_visits_zone_arrow} {unique_visits_zone_diff} %', (1400,390), fontsize=24, RGB=unique_visits_zone_color)
    report.merge()


    # pagina 55   (plaza justicia - ratio)
    report.add_text_to_page(original.pages[55], f'{ratio_zone}', (1020,365), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[55], f'{ratio_zone_arrow} {ratio_zone_diff} %', (930,255), fontsize=28, RGB=ratio_zone_color)
    report.merge()


    # pagina 56   (plaza justicia - tiempo medio)
    report.add_text_to_page(original.pages[56], f'{avg_time_zone}', (840,345), fontsize=50, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[56], f'{avg_time_zone_arrow} {avg_time_zone_diff} %', (905,250), fontsize=28, RGB=avg_time_zone_color)
    report.merge()



    # pagina 57   (plaza justicia - escalera)
    report.add_text_to_page(original.pages[57], f'{two_to_nine} %', (163,315), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[57], f'{two_to_nine_arrow} {two_to_nine_diff} %', (173,280), fontsize=20, RGB=two_to_nine_color)
    report.add_text_to_page(original.pages[57], f'{nine_to_one} %', (519,535), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[57], f'{nine_to_one_arrow} {nine_to_one_diff} %', (524,500), fontsize=20, RGB=nine_to_one_color)
    report.add_text_to_page(original.pages[57], f'{one_to_four} %', (915,405), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[57], f'{one_to_four_arrow} {one_to_four_diff} %', (927,370), fontsize=20, RGB=one_to_four_color)
    report.add_text_to_page(original.pages[57], f'{four_to_eight} %', (1300,487), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[57], f'{four_to_eight_arrow} {four_to_eight_diff} %', (1313,455), fontsize=20, RGB=four_to_eight_color)
    report.add_text_to_page(original.pages[57], f'{eight_to_two} %', (1715,478), fontsize=32, RGB=[255, 255, 255])
    report.add_text_to_page(original.pages[57], f'{eight_to_two_arrow} {eight_to_two_diff} %', (1720,445), fontsize=20, RGB=eight_to_two_color)
    report.merge()
    
    
    # pagina 58  (portada)
    report.add_text_to_page(original.pages[58], f'{month} {year}', (890,530))
    report.merge()



    ### GUARDAR REPORTE 
    report.generate(PATH + f'/../reports/casco_historico_zaragoza_{month}_{year}.pdf')
