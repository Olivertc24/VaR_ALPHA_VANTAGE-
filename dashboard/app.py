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
    find_support_resistance,
    get_series_decomposition,
    run_prophet_forecast
)

# --- Configuración de la página de Streamlit ---
st.set_page_config(layout="wide", page_title="Dashboard Financiero")
st.title("Dashboard de Análisis Financiero")


# --- Barra lateral de controles ---
st.sidebar.header("Controles")
symbol = st.sidebar.text_input("Símbolo (Ticker)", value="MSFT").upper()
st.sidebar.subheader("Indicadores Técnicos")
show_ma = st.sidebar.checkbox("Mostrar Medias Móviles (SMA 20/50)", value=True)
show_bb = st.sidebar.checkbox("Mostrar Bandas de Bollinger (BB 20)", value=True)
show_levels = st.sidebar.checkbox("Mostrar Soportes y Resistencias", value=True)
level_prominence = st.sidebar.slider("Prominencia de Niveles", min_value=1, max_value=20, value=5,
                                     help="Ajusta la sensibilidad para detectar picos y valles.")

# --- FILTRO DE FECHAS ---
st.sidebar.subheader("Filtro de Fechas")
min_date_default = datetime.now().date()
max_date_default = datetime.now().date()

# --- CONTROLES DE PROYECCIÓN (CON MEJORAS) ---
st.sidebar.subheader("Proyecciones (con Prophet)")
show_forecast = st.sidebar.checkbox("Mostrar Proyección y Descomposición", value=False)
forecast_days = st.sidebar.number_input("Días a Proyectar", min_value=7, max_value=365, value=30)

changepoint_scale = st.sidebar.slider(
    "Sensibilidad de Tendencia (Changepoint)", 
    min_value=0.01, 
    max_value=1.0, 
    value=0.05, 
    step=0.01,
    help="Valores altos (ej. 0.5) hacen la tendencia más flexible; "
         "valores bajos (ej. 0.05) la hacen más rígida."
)


# --- Carga y Procesamiento de Datos ---
@st.cache_data(ttl=3600)
def load_data(ticker):
    data = get_daily_data(ticker)
    if data.empty:
        return pd.DataFrame(), pd.DataFrame() 
    data_processed = calculate_returns(data)
    return data, data_processed

data_raw, data_returns = load_data(symbol)


# --- Corrección de Zona Horaria (tz-naive) ---
if not data_raw.empty:
    data_raw.index = data_raw.index.tz_localize(None)
    min_date_default = data_raw.index.min().date()
    max_date_default = data_raw.index.max().date()
if not data_returns.empty:
    data_returns.index = data_returns.index.tz_localize(None)


# --- Renderizado del Dashboard ---
if data_raw.empty:
    st.error(f"No se pudieron obtener datos para {symbol}. Verifica el símbolo.")
else:
    
    # --- Actualización del Filtro de Fechas ---
    col1, col2 = st.sidebar.columns(2)
    with col1:
        default_start = max(min_date_default, datetime(max_date_default.year - 1, max_date_default.month, max_date_default.day).date())
        start_date = st.date_input("Fecha Inicio", value=default_start, min_value=min_date_default, max_value=max_date_default)
    with col2:
        end_date = st.date_input("Fecha Fin", value=max_date_default, min_value=min_date_default, max_value=max_date_default)

    if start_date > end_date:
        st.sidebar.error("La fecha de inicio no puede ser posterior a la fecha de fin.")
        st.stop() 

    data_raw_filtered = data_raw.loc[start_date:end_date]
    data_returns_filtered = data_returns.loc[start_date:end_date]
    

    # --- INICIO DE LA CORRECCIÓN (BLOQUE REINSERTADO) ---
    # Aplicamos los análisis seleccionados al dataframe FILTRADO
    # Esta variable 'data_plot' es la que faltaba
    data_plot = data_raw_filtered.copy()
    if show_ma:
        data_plot = add_moving_averages(data_plot)
    if show_bb:
        data_plot = add_bollinger_bands(data_plot)
    # --- FIN DE LA CORRECCIÓN ---


    # --- 1. Sección de Gráficos ---
    st.header(f"Análisis Técnico: {symbol} ({start_date} a {end_date})")
    
    fig = go.Figure()
    
    # Esta línea (la 118) ahora funcionará
    fig.add_trace(go.Candlestick(x=data_plot.index,
                    open=data_plot['open'], high=data_plot['high'],
                    low=data_plot['low'], close=data_plot['adjusted close'],
                    name='Precio'))
    if show_ma:
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['SMA_short'], mode='lines', name='SMA 20', line=dict(color='orange', width=1.5)))
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['SMA_long'], mode='lines', name='SMA 50', line=dict(color='purple', width=1.5)))
    if show_bb:
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['BB_upper'], mode='lines', name='BB Upper', line=dict(color='gray', dash='dash', width=1)))
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['BB_lower'], mode='lines', name='BB Lower', line=dict(color='gray', dash='dash', width=1),
                                 fill='tonexty', fillcolor='rgba(128,128,128,0.1)'))
    if show_levels:
        supports, resistances = find_support_resistance(data_plot, prominence=level_prominence)
        for level in supports.unique():
            fig.add_hline(y=level, line_dash="dot", line_color="green", annotation_text=f"Soporte {level:.2f}", annotation_position="bottom right")
        for level in resistances.unique():
            fig.add_hline(y=level, line_dash="dot", line_color="red", annotation_text=f"Resistencia {level:.2f}", annotation_position="top right")

    fig.update_layout(xaxis_rangeslider_visible=False, height=600,
                      title=f"Gráfico de Precios e Indicadores para {symbol}",
                      yaxis_title="Precio (USD)", legend_title="Indicadores")
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
    

    # --- 4. SECCIÓN DE PROYECCIÓN (CON MEJORAS) ---
    if show_forecast:
        st.header(f"Análisis de Proyección para {symbol}")
        
        if len(data_raw_filtered) < 730:
            st.warning("Advertencia: Se recomiendan al menos 2 años de datos en el rango seleccionado "
                       "para una descomposición y proyección anual precisas. "
                       "Los resultados pueden no ser fiables.")
        
        # 4.1 Descomposición de la Serie
        with st.spinner("Analizando la serie de tiempo (descomposición)..."):
            decomp_fig = get_series_decomposition(data_raw_filtered)
            st.plotly_chart(decomp_fig, use_container_width=True)

        # 4.2 Proyección con Prophet
        with st.spinner(f"Calculando proyección a {forecast_days} días con Prophet... (Esto puede tardar)"):
            
            # Llamamos a la función actualizada
            forecast_fig, components_fig = run_prophet_forecast(
                data_raw_filtered, 
                periods=forecast_days,
                changepoint_scale=changepoint_scale
            )
            
            st.subheader(f"Proyección a {forecast_days} Días")
            st.plotly_chart(forecast_fig, use_container_width=True)
            
            st.subheader("Componentes del Modelo (Tendencia y Estacionalidad)")
            st.plotly_chart(components_fig, use_container_width=True)
