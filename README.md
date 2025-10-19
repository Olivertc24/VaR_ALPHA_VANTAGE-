📊 Dashboard de Análisis Financiero Avanzado
Este proyecto es un dashboard web interactivo para el análisis técnico, estadístico y de pronóstico de series de tiempo financieras. La aplicación está construida enteramente en Python, utilizando Streamlit para la interfaz, Plotly para las visualizaciones y Prophet para las proyecciones de machine learning.
Este repositorio es parte de mi portafolio profesional como Científico de Datos y Actuario.
[¡IMPORTANTE! Reemplaza esta línea con una captura de pantalla o un GIF de tu dashboard en acción. Esta es la parte más importante para tu portafolio.]
![Demo del Dashboard](URL_DEL_GIF_O_SCREENSHOT.png)
🚀 Características Principales
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
🛠️ Stack Tecnológico
• Lenguaje: Python
• Dashboard: Streamlit
• Extracción de Datos: yfinance
• Manipulación de Datos: pandas y numpy
• Visualización: plotly
• Análisis Estadístico: statsmodels
• Modelo de Proyección: prophet
• Análisis de Picos: scipy
