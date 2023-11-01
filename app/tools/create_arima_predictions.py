import pandas as pd

from tools.tools import Logger

from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import mean_absolute_error as mae

from statsmodels.tsa.arima.model import ARIMA

from datetime import date, timedelta

from hyperopt import fmin, hp, tpe, Trials, STATUS_OK

import os

import warnings
warnings.filterwarnings('ignore')

PATH = os.path.dirname(os.path.abspath(__file__))


# create logger
logger = Logger('SpaceRetail Log').logger
logger.info('Starting...')


# aprioris
space={'p': hp.quniform('p', 1, 15, 1),  # distribucion uniforme discreta
    
       'd': hp.quniform('d', 1, 15, 1),  
        
       'q': hp.quniform('q', 1, 15, 1),
       }



def arima_model():

    global space, PATH
 
    result = pd.DataFrame()
    stats_train = pd.DataFrame()
    
    N = 8
    
    columns = ['zone', 'date',  
               'visits', 'new_visits', 'recurrents', 'visitors_unique']
        
    today = date.today()     #date(2023, 8, 1)

    data = pd.read_csv(PATH + '/../data/raw/raw_data_daily.csv', usecols=columns)

    data = data[(data['date'] > str(today - timedelta(days=90))) & (data['date'] <= str(today))]
    
    zones = data.zone.unique().tolist()

    logger.info(zones)
    logger.info(len(zones))
    
    for zone in zones:
        
        df = data[data.zone==zone].reset_index(drop=True)
            
        df = df.sort_values(by='date').reset_index(drop=True)
        
        stats_train_tmp_df = pd.DataFrame()
        tmp_df = pd.DataFrame()
        
        for c in columns[2:]:
            
            media = df[c][-N:].mean()
            media2 = df[c][:-N].mean()

            df[c] = df[c].apply(lambda x: x if x>0 else df[c].mean())
            
            logger.info(f'{zone.upper()}  .....  {c.upper()}  ..... Avg Train:  {round(media, 2)}  ...... Avg Test:  {round(media2, 2)}')
            
            train, test = df[c][:-N], df[c][-N:]

            def objetivo(space):
    
                modelo = ARIMA(train, order=(space['p'], space['d'], space['q']))

                modelo.initialize_approximate_diffuse()

                trained = modelo.fit()

                pred = trained.predict(train.shape[0], df.shape[0]-1)

                pred = pred.fillna(test.mean())

                loss=mse(test, pred, squared=False)

                return {'loss': loss, 'status': STATUS_OK}
            
            
            best = fmin(fn=objetivo,
                        space=space,
                        algo=tpe.suggest,
                        max_evals=500,
                        trials=Trials())
            

            logger.info(f'Best p,d,q parameters: {best}')

            
            # prediccion para calculo error medio
            modelo=ARIMA(train, order=(best['p'], best['d'], best['q']))
            
            modelo.initialize_approximate_diffuse()

            trained = modelo.fit()
            
            error_test_pred=trained.predict(train.shape[0], df.shape[0]-1).fillna(test.mean())
            
            mae_error = mae(test, error_test_pred)  
            rmse_error = mse(test, error_test_pred, squared=False)
            
            stats_train_tmp_df[c+'_pred'] = error_test_pred
            stats_train_tmp_df[c+'_truth'] = test
            stats_train_tmp_df[c+'_error'] = abs(error_test_pred-test)/test*100
            stats_train_tmp_df['zone'] = zone
            stats_train_tmp_df['date'] = df.iloc[test.index].date
            
            
            logger.info(
                        f''':::

                            + MAE: {round(mae_error, 2)} 
                            + RMSE: {round(rmse_error, 2)}  
                            + AVG_ABS_%ERROR: {round(stats_train_tmp_df[c+'_error'].mean(), 2)} 
                            + MEDIAN_ABS_%ERROR: {round(stats_train_tmp_df[c+'_error'].median(), 2)} 
                            + %ERROR_MAE: {round(mae_error/media*100, 2)} 
                            + %ERROR_RMSE: {round(rmse_error/media*100, 2)}
                            '''
                            )
            
            logger.info('next...')
            
            
            
            # prediccion buena para app
            modelo=ARIMA(df[c], order=(best['p'], best['d'], best['q']))
            
            modelo.initialize_approximate_diffuse()

            trained = modelo.fit()

            pred=trained.predict(df.shape[0], df.shape[0]+7).fillna(test.mean())
                        
            tmp_df[c] = abs(pred)
            tmp_df['zone'] = zone
            tmp_df['date'] = [pd.DatetimeIndex(df.iloc[-1:].date) + pd.DateOffset(i) for i in range(1, 9)]
            tmp_df.date = tmp_df.date.apply(lambda x: x[0])
        
        logger.info(stats_train_tmp_df.describe().T)

        stats_train = pd.concat([stats_train, stats_train_tmp_df])
        result = pd.concat([result, tmp_df])
     
    
    stats_train.to_csv(PATH + '/../data/raw/stats_train.csv')
    result.to_csv(PATH + '/../data/raw/time_series_prediction.csv')

    logger.info(stats_train.describe().T)
    logger.info('Done.')

