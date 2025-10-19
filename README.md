# 📊 Dashboard de Análisis Financiero Avanzado

Este proyecto es un dashboard web interactivo para el análisis técnico, estadístico y de pronóstico de series de tiempo financieras. La aplicación está construida enteramente en Python, utilizando Streamlit para la interfaz, Plotly para las visualizaciones y Prophet para las proyecciones de machine learning.

# 🚀 Características Principales

El dashboard permite a los usuarios analizar cualquier ticker válido de Yahoo Finance y ofrece:

• Visualización Interactiva: Gráfico de velas (candlestick) con zoom y panning (construido con Plotly).

• Filtros Dinámicos: Selección de ticker (símbolo de la acción) y filtrado por rango de fechas.

• Indicadores Técnicos: Superposición de Medias Móviles Simples (SMA 20/50) y Bandas de Bollinger (BB 20).

• Análisis de Niveles: Detección y visualización automática de líneas de Soporte y Resistencia basadas en picos y valles locales.

• Análisis Estadístico: Cálculo de métricas clave sobre los rendimientos logarítmicos, incluyendo:

• Volatilidad Anualizada

• Sharpe Ratio (Anualizado)

• Asimetría (Skewness)

• Curtosis (Kurtosis)

• Análisis de Serie de Tiempo: Descomposición de la serie de precios en sus componentes de Tendencia, Estacionalidad y Residuales (usando statsmodels).

• Pronóstico (Machine Learning) 🤖: Proyección de precios a N días hacia el futuro utilizando Prophet (de Meta), mostrando el pronóstico (yhat) y los intervalos de confianza (yhat_lower, yhat_upper).

• Generación de Informes: Un script separado permite generar un informe HTML interactivo completo para un ticker específico desde la línea de comandos.

# 🛠️ Stack Tecnológico

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/yfinance-008080?style=for-the-badge" alt="yfinance" />
  <img src="https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="pandas" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/statsmodels-D62728?style=for-the-badge" alt="statsmodels" />
  <img src="https://img.shields.io/badge/Prophet-0068FF?style=for-the-badge&logo=meta&logoColor=white" alt="Prophet" />
  <img src="https://img.shields.io/badge/SciPy-88C149?style=for-the-badge&logo=scipy&logoColor=white" alt="SciPy" />
</p>
