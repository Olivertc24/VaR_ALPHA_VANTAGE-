# core/api_client.py
import yfinance as yf
import pandas as pd

def get_daily_data(symbol):
    """
    Obtiene los datos diarios (ajustados) para un símbolo de acción usando yfinance.
    Esta versión es robusta y maneja el caso de que 'Adj Close' no esté presente.
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # period="max" obtiene todo el historial
        # auto_adjust=False para que nos dé 'Adj Close' por separado
        data = ticker.history(period="max", auto_adjust=False)
        
        if data.empty:
            print(f"No se encontraron datos para {symbol} usando yfinance.")
            return pd.DataFrame()

        # Renombramos las columnas estándar
        data.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Adj Close': 'adjusted close', # Intentamos renombrar 'Adj Close'
            'Volume': 'volume'
        }, inplace=True)
        
        
        # --- INICIO DE LA CORRECCIÓN ---
        # Verificamos si 'adjusted close' existe después del renombramiento.
        # Si no existe (porque yfinance no envió 'Adj Close'), la creamos
        # usando la columna 'close' como fallback.
        if 'adjusted close' not in data.columns and 'close' in data.columns:
            print(f"Advertencia: 'Adj Close' no encontrado para {symbol}. Usando 'close' como 'adjusted close'.")
            data['adjusted close'] = data['close']
        # --- FIN DE LA CORRECCIÓN ---
            

        # El índice (Date) ya es un datetime, así que no hay que convertirlo
        
        # Filtramos para devolver solo las columnas que usamos
        cols_necesarias = ['open', 'high', 'low', 'close', 'adjusted close', 'volume']
        
        # Devolvemos solo las columnas que existen en el dataframe
        cols_a_devolver = [col for col in cols_necesarias if col in data.columns]
        
        return data[cols_a_devolver]

    except Exception as e:
        print(f"Error al obtener datos para {symbol} con yfinance: {e}")
        return pd.DataFrame()
