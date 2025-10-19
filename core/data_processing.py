# core/data_processing.py
import pandas as pd
import numpy as np  # Importamos numpy

def calculate_returns(df):
    """Calcula los rendimientos diarios y logarítmicos."""
    df_processed = df.copy()
    
    # Usamos 'adjusted close' para el análisis
    df_processed['simple_return'] = df_processed['adjusted close'].pct_change()
    
    # Usamos np.log() para el rendimiento logarítmico
    df_processed['log_return'] = np.log(df_processed['adjusted close'] / df_processed['adjusted close'].shift(1))
    
    # Eliminamos el primer NaN generado por .pct_change() y .shift()
    return df_processed.dropna() 
