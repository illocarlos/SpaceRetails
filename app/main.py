import time
from datetime import datetime, timedelta
import os

from flask import Flask, render_template, request, url_for, redirect, session, send_file

from tools.config_users import USERS

from tools.plots import dashboard

from tools.get_data_from_api import is_consolidated

from tools.create_pdf_reports import load_data_by_date, create_casco_historico_report, create_delicias_report

from tools.text_popup import (unique_visitors_text,
                              visits_text,
                              new_visits_text,
                              ratio_text,
                              recurrents_text,
                              avg_time_text,
                              avg_time_zone_text,
                              best_day_text,
                              best_month_day_text,
                              best_hour_text,
                              weather_text,
                              plot_hour_text,
                              plot_area_text)


PATH = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)
app.secret_key = 'spaceretail'
app.permanent_session_lifetime = timedelta(minutes=600)


USER = dict()

LOGO = 'img/zaragoza.jpeg'
USER_PICTURE = 'img/spaceretail.jpg'
LINKS = ['https://www.spaceretail.net/',
         'mailto:administracion@spaceretail.es']


@app.route('/', methods=['POST', 'GET'])
def login():

    if session.get('email') and session.get('password'):
        return redirect('/zaragoza', code=302)

    if request.method == 'POST':

        today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        email = request.form['email']
        password = request.form['password']

        USER = [e for e in USERS if e['email'] == email][0]

        time.sleep(0.1)

        try:
            db_email = USER['email']
            db_password = USER['password']
        except:
            db_email = 'none'
            db_password = 'none'

        # login
        if USER is None:
            return render_template('login.html')

        if email != db_email or password != db_password:
            error = 'Invalid Credentials. Please try again.'
            render_template('login.html', error=error)
        else:

            session['email'] = email
            session['password'] = password

            return redirect(url_for('zaragoza'))

    return render_template('login.html')


@app.route('/logout/', methods=['POST', 'GET'])
def logout():
    session.pop('email', None)
    session.pop('password', None)
    session.clear()
    return redirect(url_for('login'))


@app.route('/zaragoza/', methods=['POST', 'GET'])
def zaragoza():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('zaragoza')

    return render_template('zaragoza.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/zona_delicias/', methods=['POST', 'GET'])
def zona_delicias():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('zona_delicias')

    return render_template('zona_delicias.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/zona_casco/', methods=['POST', 'GET'])
def zona_casco():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('zona_casco')

    return render_template('zona_casco.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/mercado_delicias/', methods=['POST', 'GET'])
def mercado_delicias():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('mercado_delicias')

    return render_template('mercado_delicias.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/zona_a/', methods=['POST', 'GET'])
def zona_a():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('zona_a')

    return render_template('zona_a.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/pza_jardin/', methods=['POST', 'GET'])
def pza_jardin():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('plaza_jardin')

    return render_template('pza_jardin.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/zona_b/', methods=['POST', 'GET'])
def zona_b():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('zona_b')

    return render_template('zona_b.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/zona_c/', methods=['POST', 'GET'])
def zona_c():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('zona_c')

    return render_template('zona_c.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/pza_san_felipe/', methods=['POST', 'GET'])
def pza_san_felipe():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('plaza_san_felipe')

    return render_template('pza_san_felipe.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/zona_d/', methods=['POST', 'GET'])
def zona_d():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('zona_d')

    return render_template('zona_d.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/pza_san_pedro/', methods=['POST', 'GET'])
def pza_san_pedro():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('plaza_san_pedro_nolasco')

    return render_template('pza_san_pedro.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/zona_e/', methods=['POST', 'GET'])
def zona_e():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('zona_e')

    return render_template('zona_e.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/zona_f/', methods=['POST', 'GET'])
