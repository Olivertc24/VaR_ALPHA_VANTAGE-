# core/analysis.py
import pandas as pd
import numpy as np
from scipy.signal import find_peaks # Para el análisis de niveles

def add_moving_averages(df, short_window=20, long_window=50):
    """Añade medias móviles simples (SMA)."""
    df['SMA_short'] = df['adjusted close'].rolling(window=short_window).mean()
    df['SMA_long'] = df['adjusted close'].rolling(window=long_window).mean()
    return df

def add_bollinger_bands(df, window=20):
    """Añade Bandas de Bollinger."""
    df['BB_middle'] = df['adjusted close'].rolling(window=window).mean()
    std_dev = df['adjusted close'].rolling(window=window).std()
    df['BB_upper'] = df['BB_middle'] + (std_dev * 2)
    df['BB_lower'] = df['BB_middle'] - (std_dev * 2)
    return df

def get_descriptive_stats(returns_series):
    """Genera un reporte estadístico avanzado."""
    # Aseguramos 252 días de trading para anualizar
    anual_factor = np.sqrt(252)
    
    stats = {
        "Media (Diaria)": returns_series.mean(),
        "Mediana": returns_series.median(),
        "Desv. Estándar (Volatilidad Diaria)": returns_series.std(),
        "Volatilidad Anualizada": returns_series.std() * anual_factor,
        "Skewness (Asimetría)": returns_series.skew(),
        "Kurtosis (Curtosis)": returns_series.kurtosis(),
        "Sharpe Ratio (Anualizado)": (returns_series.mean() / returns_series.std()) * anual_factor
    }
    # Formatear números para mejor lectura
    stats_formatted = {key: f"{value:.6f}" for key, value in stats.items()}
    return stats_formatted

def find_support_resistance(df, prominence=1):
    """
    Encuentra niveles de soporte y resistencia usando picos y valles.
    Este es el "Análisis de Nivel".
    """
    # Usamos 'low' para soporte y 'high' para resistencia
    lows = df['low']
    highs = df['high']
    
    # find_peaks necesita valores negativos para encontrar valles (mínimos)
    support_indices, _ = find_peaks(-lows, prominence=prominence)
    resistance_indices, _ = find_peaks(highs, prominence=prominence)
    
    support_levels = lows.iloc[support_indices]
    resistance_levels = highs.iloc[resistance_indices]
    
    return support_levels, resistance_levels
