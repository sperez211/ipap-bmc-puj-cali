# Pronóstico mensual del IPAP BMC a doce meses

@identidad

## Resumen

Pronosticamos el Total agropecuario mensual del IPAP BMC para los doce meses posteriores a una fecha de corte. Utilizamos ETS con tendencia amortiguada, estacionalidad anual y hasta 120 meses recientes de entrenamiento. El CSV conserva 189 observaciones oficiales. En seis cortes históricos, el modelo obtiene RMSE de {{rmse}} puntos y MAPE de {{mape}} %. El RMSE es {{mejora_ultimo}} % menor que el de repetir el último valor. La evaluación es retrospectiva y no garantiza ese desempeño en meses nuevos. El paquete incluye datos, código, evaluación y modelo entrenado.

## 1 Problema y datos

El objetivo es anticipar la trayectoria anual del índice usando la información anterior a cada corte. La proyección puede servir como referencia para analizar el mercado agropecuario y preparar escenarios. No medimos ahorros monetarios ni efectos causales, y el resultado no representa el precio particular de un producto o una finca.

Trabajamos con un dato por mes del Total agropecuario, expresado en puntos del índice. El CSV contiene las columnas fecha y valor, desde enero de 2011 hasta septiembre de 2026. Sus 189 meses son continuos, sin duplicados ni valores ausentes. El último nivel observado es 254,74. Las predicciones futuras se guardan aparte y no se incorporan a este archivo.

La fuente es el tablero BMC, vista Niveles, opción Total agropecuario, capturado el 23 de octubre de 2026. Se tomaron las celdas de Mostrar como tabla y se conservaron sus dos decimales visibles. Las fechas se expresaron como año y mes, y la coma decimal se cambió por punto para el CSV. No se modificaron los niveles, no se rellenaron meses ni se combinaron publicaciones PDF. La captura JSON y una imagen de evidencia acompañan los datos. El programa contrasta sus 189 valores y sus huellas digitales.

## 2 Modelo y evaluación

ETS estima el nivel, la tendencia y el patrón que se repite durante el año. Utilizamos tendencia aditiva amortiguada, estacionalidad aditiva de doce meses e inicialización estimada, con ExponentialSmoothing de statsmodels 0.14.6. En cada corte toma como máximo los últimos 120 meses disponibles. Si hay menos, usa toda esa historia. Esta ventana conserva hasta diez ciclos anuales y limita el peso de períodos lejanos. Los parámetros se estiman dentro de cada entrenamiento.

La entrada es únicamente la historia mensual del total. No hacen falta valores futuros de IPP, tasa de cambio, clima o componentes. Comparamos ETS con tres reglas: repetir el último nivel, repetir el mismo mes del año anterior y prolongar el cambio mensual promedio del último año, llamado deriva de doce meses. Todos reciben información hasta la misma fecha y pronostican los mismos doce objetivos.

En cada corte generamos un año completo de una sola vez. Los valores reales intermedios no actualizan las predicciones. Los seis bloques evaluados no se superponen y suman 72 meses por método, aunque los entrenamientos comparten historia.

@cortes

RMSE penaliza los fallos grandes y MAE mide el error absoluto promedio; ambos están en puntos del índice. MAPE expresa el error absoluto relativo medio, en porcentaje. Los objetivos son positivos. El RMSE conjunto utiliza los 72 errores individuales, no el promedio de seis RMSE anuales.

La ventana y la especificación se definieron durante el desarrollo sobre períodos ya examinados. Estas cifras describen una evaluación retrospectiva, no una nueva prueba independiente. Además, la historia de la captura puede contener revisiones y no reconstruye todas las versiones conocidas en cada fecha pasada.

## 3 Resultados

La comparación agrupada tiene 72 objetivos por método. ETS obtiene el menor RMSE, MAE y MAPE de los cuatro métodos sobre este conjunto. Frente al último valor, el RMSE pasa de {{rmse_ultimo}} a {{rmse}} puntos, una reducción del {{mejora_ultimo}} %. Frente a la deriva, cuyo RMSE es {{rmse_deriva}}, la reducción es del {{mejora_deriva}} %. Son comparaciones de error, no porcentajes de acierto ni garantías de superioridad futura.

@metricas

