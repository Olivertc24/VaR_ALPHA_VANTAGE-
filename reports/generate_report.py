# reports/generate_report.py

import sys
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- INICIO DE LA SOLUCIÓN (sys.path) ---
# Añade el directorio raíz del proyecto al 'path' de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- FIN DE LA SOLUCIÓN ---


# --- Importaciones de nuestros módulos CORE ---
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

def generate_html_report(symbol, forecast_days=30, prominence=5):
    """
    Función principal que genera un reporte HTML completo para un símbolo dado.
    """
    print(f"Iniciando generación de reporte para {symbol}...")
    
    # 1. Cargar y Procesar Datos
    print("Paso 1/5: Obteniendo datos...")
    data_raw = get_daily_data(symbol)
    if data_raw.empty:
        print(f"Error: No se pudieron obtener datos para {symbol}. Abortando.")
        return

    # Quitar 'tz' (igual que en el dashboard)
    data_raw.index = data_raw.index.tz_localize(None)
    data_returns = calculate_returns(data_raw)
    
    min_date = data_raw.index.min().date()
    max_date = data_raw.index.max().date()
    print(f"Datos cargados. Rango: {min_date} a {max_date}")

    # 2. Análisis Estadístico y Técnico
    print("Paso 2/5: Ejecutando análisis estadístico y técnico...")
    stats = get_descriptive_stats(data_returns['log_return'])
    
    data_plot = data_raw.copy()
    data_plot = add_moving_averages(data_plot)
    data_plot = add_bollinger_bands(data_plot)
    supports, resistances = find_support_resistance(data_plot, prominence=prominence)
    
    # 3. Generar Gráficos (Técnico e Histograma)
    print("Paso 3/5: Generando gráficos (Técnico, Histograma)...")
    
    # Gráfico 1: Técnico (copiado de app.py)
    fig_tecnico = go.Figure()
    fig_tecnico.add_trace(go.Candlestick(x=data_plot.index,
                    open=data_plot['open'], high=data_plot['high'],
                    low=data_plot['low'], close=data_plot['adjusted close'],
                    name='Precio'))
    fig_tecnico.add_trace(go.Scatter(x=data_plot.index, y=data_plot['SMA_short'], mode='lines', name='SMA 20', line=dict(color='orange', width=1.5)))
    fig_tecnico.add_trace(go.Scatter(x=data_plot.index, y=data_plot['SMA_long'], mode='lines', name='SMA 50', line=dict(color='purple', width=1.5)))
    fig_tecnico.add_trace(go.Scatter(x=data_plot.index, y=data_plot['BB_upper'], mode='lines', name='BB Upper', line=dict(color='gray', dash='dash', width=1)))
    fig_tecnico.add_trace(go.Scatter(x=data_plot.index, y=data_plot['BB_lower'], mode='lines', name='BB Lower', line=dict(color='gray', dash='dash', width=1),
                             fill='tonexty', fillcolor='rgba(128,128,128,0.1)'))
    for level in supports.unique():
        fig_tecnico.add_hline(y=level, line_dash="dot", line_color="green", annotation_text=f"Soporte {level:.2f}")
    for level in resistances.unique():
        fig_tecnico.add_hline(y=level, line_dash="dot", line_color="red", annotation_text=f"Resistencia {level:.2f}")
    fig_tecnico.update_layout(
        title=f"Análisis Técnico: {symbol}",
        xaxis_rangeslider_visible=False, 
        height=600, 
        yaxis_title="Precio (USD)"
    )

    # Gráfico 2: Histograma (copiado de app.py)
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=data_returns['log_return'], nbinsx=100, name='Frecuencia', marker_color='blue'))
    fig_hist.update_layout(title="Distribución de Rendimientos Logarítmicos", xaxis_title="Rendimiento Log", yaxis_title="Frecuencia")

    # 4. Análisis de Series y Proyección (Prophet)
    print("Paso 4/5: Ejecutando análisis de series y proyección (Prophet)...")
    fig_decomp = get_series_decomposition(data_raw)
    fig_forecast = run_prophet_forecast(data_raw, periods=forecast_days)
    print("Análisis completado.")

    # 5. Ensamblar Reporte HTML
    print("Paso 5/5: Ensamblando reporte HTML...")
    # El reporte se guardará dentro de la misma carpeta 'reports/'
    filename = f"reporte_financiero_{symbol}_{datetime.now().strftime('%Y%m%d')}.html"
    report_path = os.path.join(current_dir, filename)

    with open(report_path, 'w', encoding='utf-8') as f:
        # Escribir el encabezado del HTML
        f.write(f"<html><head><title>Reporte {symbol}</title>")
        # Estilos CSS simples
        f.write("""
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px; background-color: #f9f9f9; }
            h1, h2 { color: #1e1e1e; border-bottom: 2px solid #ddd; padding-bottom: 5px; }
            .container { max-width: 1000px; margin: auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .stat-box { background-color: #f0f0f0; border: 1px solid #ddd; border-radius: 5px; padding: 15px; }
            .stat-box b { color: #333; display: block; margin-bottom: 5px; font-size: 0.9em; }
            .stat-box span { color: #000; font-size: 1.1em; font-weight: 600; }
        </style>
        """)
        # Importante: Cargar la librería Plotly.js desde CDN
        f.write("<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>")
        f.write("</head><body><div class='container'>")
        
        f.write(f"<h1>Reporte de Análisis Financiero: {symbol}</h1>")
        f.write(f"<p>Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        f.write(f"<p>Rango de datos analizado: {min_date} a {max_date}</p>")

        # Sección de Estadísticas
        f.write("<h2>Estadísticas Clave (Rendimientos Logarítmicos)</h2>")
        f.write("<div class='stats-grid'>")
        for key, value in stats.items():
            f.write(f"<div class='stat-box'><b>{key}</b><span>{value}</span></div>")
        f.write("</div>")

        # Gráficos (convertidos a HTML)
        f.write(f"<h2>{fig_tecnico.layout.title.text}</h2>")
        f.write(fig_tecnico.to_html(full_html=False, include_plotlyjs=False, div_id='fig-tecnico'))

        f.write(f"<h2>{fig_hist.layout.title.text}</h2>")
        f.write(fig_hist.to_html(full_html=False, include_plotlyjs=False, div_id='fig-hist'))
        
        f.write("<h2>Análisis de Serie de Tiempo y Proyección</h2>")

        f.write(f"<h3>{fig_decomp.layout.title.text}</h3>")
        f.write(fig_decomp.to_html(full_html=False, include_plotlyjs=False, div_id='fig-decomp'))

        f.write(f"<h3>{fig_forecast.layout.title.text}</h3>")
        f.write(fig_forecast.to_html(full_html=False, include_plotlyjs=False, div_id='fig-forecast'))

        # Cerrar HTML
        f.write("</div></body></html>")
    
    print(f"\n¡Reporte generado! 🚀")
    print(f"Archivo guardado en: {report_path}")

# --- Esto permite ejecutar el script desde la línea de comandos ---
if __name__ == "__main__":
    # Tomar el símbolo de la línea de comandos
    if len(sys.argv) > 1:
        symbol_input = sys.argv[1].upper()
    else:
        symbol_input = "MSFT" # Usar MSFT como default si no se provee
    
    generate_html_report(symbol_input)
