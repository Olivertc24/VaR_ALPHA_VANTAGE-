# dashboard/app.py
import streamlit as st
import plotly.graph_objects as go
from core.api_client import get_daily_data
from core.data_processing import calculate_returns
from core.analysis import (
    add_moving_averages, 
    add_bollinger_bands, 
    get_descriptive_stats,
    find_support_resistance
)

st.set_page_config(layout="wide")
st.title("Dashboard de Análisis Financiero Avanzado")

# --- Barra lateral de controles ---
st.sidebar.header("Controles")
symbol = st.sidebar.text_input("Símbolo (Ticker)", value="MSFT").upper()
st.sidebar.subheader("Indicadores Técnicos")
show_ma = st.sidebar.checkbox("Mostrar Medias Móviles (SMA 20/50)", value=True)
show_bb = st.sidebar.checkbox("Mostrar Bandas de Bollinger (BB 20)", value=True)
show_levels = st.sidebar.checkbox("Mostrar Soportes y Resistencias", value=True)
level_prominence = st.sidebar.slider("Prominencia de Niveles", min_value=1, max_value=20, value=5)


# --- Carga y Procesamiento de Datos ---
# Usamos cache para no llamar a la API cada vez que movemos un slider
@st.cache_data(ttl=3600) # Cache por 1 hora
def load_data(ticker):
    data = get_daily_data(ticker)
    if data.empty:
        return pd.DataFrame(), pd.DataFrame()
    data_processed = calculate_returns(data)
    return data, data_processed

data_raw, data_returns = load_data(symbol)

if data_raw.empty:
    st.error(f"No se pudieron obtener datos para {symbol}. Verifica el símbolo o la API key.")
else:
    # Aplicamos los análisis seleccionados
    data_plot = data_raw.copy()
    if show_ma:
        data_plot = add_moving_averages(data_plot)
    if show_bb:
        data_plot = add_bollinger_bands(data_plot)
    
    
    # --- Sección de Gráficos ---
    st.header(f"Gráfico de Precios de {symbol}")
    
    fig = go.Figure()
    
    # Gráfico de Velas (Candlestick)
    fig.add_trace(go.Candlestick(x=data_plot.index,
                    open=data_plot['open'],
                    high=data_plot['high'],
                    low=data_plot['low'],
                    close=data_plot['adjusted close'],
                    name='Precio'))

    # Añadir indicadores al gráfico
    if show_ma:
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['SMA_short'], mode='lines', name='SMA 20', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['SMA_long'], mode='lines', name='SMA 50', line=dict(color='purple')))
    
    if show_bb:
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['BB_upper'], mode='lines', name='BB Upper', line=dict(color='gray', dash='dash')))
        fig.add_trace(go.Scatter(x=data_plot.index, y=data_plot['BB_lower'], mode='lines', name='BB Lower', line=dict(color='gray', dash='dash'), fill='tonexty', fillcolor='rgba(128,128,128,0.1)'))

    # Añadir niveles de soporte y resistencia
    if show_levels:
        supports, resistances = find_support_resistance(data_plot, prominence=level_prominence)
        for level in supports:
            fig.add_hline(y=level, line_dash="dot", line_color="green", annotation_text=f"Soporte {level:.2f}", annotation_position="bottom right")
        for level in resistances:
            fig.add_hline(y=level, line_dash="dot", line_color="red", annotation_text=f"Resistencia {level:.2f}", annotation_position="top right")

    fig.update_layout(
        xaxis_rangeslider_visible=False, 
        height=600,
        title=f"Análisis Técnico: {symbol}",
        yaxis_title="Precio (USD)"
    )
    st.plotly_chart(fig, use_container_width=True)

    
    # --- Sección de Informe Estadístico ---
    st.header("Informe Estadístico Avanzado (Sobre Rendimientos Log)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estadísticas Descriptivas")
        stats = get_descriptive_stats(data_returns['log_return'])
        st.json(stats) # st.json() formatea diccionarios muy bien
        
    with col2:
        st.subheader("Distribución de Rendimientos")
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(x=data_returns['log_return'], nbinsx=50, name='Frecuencia'))
        fig_hist.update_layout(title="Histograma de Rendimientos Logarítmicos", xaxis_title="Rendimiento Log", yaxis_title="Frecuencia")
        st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("Datos Crudos")
    st.dataframe(data_returns.tail(10))

