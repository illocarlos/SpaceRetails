
from flask import Markup

unique_visitors_text = Markup('''Visitantes Unicos.  Número de visitantes unicos en la zona.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))


visits_text = Markup('''Visitas Totales.  Número de visitas totales en la zona.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))


new_visits_text = Markup('''Nuevas Visitas.  Número de visitas nuevas en la zona.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))


ratio_text = Markup('''Ratio.  Número de visitantes unicos / Número de visitas totales.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))


recurrents_text = Markup('''Visitantes Recurrentes.  Número de visitantes recurrentes en la zona.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))


avg_time_text = Markup('''Tiempo Medio.  Tiempo que los visitantes pasan de media en la zona.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))


avg_time_zone_text = Markup('''Tiempo Medio Zone.  Tiempo que los visitantes pasan de media en la zona.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))


best_day_text = Markup('''Mejor Día.  Día de la semana con más visitas de media.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))


best_month_day_text = Markup('''Mejor Día Mes.  Día del con más visitas de manera absoluta.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))


best_hour_text = Markup('''Mejor Hora.  Hora del día con más visitas de media.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))


weather_text = Markup('''Clima.  Clima que maximiza las visitas.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))


plot_hour_text = Markup('''Visitas Por Hora. Media de las visitas en cada hora.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))


plot_area_text = Markup('''Histórico.'''.replace('  ', '&#10;').replace(' ', '&nbsp;'))
