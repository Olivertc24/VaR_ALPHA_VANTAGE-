# core/api_client.py
from alpha_vantage.timeseries import TimeSeries
from config.config import API_KEY
import pandas as pd

def get_daily_data(symbol):
    """
    Obtiene los datos diarios (ajustados) para un símbolo de acción.
    """
    ts = TimeSeries(key=API_KEY, output_format='pandas')
    try:
        # 'compact' devuelve 100 días, 'full' devuelve historial completo
        data, meta_data = ts.get_daily_adjusted(symbol=symbol, outputsize='full')
        # Renombramos columnas para que sean más limpias (ej. '1. open' -> 'open')
        data.columns = [col.split('. ')[-1] for col in data.columns]
        data = data.sort_index(ascending=True) # Ordenamos de más antiguo a más reciente
        return data
    except Exception as e:
        print(f"Error al obtener datos para {symbol}: {e}")
        return pd.DataFrame()
