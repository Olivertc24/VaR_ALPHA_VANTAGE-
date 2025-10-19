# core/analysis.py
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

# --- IMPORTACIONES ---
from statsmodels.tsa.seasonal import seasonal_decompose
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly # <--- MODIFICADO
from plotly.subplots import make_subplots
import plotly.graph_objects as go
# --- FIN IMPORTACIONES ---

# ... (El resto de tus funciones: add_moving_averages, get_descriptive_stats, etc. quedan igual) ...
# ... (Asegúrate de copiar también las funciones add_bollinger_bands y find_support_resistance) ...

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
    stats_formatted = {key: f"{value:.6f}" for key, value in stats.items()}
    return stats_formatted

def find_support_resistance(df, prominence=1):
    """Encuentra niveles de soporte y resistencia usando picos y valles."""
    lows = df['low']
    highs = df['high']
    
    support_indices, _ = find_peaks(-lows, prominence=prominence)
    resistance_indices, _ = find_peaks(highs, prominence=prominence)
    
    support_levels = lows.iloc[support_indices]
    resistance_levels = highs.iloc[resistance_indices]
    
    return support_levels, resistance_levels


# --- FUNCIONES DE ANÁLISIS DE SERIES Y PROYECCIÓN (ACTUALIZADAS) ---

def get_series_decomposition(df_series):
    """
    Analiza y grafica la descomposición de la serie de tiempo (Tendencia, Estacionalidad, Residual).
    """
    series = df_series['adjusted close'].resample('D').median().fillna(method='ffill')
    periodo = 365 if len(series) > 730 else 30
    
    decomposition = seasonal_decompose(series, model='additive', period=periodo)

    fig = make_subplots(rows=4, cols=1,
                        subplot_titles=('Observado', 'Tendencia', 'Estacionalidad', 'Residual'))
    
    fig.add_trace(go.Scatter(x=decomposition.observed.index, y=decomposition.observed, mode='lines', name='Observado'), row=1, col=1)
    fig.add_trace(go.Scatter(x=decomposition.trend.index, y=decomposition.trend, mode='lines', name='Tendencia'), row=2, col=1)
    fig.add_trace(go.Scatter(x=decomposition.seasonal.index, y=decomposition.seasonal, mode='lines', name='Estacionalidad'), row=3, col=1)
    fig.add_trace(go.Scatter(x=decomposition.resid.index, y=decomposition.resid, mode='markers', name='Residual'), row=4, col=1)
    
    fig.update_layout(height=700, title_text="Descomposición de la Serie de Tiempo", showlegend=False)
    return fig


def run_prophet_forecast(df, periods=30, changepoint_scale=0.05): # <--- NUEVO ARGUMENTO
    """
    Entrena un modelo Prophet y devuelve dos gráficos de Plotly:
    1. La proyección.
    2. Los componentes del modelo.
    """
    # El índice de yfinance se llama 'Date'. Lo convertimos a 'ds'.
    df_prophet = df.reset_index().rename(columns={'Date': 'ds', 'adjusted close': 'y'})
    
    # Instanciar y entrenar el modelo
    model = Prophet(daily_seasonality=False, 
                    weekly_seasonality=True, 
                    yearly_seasonality=True,
                    changepoint_prior_scale=changepoint_scale) # <--- APLICAMOS EL ARGUMENTO
    
    # --- MEJORA: AÑADIR FERIADOS ---
    model.add_country_holidays(country_name='US')
    
    model.fit(df_prophet)

    # Crear dataframe futuro y predecir
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    # Generar el gráfico de Proyección
    fig_forecast = plot_plotly(model, forecast)
    fig_forecast.update_layout(title=f'Proyección a {periods} días con Prophet',
                               xaxis_title='Fecha', yaxis_title='Precio (Proyectado)')
    
    # --- MEJORA: GENERAR GRÁFICO DE COMPONENTES ---
    fig_components = plot_components_plotly(model, forecast)
    fig_components.update_layout(title='Componentes del Modelo Prophet')

    return fig_forecast, fig_components