def zona_f():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('zona_f')

    return render_template('zona_f.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],


                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/pza_justicia/', methods=['POST', 'GET'])
def pza_justicia():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('plaza_justicia')

    return render_template('pza_justicia.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/zona_g/', methods=['POST', 'GET'])
def zona_g():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('zona_g')

    return render_template('zona_g.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/zona_h/', methods=['POST', 'GET'])
def zona_h():

    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    data = dashboard('zona_h')

    return render_template('zona_h.html',

                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           unique_visitors=data[0],
                           visits=data[1],
                           ratio=data[2],
                           recurrents=data[3],

                           avg_time=data[4],
                           temp=data[5],
                           best_day=data[6],
                           best_hour=data[7],

                           bar_plot=data[8],
                           area_plot=data[9],

                           mes=data[10],

                           new_visits=data[11],
                           avg_time_zone=data[12],

                           best_month_day=data[13],
                           best_month_day_text=best_month_day_text,

                           unique_visitors_text=unique_visitors_text,
                           visits_text=visits_text,
                           new_visits_text=new_visits_text,
                           ratio_text=ratio_text,
                           recurrents_text=recurrents_text,
                           avg_time_text=avg_time_text,
                           avg_time_zone_text=avg_time_zone_text,
                           best_day_text=best_day_text,
                           best_hour_text=best_hour_text,
                           weather_text=weather_text,
                           plot_hour_text=plot_hour_text,
                           plot_area_text=plot_area_text
                           )


@app.route('/maps/', methods=['POST', 'GET'])
def maps():
    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    fields = {'Visitas_Totales': 'visits',
              'Nuevas_Visitas': 'new_visits',
              'Visitas_Recurrentes': 'recurrents',
              'Visitas_Unicas': 'visitors_unique'}

    if request.method == 'POST':

        s_field = request.form['field']

        return render_template('maps.html',
                               user_picture=USER_PICTURE,
                               logo=LOGO,
                               links=LINKS,
                               field=s_field,
                               fields=list(fields.keys()),
                               len_fields=len(fields.keys()),
                               map_path=f'../static/maps/map_{fields[s_field]}.html'
                               )

    return render_template('maps.html',
                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,
                           field='Visitas_Totales',
                           fields=list(fields.keys()),
                           len_fields=len(fields.keys()),
                           map_path='../static/maps/map_visits.html'
                           )


@app.route('/down/', methods=['POST', 'GET'])
def down():
    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    years = [2022, 2023, 2024]

    zones = ['Casco_Historico', 'Calle_Delicias']

    if request.method == 'POST':

        s_zone = request.form['zone']
        s_month = request.form['month']
        s_year = request.form['year']

        zero = '0'
        consolidated_date = f'{s_year}-{zero+str(months.index(s_month)+1) if months.index(s_month)+1<10 else months.index(s_month)+1}-20'

        if is_consolidated(consolidated_date) == 0:
            # si NO esta consolidado...
            return render_template('down.html',
                                   user_picture=USER_PICTURE,
                                   logo=LOGO,
                                   links=LINKS,

                                   zone=s_zone,
                                   zones=zones,
                                   len_zones=len(zones),

                                   month=s_month,
                                   months=months,
                                   len_months=len(months),

                                   year=s_year,
                                   years=years,
                                   len_years=len(years),

                                   warning=f'El dato NO está consolidado para la fecha {s_month}-{s_year}  .'
                                   )

        else:
            try:
                return send_file(PATH + f'/reports/{s_zone.lower()}_zaragoza_{s_month}_{s_year}.pdf', as_attachment=True)

            except:
                try:
                    # load data
                    DATA_MES, DATA_DIA, DATA_HORA, DATA_FLOW, DATA_RET, DATA_RANGE = load_data_by_date(
                        s_month, s_year)

                    # create pdf
                    create_delicias_report(
                        s_month, s_year, DATA_MES, DATA_DIA, DATA_HORA, DATA_FLOW, DATA_RET)
                    create_casco_historico_report(
                        s_month, s_year, DATA_MES, DATA_DIA, DATA_HORA, DATA_FLOW, DATA_RET)

                    # remove csv files
                    files_path = PATH + f'/reports/data/'
                    files_csv = os.listdir(files_path)
                    [os.remove(files_path + e) for e in files_csv]

                    return send_file(PATH + f'/reports/{s_zone.lower()}_zaragoza_{s_month}_{s_year}.pdf', as_attachment=True)
                except:
                    return render_template('down.html',
                                           user_picture=USER_PICTURE,
                                           logo=LOGO,
                                           links=LINKS,

                                           zone=s_zone,
                                           zones=zones,
                                           len_zones=len(zones),

                                           month=s_month,
                                           months=months,
                                           len_months=len(months),

                                           year=s_year,
                                           years=years,
                                           len_years=len(years),

                                           warning=f'No existe informe de {s_zone.replace("_", " ")} para la fecha {s_month}-{s_year}  .'
                                           )

    return render_template('down.html',
                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,

                           zone='Casco_Historico',
                           zones=zones,
                           len_zones=len(zones),

                           month=months[datetime.today().month - 2],
                           months=months,
                           len_months=len(months),

                           year=2023,
                           years=years,
                           len_years=len(years),

                           warning=''
                           )


@app.route('/about/', methods=['POST', 'GET'])
def about():
    global USER_PICTURE, LOGO, LINKS

    if session.get('email') is None or session.get('password') is None:
        return redirect('/', code=302)

    return render_template('about.html',
                           user_picture=USER_PICTURE,
                           logo=LOGO,
                           links=LINKS,
                           )


if __name__ == '__main__':
    app.run(debug=True, port=5010)