@figura error_por_corte.png|Figura 1. RMSE de los doce meses posteriores a cada corte de septiembre. Fuente: predicciones y métricas generadas por el código con la captura BMC.

El mayor error de ETS aparece en el corte {{peor_corte}}, con RMSE de {{peor_rmse}} puntos, cuando subestima el aumento posterior del índice. El error también cambia con el plazo: el RMSE es {{h1}} en el primer mes y {{h12}} en el mes doce. Cada horizonte reúne solo seis errores. La precisión del primer mes no resume la de una trayectoria anual completa.

Como diagnóstico adicional, entrenamos hasta diciembre de 2024 y pronosticamos enero a diciembre de 2025. Estos meses se superponen con los bloques anteriores y no son otra prueba independiente. En ese año, ETS obtiene RMSE {{rmse_2025}}, mientras la deriva alcanza {{rmse_deriva_2025}}. Este resultado muestra que ETS no es el mejor método en todos los períodos.

@metricas_2025

## 4 Ajuste final y pronóstico

El modelo entregado se entrenó con 120 meses, de octubre de 2016 a septiembre de 2026. El CSV conserva los 189 meses para la evaluación y la trazabilidad. Guardamos el ajuste y su ficha, lo recargamos y generamos la trayectoria de octubre de 2026 a septiembre de 2027.

@figura pronostico_12_meses.png|Figura 2. Observaciones recientes y pronóstico central. La línea vertical marca septiembre de 2026, último mes observado de la captura; el tramo discontinuo corresponde al modelo.

La estimación es {{primero_futuro}} puntos para octubre de 2026 y {{ultimo_futuro}} para septiembre de 2027. Estos números son predicciones, no observaciones oficiales. La proyección corresponde a la captura del 23 de octubre y no a una actualización del portal al 1 de noviembre. Aún no hay doce objetivos futuros completos para evaluarla y esta entrega no incluye intervalos de incertidumbre calibrados.

## 5 Reproducción y alcance

El repositorio reúne datos, captura, código, dependencias, modelo, cuaderno y salidas. modelo_ipap.py reconstruye la evaluación, el ajuste y los gráficos; comprobar.py revisa los resultados y usar_modelo.py carga el ajuste sin reentrenar. El README y la guía explican la ejecución y la lectura de las salidas.

La instalación y ejecución se comprobaron con Python 3.12.14 en macOS ARM64, en un entorno nuevo. Los controles contrastan 189 niveles con la captura, regeneran 336 predicciones, recalculan métricas y comprueban siete cortes alterando el futuro. También comparan el modelo recargado con un ajuste nuevo. Las ocho celdas del cuaderno terminaron sin errores. No se comprobó la ejecución en otros sistemas.

La base declarada diciembre de 2014 requiere aclaración porque el total publicado para ese mes es 99,13. Lo conservamos sin reescalarlo. Tampoco disponemos de todos los calendarios y versiones históricos del indicador. Los seis bloques y su historia compartida limitan lo que se puede concluir sobre otros cambios del mercado. El siguiente paso es fijar la evaluación antes de conocer nuevos meses y revisar con ellos el error y la incertidumbre.

El proyecto permite reproducir una proyección anual y comprobar sus datos, fechas y errores. ETS tiene menor error agregado que las tres referencias en los períodos estudiados, aunque la deriva lo supera en el caso de 2025. La utilidad demostrada es un procedimiento ejecutable y verificable; su precisión futura y su utilidad para usuarios requieren evaluación adicional.

### Fuentes

[BMC, tablero IPAP](https://www.bolsamercantil.com.co/user/tableros), vista Niveles, Total agropecuario, captura del 23 de octubre de 2026; [metodología de julio de 2022](https://www.bolsamercantil.com.co/sites/default/files/2022-08/14.%20Metodolog%C3%ADa%20IPAP.pdf), contexto del indicador.

[statsmodels 0.14.6, ExponentialSmoothing](https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.holtwinters.ExponentialSmoothing.html), implementación utilizada. [Repositorio PUJ Cali](https://github.com/sperez211/ipap-bmc-puj-cali), código, documentación y resultados.

### Declaración de uso de IA

Espacio reservado para completar manualmente por el equipo antes de la entrega.

