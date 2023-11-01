from tools.create_arima_predictions import arima_model
from tools.heatmap_creation import create_maps
from tools.extract_data_csv import extract_data



if __name__ == '__main__':
    extract_data()
    create_maps()
    arima_model()
