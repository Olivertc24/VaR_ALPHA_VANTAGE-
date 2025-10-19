# dashboard/app.py

import sys
import os
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# --- INICIO DE LA SOLUCIÓN (sys.path) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- FIN DE LA SOLUCIÓN ---


# --- Importaciones de nuestros módulos ---
from core.api_client import get_daily_data
from core.data_processing import calculate_returns
from core.analysis import (
    add_moving_averages, 
    add_bollinger_bands, 
    get_descriptive_stats,
    find_support_resistance
)

# --- Configuración de la página de Streamlit ---
st.set_page_config(layout="wide", page_title="Dashboard Financiero")
st.title("Dashboard de Análisis Financiero Avanzado")


# --- Barra lateral de controles ---
st.sidebar.header("Controles")
symbol = st.sidebar.text_input("Símbolo (Ticker)", value="MSFT").upper()
st.sidebar.subheader("Indicadores Técnicos")
show_ma = st.sidebar.checkbox("Mostrar Medias Móviles (SMA 20/50)", value=True)
show_bb = st.sidebar.checkbox("Mostrar Bandas de Bollinger (BB 20)", value=True)
show_levels = st.sidebar.checkbox("Mostrar Soportes y Resistencias", value=True)
level_prominence = st.sidebar.slider("Prominencia de Niveles", min_value=1, max_value=20, value=5,
                                     help="Ajusta la sensibilidad para detectar picos y valles. "
                                          "Un valor más alto detecta niveles más significativos.")


# --- Carga y Procesamiento de Datos ---
@st.cache_data(ttl=3600) # Cache por 1 hora
def load_data(ticker):
    """Carga y procesa los datos desde la API."""
    data = get_daily_data(ticker)
    if data.empty:
        return pd.DataFrame(), pd.DataFrame() 
    
    data_processed = calculate_returns(data)
    return data, data_processed

# Cargamos el historial COMPLETO
data_raw, data_returns = load_data(symbol)


# --- Corrección de Zona Horaria (tz-naive) ---
if not data_raw.empty:
    data_raw.index = data_raw.index.tz_localize(None)
if not data_returns.empty:
    data_returns.index = data_returns.index.tz_localize(None)
# --- Fin Corrección ---


# --- Renderizado del Dashboard ---
if data_raw.empty:
    st.error(f"No se pudieron obtener datos para {symbol}. Verifica el símbolo.")
else:
    
    # --- FILTRO DE FECHAS ---
    st.sidebar.subheader("Filtro de Fechas")
    
    min_date = data_raw.index.min().date()
    max_date = data_raw.index.max().date()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        # Valor default: 1 año atrás desde la fecha máxima
        default_start = max(min_date, datetime(max_date.year - 1, max_date.month, max_date.day).date())
        start_date = st.date_input("Fecha Inicio", value=default_start, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("Fecha Fin", value=max_date, min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.sidebar.error("La fecha de inicio no puede ser posterior a la fecha de fin.")
        st.stop() 

    # Aplicamos el filtro de fechas
    data_raw_filtered = data_raw.loc[start_date:end_date]
    data_returns_filtered = data_returns.loc[start_date:end_date]
    # --- FIN FILTRO DE FECHAS ---


    # Aplicamos los análisis seleccionados al dataframe FILTRADO
    data_plot = data_raw_filtered.copy()
    if show_ma:
        data_plot = add_moving_averages(data_plot)
    if show_bb:
        data_plot = add_bollinger_bands(data_plot)
    
    
    # --- 1. Sección de Gráficos ---
    st.header(f"Análisis Técnico: {symbol} ({start_date} a {end_date})")
    
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(x=data_plot.index,
                    open=data_plot['open'],
                    high=data_plot['high'],
                    low=data_plot['low'],
                    close=data_plot['adjusted close'],
                    name='Precio'))

    if show_ma:
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['SMA_short'], mode='lines', name='SMA 20', line=dict(color='orange', width=1.5)))
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['SMA_long'], mode='lines', name='SMA 50', line=dict(color='purple', width=1.5)))
    
    if show_bb:
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['BB_upper'], mode='lines', name='BB Upper', line=dict(color='gray', dash='dash', width=1)))
        # --- LÍNEA CORREGIDA ---
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['BB_lower'], mode='lines', name='BB Lower', line=dict(color='gray', dash='dash', width=1),
                                 fill='tonexty', fillcolor='rgba(128,128,128,0.1)'))

    if show_levels:
        supports, resistances = find_support_resistance(data_plot, prominence=level_prominence)
        for level in supports.unique():
            fig.add_hline(y=level, line_dash="dot", line_color="green", annotation_text=f"Soporte {level:.2f}", annotation_position="bottom right")
        for level in resistances.unique():
            fig.add_hline(y=level, line_dash="dot", line_color="red", annotation_text=f"Resistencia {level:.2f}", annotation_position="top right")

    fig.update_layout(
        xaxis_rangeslider_visible=False, 
        height=600,
        title=f"Gráfico de Precios e Indicadores para {symbol}",
        yaxis_title="Precio (USD)",
        legend_title="Indicadores"
    )
    st.plotly_chart(fig, use_container_width=True)

    
    # --- 2. Sección de Informe Estadístico ---
    st.header("Informe Estadístico (Sobre Rendimientos Logarítmicos)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Estadísticas Clave")
        stats = get_descriptive_stats(data_returns_filtered['log_return'])
        st.json(stats)
        
    with col2:
        st.subheader("Distribución de Rendimientos")
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(x=data_returns_filtered['log_return'], nbinsx=100, name='Frecuencia', marker_color='blue'))
        
        fig_hist.update_layout(title="Histograma de Rendimientos Logarítmicos", xaxis_title="Rendimiento Log", yaxis_title="Frecuencia", showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)

    
    # --- 3. Sección de Datos Crudos ---
    st.subheader(f"Últimos 10 días de datos procesados para {symbol} (en el rango)")
    st.dataframe(data_returns_filtered.tail(10))
