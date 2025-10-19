# core/data_processing.py
import pandas as pd

def calculate_returns(df):
    """Calcula los rendimientos diarios y logarítmicos."""
    df_processed = df.copy()
    # Usamos 'adjusted close' para el análisis
    df_processed['simple_return'] = df_processed['adjusted close'].pct_change()
    df_processed['log_return'] = pd.np.log(df_processed['adjusted close'] / df_processed['adjusted close'].shift(1))
    return df_processed.dropna()
