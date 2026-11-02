# Pronóstico mensual del IPAP BMC

Equipo PUJ Cali, Pontificia Universidad Javeriana Cali.
Santiago Pérez, Santiago Zambrano y Martín Bastidas.

El proyecto pronostica el Total agropecuario mensual con ETS y hasta 120 meses recientes de entrenamiento. El archivo de entrada conserva 189 observaciones oficiales de enero de 2011 a septiembre de 2026. El pronóstico final cubre octubre de 2026 a septiembre de 2027.

## Leer los resultados

El [informe técnico](Informe_tecnico_PUJ_Cali.docx) resume el trabajo. La [guía del proyecto](Guia_del_proyecto_PUJ_Cali.docx) explica la ejecución, los datos, los modelos, el código y la interpretación de cada gráfico desde cero.

También se pueden abrir directamente [los resultados](resultados/LEER_RESULTADOS.md), [las métricas](resultados/metricas_6_cortes.csv) y [el pronóstico](resultados/pronostico_12_meses.csv). No hace falta ejecutar código para leer esos archivos. Las imágenes PNG se abren con el visor habitual del computador.

## Ejecutar en macOS o Linux

Usar Python 3.12. Desde la carpeta del proyecto:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python usar_modelo.py
sh ejecutar.sh
```

La primera orden crea un entorno aislado y la segunda instala las bibliotecas. `usar_modelo.py` carga el modelo entregado. `ejecutar.sh` vuelve a entrenar, evaluar y comprobar todo. Solo la instalación necesita conexión a Internet.

## Ejecutar en Windows

Instalar Python 3.12 y abrir una terminal dentro de la carpeta:

```bat
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe usar_modelo.py
ejecutar.bat
```

La instalación y ejecución se comprobaron en macOS ARM64 con Python 3.12.14 y un entorno nuevo. Las instrucciones de Windows y Linux se incluyen para adaptación; no se ejecutaron en esos sistemas.

## Archivos principales

| Archivo | Para qué sirve |
| --- | --- |
| datos/ipap_bmc_mensual.csv | Único CSV de entrada, con mes y nivel del índice |
| datos/fuente.json | Fuente, cobertura, precisión y huellas de los datos |
| modelo_ipap.py | Lectura, ajuste, evaluación, gráficos y guardado del modelo |
| usar_modelo.py | Pronóstico con el modelo guardado, sin entrenar otra vez |
| comprobar.py | Contraste con la captura, métricas, predicciones y controles temporales |
| modelos/modelo_ets.pkl | Ajuste final entrenado con 120 meses, de octubre de 2016 a septiembre de 2026 |
| modelos/ficha_modelo.json | Configuración, entrenamiento, parámetros y entorno |
| resultados/ | Tablas, gráficos y comprobaciones |
| Proyecto_IPAP.ipynb | Cuaderno con explicaciones, código y resultados ejecutados |
| documentacion/ | Captura original de BMC e imagen de procedencia |
| experimentos/ | Código de comparación de configuraciones y tabla resumen |

Los CSV de resultados contienen salidas del programa. No son entradas adicionales. La ejecución regenera modelos y resultados, pero no modifica las observaciones oficiales.

## Cuaderno y documentos

Para ejecutar el cuaderno con el mismo entorno:

```sh
.venv/bin/python -m pip install -r requirements-cuaderno.txt
.venv/bin/python ejecutar_cuaderno.py
.venv/bin/python comprobar.py
```

La ejecución actualiza `Proyecto_IPAP.ipynb` con sus salidas y muestra el número de celdas y errores. En Windows, sustituir `.venv/bin/python` por `.venv\Scripts\python.exe`. Los documentos Word explican los resultados entregados; después de cambiar datos o métodos deben revisarse también sus cifras y figuras.

La comparación complementaria se repite con las mismas dependencias del modelo:

```sh
.venv/bin/python experimentos/comparar_variantes.py
```

Esta orden actualiza únicamente `experimentos/comparacion.csv`. Conserva todas las configuraciones comparadas y permite revisar la elección de la ventana de entrenamiento.

## Datos y evaluación

La fuente es el [tablero BMC](https://www.bolsamercantil.com.co/user/tableros), vista Niveles, Total agropecuario, capturada el 23 de octubre de 2026. Se conservaron los dos decimales visibles. No se rellenaron valores, no se mezclaron publicaciones PDF y no se reescaló el índice. La captura original está en `documentacion/captura_bmc.json` y el programa comprueba que coincida con el CSV.

En seis cortes de septiembre de 2020 a septiembre de 2025 se pronostican doce meses completos, sin recibir observaciones reales intermedias. Cada método tiene 72 objetivos y se compara con último valor, mismo mes del año anterior y deriva de doce meses. El ejemplo de 2025 comparte meses con esos bloques y no es una prueba adicional independiente.

La ventana de entrenamiento se definió durante el desarrollo sobre períodos ya examinados. La evaluación es retrospectiva. La captura puede contener revisiones y faltan todas las versiones históricas para reproducir la disponibilidad real de los datos. No se entregan intervalos calibrados ni se garantiza el error futuro. Los pronósticos están separados de los datos oficiales y se expresan en puntos del índice, no en pesos.

## Fuentes y créditos

- Bolsa Mercantil de Colombia: [tablero IPAP BMC](https://www.bolsamercantil.com.co/user/tableros) y [metodología de julio de 2022](https://www.bolsamercantil.com.co/sites/default/files/2022-08/14.%20Metodolog%C3%ADa%20IPAP.pdf).
- [statsmodels 0.14.6](https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.holtwinters.ExponentialSmoothing.html), implementación de suavizamiento exponencial utilizada.
- Se consultó como antecedente [Commodity Price Forecasting de María Sol Pera](https://github.com/msolpera/forecasting_agro). Sus bases de carne, soja y trigo y sus modelos guardados no forman parte de este proyecto. El modelo entregado se ajusta con la serie BMC y no importa código de aquel repositorio.

La [declaración de uso de IA](DECLARACION_IA.md).
