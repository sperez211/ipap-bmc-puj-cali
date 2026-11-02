# Guía para ejecutar y explicar el proyecto IPAP BMC

@identidad

## 1 Cómo empezar

Esta guía permite recorrer el trabajo desde los datos hasta la explicación de los resultados. Empieza por entender qué se está pronosticando. Después puedes ejecutar el programa y estudiar sus funciones en detalle. Los archivos de esta carpeta bastan para hacer ese recorrido.

El informe técnico resume el proyecto. Este manual forma parte de la documentación de uso y desarrolla los pasos que el informe presenta de manera breve. Si solo quieres leer los resultados, abre el informe, resultados/LEER_RESULTADOS.md y las imágenes PNG. Si quieres repetir los cálculos, sigue las instrucciones de instalación. El cuaderno permite recorrerlos por etapas.

Una carpeta es un lugar donde se agrupan archivos. Aquí, datos contiene las observaciones que recibe el modelo; modelos conserva el ajuste entrenado; resultados guarda lo que produce el programa; documentacion contiene la procedencia y los textos de los documentos. Los experimentos son complementarios y no hacen falta para utilizar el ajuste final.

El archivo README.md se puede leer en GitHub o con un editor de texto. Los DOCX se abren con Word o un programa compatible. Las imágenes PNG se abren con el visor de imágenes. Los CSV son tablas de texto que también pueden importarse en Excel. Un archivo PY contiene instrucciones para Python y un IPYNB es un cuaderno que reúne instrucciones, explicaciones y resultados.

## 2 Qué pronosticamos

La variable es el Total agropecuario mensual del Índice de Precios Agropecuarios de la Bolsa Mercantil de Colombia, IPAP BMC. Cada observación corresponde a un mes. El objetivo es estimar los doce niveles mensuales posteriores a una fecha de corte.

Un índice resume movimientos de precios respecto a una referencia. Sus valores se expresan en puntos. El nivel 254,74 de septiembre de 2026 no significa 254,74 pesos, ni un precio por kilogramo. Tampoco es por sí solo una variación de 254,74 %. Para calcular una variación porcentual entre dos fechas habría que dividir el cambio por el nivel inicial y multiplicar por cien.

El proyecto trabaja con el agregado publicado. No reconstruye el indicador a partir de facturas, no calcula precios para productos concretos y no determina qué productor debe comprar o vender. Una trayectoria agregada puede ayudar a preparar escenarios, pero no medimos un beneficio monetario ni una relación de causa y efecto.

La fecha de corte es el último mes que permitimos conocer al modelo. El horizonte indica cuántos meses adelante se pronostica. Si el corte es septiembre de 2026, el horizonte 1 corresponde a octubre de 2026 y el horizonte 12 a septiembre de 2027. Un horizonte de doce meses y una ventana de 120 meses son cosas distintas: doce es lo que queremos estimar y 120 es el máximo de historia que usamos para entrenar.

## 3 Los datos y su procedencia

El único archivo que alimenta el modelo es datos/ipap_bmc_mensual.csv. Conserva 189 filas, de enero de 2011 a septiembre de 2026, y las columnas fecha y valor. La primera fila tiene fecha 2011-01 y valor 89.15. La última tiene fecha 2026-09 y valor 254.74. En el documento usamos coma decimal; dentro del CSV se usa punto.

La fuente es el [tablero oficial BMC](https://www.bolsamercantil.com.co/user/tableros). La selección utilizada fue IPAP BMC, vista Niveles, Total agropecuario. Los datos se capturaron el 23 de octubre de 2026. Esa fecha describe cuándo se obtuvo la copia, no el mes de cada observación ni una actualización automática al día en que alguien ejecute el programa.

La exportación del tablero no entregó un archivo descargable durante la captura. Se utilizó Mostrar como tabla y se recorrieron las filas visibles. Las pantallas sucesivas compartían algunos meses; esas coincidencias permitieron consolidar una sola fila por mes. Se conservaron los dos decimales visibles. Esta copia no ofrece una precisión superior a la publicada en pantalla.

El registro de la captura se conserva en documentacion/captura_bmc.json. Allí están la dirección de la fuente, la selección, la fecha de recuperación y las filas con sus valores. documentacion/evidencia_portal_bmc.png conserva una imagen del tablero. datos/fuente.json resume la procedencia y registra las huellas de los archivos. La captura es evidencia de la copia preservada y no una certificación de la BMC sobre el modelo.

Para preparar el CSV se expresaron las fechas como año y mes, se cambió la coma decimal por punto y se ordenaron las filas cronológicamente. Se revisó que los meses fueran únicos y continuos, y que los valores fueran números finitos y positivos. El programa no rellena meses ni modifica valores para que las comprobaciones pasen.

No se imputaron observaciones, no se reemplazaron valores por promedios y no se mezclaron niveles procedentes de informes PDF. Tampoco se reescaló el índice. El total de diciembre de 2014 se conserva en 99,13, aunque la metodología del productor declara ese mes como base. La diferencia queda pendiente de aclaración; no la convertimos en una corrección inventada.

Las 189 filas del CSV coinciden con los valores de la captura JSON a sus dos decimales. Se registra una huella SHA256 para detectar cambios de contenido. Una huella es una identificación calculada a partir de los bytes del archivo. Coincidir con la huella preservada ayuda a detectar sustituciones, pero no acredita por sí sola la autenticidad de una fuente externa. Por eso también se conservan la dirección, la selección y la evidencia.

Los CSV de resultados son salidas. No son bases adicionales que se introduzcan al modelo. Las predicciones de octubre de 2026 a septiembre de 2027 están separadas de las observaciones oficiales y se identifican como pronósticos del modelo. No se presentan como nuevos datos de BMC.

## 4 Cómo instalar y ejecutar en Mac

Para leer el informe y las imágenes no necesitas instalar Python. Para repetir los cálculos necesitas Python 3.12 y las bibliotecas indicadas en requirements.txt. La instalación de bibliotecas requiere Internet. Una vez instaladas, los cálculos utilizan los archivos locales de la carpeta.

Puedes obtener Python desde [su página oficial](https://www.python.org/downloads/release/python-31210/). El instalador de la familia 3.12 para macOS se identifica como universal2. La ejecución de referencia de este proyecto se comprobó con Python 3.12.14. Usar otra familia, por ejemplo 3.9 o 3.14, puede cambiar la compatibilidad de las dependencias; estas instrucciones se prepararon para 3.12.

1. Copia la carpeta completa a tu computador o descárgala desde GitHub con Code y Download ZIP. Descomprime el archivo antes de ejecutar. Para una prueba local resulta práctico usar una carpeta del Escritorio.

2. Abre Terminal con Spotlight, escribiendo Terminal. Escribe cd seguido de un espacio y arrastra la carpeta del proyecto desde Finder hacia esa ventana. Terminal insertará su ruta. Pulsa Intro. Este paso sitúa la terminal dentro de la carpeta; no mueve ni borra sus archivos.

3. Comprueba que la orden siguiente muestre una versión 3.12. El texto del resultado aparecerá después de pulsar Intro. No escribas el símbolo del indicador de la terminal.

```sh
python3.12 --version
```

4. Crea el entorno de trabajo. Un entorno es una carpeta que reúne las bibliotecas de este proyecto para que no se mezclen con las de otros trabajos. La orden no calcula todavía el pronóstico.

```sh
python3.12 -m venv .venv
```

5. Instala las dependencias. pip es el instalador de paquetes de Python y requirements.txt indica las versiones. Espera a que termine y aparezca otra vez el indicador de la terminal antes de escribir la siguiente orden.

```sh
.venv/bin/python -m pip install -r requirements.txt
```

6. Utiliza el modelo entrenado que viene en la entrega. La orden muestra doce meses y guarda la tabla del pronóstico. No estima otra vez los parámetros.

```sh
.venv/bin/python usar_modelo.py
```

7. Para reconstruir el trabajo completo y comprobarlo, ejecuta la orden siguiente. El archivo ejecutar.sh llama al programa principal y después a comprobar.py.

```sh
sh ejecutar.sh
```

También puedes realizar esas dos etapas por separado. La primera calcula y exporta; la segunda contrasta los resultados. Al terminar la comprobación debe aparecer el mensaje de comprobaciones correctas.

```sh
.venv/bin/python modelo_ipap.py
.venv/bin/python comprobar.py
```

La ejecución regenera modelos y resultados. El CSV oficial permanece intacto. La ficha del ajuste tendrá una nueva hora de entrenamiento y el PKL puede cambiar de huella aunque sus predicciones coincidan. Si quieres conservar una ejecución concreta, copia antes las carpetas modelos y resultados. El entorno .venv no forma parte de los archivos que se publican en GitHub ni hace falta copiarlo a otra persona.

## 5 Cómo ejecutar en Windows o Linux

La instalación y las comprobaciones de esta entrega se ejecutaron en macOS ARM64. Las siguientes órdenes indican la adaptación para otros sistemas; no se afirma que se hayan probado en Windows o Linux.

En Windows instala Python 3.12 desde python.org, descomprime la carpeta y abre una terminal dentro de ella. Puedes utilizar el lanzador py para escoger esa familia de Python. Ejecuta las órdenes una por una.

```bat
py -3.12 --version
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe usar_modelo.py
ejecutar.bat
```

Si utilizas PowerShell, la última orden puede escribirse como .\ejecutar.bat. Si prefieres las etapas separadas, llama a .venv\Scripts\python.exe modelo_ipap.py y después a .venv\Scripts\python.exe comprobar.py. Las barras de la ruta cambian respecto a macOS; los datos y los cálculos son los mismos.

En Linux se utilizan las órdenes de macOS si Python 3.12 está instalado y permite crear entornos con venv. Algunos sistemas separan venv en un paquete del sistema. La preparación de ese Python depende de la distribución. Una vez creado el entorno, las órdenes de instalación y ejecución del proyecto son iguales a las de macOS.

## 6 Qué hace el programa de principio a fin

Primero lee el CSV y comprueba su correspondencia con el registro de procedencia. Después organiza la serie por mes y rechaza errores de calendario o valores inválidos. Esta comprobación evita entrenar sobre una tabla incompleta o distinta de la documentada.

Para evaluar, elige seis cortes históricos. En cada uno separa la historia disponible y los doce meses que se van a pronosticar. ETS toma hasta 120 meses de esa historia. Las reglas sencillas utilizan los valores necesarios anteriores al mismo corte. Los valores reales posteriores se usan solamente después, para medir el error.

El programa reúne todas las predicciones en filas con método, origen, fecha, horizonte, predicción y real. A partir de ellas calcula las métricas agrupadas, por corte y por horizonte. También produce un diagnóstico de enero a diciembre de 2025 con un corte en diciembre de 2024.

Una vez realizada la evaluación, entrena el modelo final con los últimos 120 meses del CSV completo, de octubre de 2016 a septiembre de 2026. Guarda el ajuste, la historia utilizada y una ficha. Vuelve a cargarlo y genera octubre de 2026 a septiembre de 2027. Finalmente escribe las tablas, dibuja las figuras y prepara el archivo de lectura de resultados.

Entrenar significa estimar los parámetros a partir de observaciones conocidas. Evaluar significa comparar predicciones con valores reales que se mantuvieron fuera de ese ajuste. Usar el modelo guardado significa recuperar parámetros ya estimados. Son etapas diferentes, aunque estén dentro del mismo proyecto.

## 7 Qué significa cada método

### ETS con hasta 120 meses

ETS es un método de suavizamiento exponencial. Combina un nivel que sigue la posición de la serie, una tendencia que estima su dirección y un patrón estacional que se repite cada doce meses. Los datos recientes participan en la actualización de esos componentes con pesos que el ajuste estima. No se trata de sumar los 120 valores y dividirlos por 120.

La tendencia y la estacionalidad son aditivas: sus efectos se expresan en puntos del índice. La tendencia es amortiguada, lo que reduce la prolongación de su pendiente cuando el horizonte se aleja. De esa forma una dirección reciente no se extiende indefinidamente con la misma fuerza. La estacionalidad anual utiliza doce posiciones, una por mes.

La ventana de 120 meses conserva hasta diez ciclos anuales y limita la influencia de períodos lejanos. Cuando un corte tiene menos historia disponible, usa toda esa historia, siempre que haya al menos dos años para ajustar la estacionalidad. En septiembre de 2020 hay 117 meses y se utilizan los 117. En el ajuste final hay 189 observaciones disponibles, pero se usan las 120 más recientes.

La configuración se definió durante el desarrollo en períodos ya examinados. La evaluación es por eso retrospectiva. La ventana no se debe interpretar como una garantía de que diez años sean siempre la cantidad óptima de datos para cualquier mercado o fecha.

En el ajuste final, el parámetro del nivel es {{nivel}}, el de tendencia {{tendencia}}, el estacional {{estacional}} y el de amortiguación {{amortiguacion}}. Son valores estimados por el optimizador. El nivel responde con bastante peso a la información reciente. Un parámetro estacional de cero significa que el patrón estacional estimado inicialmente no se actualiza mediante ese componente; no significa que el modelo haya eliminado la estacionalidad.

### Último valor

Esta referencia, identificada como Naive en las tablas, pronostica el último nivel observado para los doce meses siguientes. Si el corte es diciembre de 2024, repite {{dic2024}} en todos los meses de 2025. Es una regla deliberadamente sencilla que permite comprobar si ETS aporta algo frente a mantener el índice constante.

### Mismo mes del año anterior

Naive12 repite los últimos doce meses en su mismo orden. Para pronosticar enero de 2025 usa enero de 2024; para febrero utiliza febrero de 2024, y así sucesivamente. Conserva un patrón anual sin estimar parámetros. Su error ayuda a evaluar si basta con repetir la estacionalidad observada.

### Deriva de doce meses

Deriva12 mide cuánto cambió el nivel entre el corte y el mismo mes del año anterior. Divide ese cambio entre doce para obtener un cambio mensual promedio y lo prolonga. Para el horizonte h suma h veces ese cambio mensual al último nivel. Solo usa datos conocidos en el corte.

En diciembre de 2024 el nivel es {{dic2024}} y en diciembre de 2023 es {{dic2023}}. Su diferencia dividida entre doce da {{paso_deriva}} puntos mensuales. La predicción para enero de 2025 es entonces {{deriva_enero}}. Esta cuenta explica la línea de deriva del gráfico; no requiere clima ni tasa de cambio futura.

Las tres reglas son referencias de comparación, también llamadas baselines. Tener una regla sencilla con buen resultado es útil. El objetivo de compararlas no es hacer que el método principal gane a toda costa.

## 8 Cómo se evaluó sin usar el futuro

Cada evaluación parte de una fecha de corte y calcula los doce meses siguientes de una sola vez. Durante ese año no se incorporan observaciones reales intermedias para corregir la trayectoria. Así se evalúa una proyección anual desde un origen fijo, no doce pronósticos de un mes que se actualizan continuamente.

@cortes

Los seis bloques evaluados cubren octubre de 2020 a septiembre de 2026. Cada método tiene 72 objetivos. Los bloques de evaluación no se superponen, pero los entrenamientos comparten meses. Esa historia común introduce dependencia entre resultados y debe tenerse en cuenta al interpretar la estabilidad.

El ejemplo de 2025 utiliza enero a diciembre de ese año después de entrenar hasta diciembre de 2024. Comparte meses con la evaluación de seis cortes. No se suman sus doce observaciones como si fueran evidencia completamente nueva. El proyecto guarda ambas tablas porque responden a dos maneras de mirar los mismos datos: años desde septiembre y un año calendario.

Para comprobar que el código no utiliza valores posteriores al corte, comprobar.py cambia esos valores por números enormes y vuelve a pronosticar. Si el entrenamiento está bien separado, las predicciones del corte deben permanecer iguales. Se realiza esta comprobación en los seis orígenes y en diciembre de 2024.

Ese control comprueba el comportamiento del código. No resuelve otra limitación distinta: la captura actual del tablero puede contener revisiones de meses anteriores. Sin las versiones y fechas históricas de publicación no podemos reconstruir exactamente qué cifra estaba disponible en cada fecha pasada. Además, los períodos ya se analizaron durante el desarrollo; no son una prueba final independiente.

## 9 Qué significan las métricas

El error de una fila es el valor real menos la predicción. Si es positivo, el modelo quedó por debajo del valor observado. Si es negativo, pronosticó por encima. Para resumir errores no basta con promediarlos con su signo, porque los positivos y negativos podrían compensarse y ocultar equivocaciones grandes.

El MAE es el promedio de los errores absolutos. Un MAE de {{mae}} puntos significa que el error absoluto medio en los 72 meses fue ese número de puntos. No significa que todos los meses se hayan equivocado exactamente lo mismo.

El RMSE eleva cada error al cuadrado, obtiene el promedio y toma su raíz cuadrada. Elevar al cuadrado hace que los errores grandes tengan más peso. Su resultado vuelve a estar en puntos del índice. Por eso un método puede tener buen MAE y un RMSE menos favorable si concentra algunos fallos grandes.

El MAPE divide el error absoluto de cada mes por su valor real, obtiene el promedio y lo expresa en porcentaje. Aquí es {{mape}} %. No es correcto convertirlo en una promesa de exactitud del 100 menos {{mape}} %. Es una medida promedio de error relativo en los meses evaluados. Los reales son positivos y no hay ceros en su denominador.

La columna n cuenta los objetivos que entraron en el cálculo. En la tabla agrupada es 72 por método; por corte es 12 y por horizonte es 6. En el diagnóstico de 2025 es 12. Al interpretar una cifra conviene comprobar también qué fechas incluye y cuántos errores la respaldan.

@metricas

ETS tiene RMSE {{rmse}}, MAE {{mae}} y MAPE {{mape}} %. Frente al último valor, cuyo RMSE es {{rmse_ultimo}}, la reducción relativa del RMSE es {{mejora_ultimo}} %. La cuenta divide la diferencia de errores por el error de esa referencia. No expresa crecimiento del índice ni un porcentaje de meses acertados.

La deriva obtiene RMSE {{rmse_deriva}}. ETS queda por debajo en la comparación agrupada, pero la diferencia es menor que frente al último valor. Es importante conservar esta referencia sencilla y mostrar los períodos en los que funciona mejor.

@metricas_2025

En 2025, ETS obtiene RMSE {{rmse_2025}} y la deriva {{rmse_deriva_2025}}. La deriva funciona mejor en ese diagnóstico. El resultado no contradice la tabla agrupada: se están resumiendo meses distintos. Tampoco conviene escoger solamente un año favorable para presentar el modelo.

## 10 Cómo leer los cinco gráficos

Todas las figuras se guardan como PNG dentro de resultados. Las curvas se diferencian con trazos, marcadores y leyendas. La posición de cada línea viene de los datos o de las predicciones calculadas. Unir puntos mensuales facilita la lectura, pero no significa que se hayan estimado observaciones diarias entre ellos.

### Historia del índice

@figura historia_ipap.png|Historia mensual del Total agropecuario. Cada posición horizontal corresponde a una fecha y la altura representa puntos del índice.

El eje horizontal recorre enero de 2011 a septiembre de 2026. El vertical muestra el nivel observado. Una subida indica que el índice aumentó entre esas fechas y una bajada indica que disminuyó. La figura permite reconocer movimientos prolongados y cambios de ritmo, pero no explica por sí sola sus causas. Aquí no hay predicciones: toda la línea procede del CSV oficial preservado.

### Comparación del año 2025

@figura comparacion_2025.png|Valores observados y doce predicciones desde diciembre de 2024. La leyenda identifica BMC y los cuatro métodos.

El eje horizontal muestra los meses de 2025 y el vertical los puntos del índice. La línea observada permite contrastar qué ocurrió con lo que cada método había pronosticado desde diciembre de 2024. La distancia vertical entre una predicción y la observación del mismo mes es su error con signo, según cuál quede más arriba.

La línea de último valor es horizontal porque repite el nivel del corte. La deriva tiene una pendiente constante porque prolonga un cambio mensual medio. Naive12 reproduce el patrón de los doce meses anteriores. ETS combina sus componentes y puede formar una trayectoria distinta. Una curva visualmente próxima durante parte del año no garantiza el menor RMSE: se calcula con los doce errores.

### Error por corte

@figura error_por_corte.png|RMSE de los doce meses posteriores a cada corte de septiembre. Un punto resume un año de predicciones de un método.

El eje horizontal identifica el año del corte de entrenamiento. Todos los cortes de esta figura son de septiembre. Por ejemplo, 2021 resume errores de octubre de 2021 a septiembre de 2022. El eje vertical muestra RMSE en puntos, no el nivel del índice ni un porcentaje. Estar más abajo significa menor error en ese bloque.

El peor corte de ETS es {{peor_corte}}, con RMSE {{peor_rmse}}. La curva ayuda a ver que la dificultad cambia entre períodos. Su forma no es una predicción del error de años futuros. Cada punto tiene doce objetivos y los entrenamientos comparten historia.

### Error por horizonte

@figura error_por_horizonte.png|RMSE según el número de meses después del corte. Cada punto reúne seis errores de un mismo horizonte y método.

El eje horizontal va de 1 a 12. El 1 reúne el primer mes posterior a los seis cortes y el 12 reúne el último mes de esos seis años pronosticados. El vertical sigue siendo RMSE en puntos. Esta figura no representa una sola trayectoria de doce meses; agrupa errores de seis fechas de origen.

En ETS, el RMSE es {{h1}} en el horizonte 1 y {{h12}} en el horizonte 12. Puede haber subidas y bajadas intermedias, porque el patrón anual y los cambios del índice no afectan por igual todos los plazos. Cada horizonte tiene pocas observaciones, así que la forma de la curva se debe interpretar con cautela.

Las curvas de Naive y Naive12 coinciden en el horizonte 12 porque ambas reglas terminan usando el valor del mes del corte para ese último pronóstico anual. Esa coincidencia tiene una explicación en las reglas y no es una duplicación accidental de las tablas.

### Historia reciente y pronóstico

@figura pronostico_12_meses.png|Observaciones recientes y proyección de octubre de 2026 a septiembre de 2027. El tramo discontinuo es una estimación del modelo.

El eje horizontal muestra meses de la historia reciente y los doce posteriores al corte. El vertical contiene puntos del IPAP. La línea vertical marca septiembre de 2026, último mes observado en la captura. La línea continua representa observaciones BMC y la discontinua representa pronósticos del modelo.

La unión de ambas líneas comienza en el último dato observado para que se vea desde dónde parte la trayectoria. Ese punto de unión no añade un mes futuro. La tabla del pronóstico tiene doce filas, desde octubre de 2026 hasta septiembre de 2027. La subida o bajada del tramo discontinuo es lo que estima ETS, no información oficial nueva.

No hay una banda de incertidumbre calibrada. La ausencia de una banda no significa que el resultado sea seguro. Tampoco significa que el error histórico se deba sumar y restar automáticamente al pronóstico para obtener un intervalo válido.

## 11 La tabla futura y los archivos de salida

@pronostico

La primera estimación es {{primero_futuro}} y la última {{ultimo_futuro}} puntos. Se calculan con el modelo entrenado con 120 meses hasta septiembre de 2026. Una nueva ejecución con la misma captura mantiene el mismo corte de información: no consulta ni actualiza automáticamente el tablero.

resultados/pronostico_12_meses.csv identifica método, origen, fecha, horizonte, predicción y tipo. El tipo pronostico_del_modelo permite distinguir esas filas de observaciones oficiales. No incluye una columna real porque todavía no están disponibles todos los objetivos futuros de ese año.

resultados/predicciones_6_cortes.csv tiene 288 filas: cuatro métodos, seis cortes y doce horizontes. resultados/predicciones_2025.csv tiene 48 filas: cuatro métodos por doce meses. En ambas, real es el nivel observado y prediccion es lo que produjo el método desde ese corte. El código calcula el error a partir de estas dos columnas.

metricas_6_cortes.csv resume cuatro métodos. metricas_2025.csv resume el diagnóstico anual. metricas_por_corte.csv tiene 24 filas y metricas_por_horizonte.csv tiene 48. Los CSV conservan más decimales que las tablas del informe; esas diferencias de presentación no cambian las cuentas.

LEER_RESULTADOS.md reúne una explicación breve y enlaces a los gráficos. comprobaciones.json registra la revisión de datos, métricas, predicciones y modelo. comprobacion_cuaderno.json indica cuántas celdas se ejecutaron y si hubo errores. Los registros describen las comprobaciones realizadas y no certifican precisión futura.

modelos/modelo_ets.pkl contiene el ajuste, su historia de entrenamiento y la ficha. modelos/ficha_modelo.json permite consultar esa ficha sin abrir el PKL. Distingue los meses del CSV y del ajuste, sus fechas, la ventana, los parámetros estimados, las versiones y la huella de los datos.

## 12 Qué significa el código por segmentos

Python lee instrucciones. Una función agrupa instrucciones bajo un nombre para poder usarlas varias veces. def crea una función y return devuelve su resultado. Un bucle for repite pasos sobre una colección. Un diccionario relaciona nombres con valores. Los nombres np y pd son abreviaturas de NumPy y pandas, las bibliotecas utilizadas para números y tablas.

BASE identifica la carpeta donde se encuentra el archivo, por lo que los datos no dependen de la ruta personal de un usuario. VENTANA vale 120 y ORIGENES contiene los seis cortes de septiembre. CONFIGURACION describe tendencia, amortiguación, estacionalidad, período anual e inicialización. NOMBRES y ESTILOS se usan para presentar las curvas; no intervienen en el ajuste.

Los fragmentos siguientes sirven para localizar y entender las funciones del archivo completo. No hace falta copiarlos ni ejecutarlos por separado. Las instrucciones de ejecución están en las secciones anteriores. Algunos fragmentos muestran solo el comienzo de una función; el resto está en modelo_ipap.py.

@codigo

### Los programas de apoyo

usar_modelo.py comprueba que el CSV coincida con la ficha, carga el paquete y muestra el futuro. No llama a entrenar. comprobar.py revisa la captura y el CSV, la forma de las tablas, las fechas y los valores reales. Recalcula las métricas mediante cuentas independientes de la función metricas, regenera las predicciones y comprueba siete cortes al alterar el futuro. También contrasta la historia del PKL y su pronóstico frente a un ajuste nuevo.

ejecutar_cuaderno.py abre el cuaderno, crea un kernel temporal con el Python que lo ejecuta y recorre sus celdas en orden. Un kernel es el proceso que realiza las instrucciones del cuaderno. Se guarda un archivo ejecutado y un registro de comprobación. No hace falta instalar un kernel global para este recorrido.

ejecutar.sh y ejecutar.bat agrupan las dos órdenes principales para macOS/Linux y Windows. requirements.txt fija las versiones principales de las bibliotecas de cálculo. requirements-cuaderno.txt añade lo necesario para ejecutar el cuaderno. requirements-documentos.txt añade python-docx para regenerar los Word.

NumPy maneja arreglos de números, pandas organiza fechas y tablas, statsmodels implementa el ajuste, SciPy participa en su optimización y Matplotlib dibuja las figuras. No son datos extra del mercado; son herramientas de cálculo. Se fijaron versiones para facilitar la reproducción.

## 13 Leer y ejecutar el cuaderno

Proyecto_IPAP.ipynb es el cuaderno editable. Proyecto_IPAP_ejecutado.ipynb contiene las mismas etapas con sus salidas. GitHub permite leerlo sin instalar un editor de cuadernos. El recorrido tiene ocho celdas de código, intercaladas con explicaciones.

El orden es leer la serie, separar 2025, pronosticar, comparar reglas, evaluar seis cortes, revisar horizontes y guardar el modelo con sus gráficos. Las celdas utilizan las funciones de modelo_ipap.py. El cuaderno no mantiene otro cálculo independiente con fórmulas distintas.

Para ejecutarlo, sitúa la terminal en la carpeta del proyecto y utiliza el entorno creado. Primero instala las dependencias opcionales y luego ejecuta el recorrido y su comprobación.

```sh
.venv/bin/python -m pip install -r requirements-cuaderno.txt
.venv/bin/python ejecutar_cuaderno.py
.venv/bin/python comprobar.py
```

En Windows cambia .venv/bin/python por .venv\Scripts\python.exe. El registro esperado indica ocho celdas de código y cero errores. La última celda vuelve a guardar el ajuste y el pronóstico, por eso se ejecuta después comprobar.py. Para reconstruir todos los archivos desde las observaciones, la entrada principal sigue siendo modelo_ipap.py.

## 14 Comprobaciones y problemas de ejecución

La instalación y ejecución se verificaron en un entorno nuevo con Python 3.12.14 en macOS ARM64. Los controles contrastaron 189 observaciones con la captura, regeneraron 336 predicciones históricas, recalcularon las tablas y revisaron siete cortes frente a cambios del futuro. El ajuste final se recargó y se comparó con un ajuste nuevo. El cuaderno terminó sin errores.

Estas comprobaciones verifican la coherencia local entre archivos y cálculos. No acreditan que todos los valores fueran conocidos en tiempo real en cada fecha pasada, ni que otro computador produzca archivos idénticos byte por byte. Pequeñas diferencias numéricas pueden depender del entorno. La ficha identifica el entorno utilizado y el manifiesto conserva huellas de la entrega.

Si la terminal dice command not found al llamar a python3.12, esa versión no está accesible con ese nombre. Revisa la instalación y abre otra ventana de Terminal. Si dice No such file or directory para un archivo del proyecto, comprueba que la terminal esté en la carpeta correcta y que hayas descomprimido la entrega.

Si aparece ModuleNotFoundError, revisa que hayas instalado los paquetes con el mismo Python que estás utilizando. Aquí las órdenes llaman explícitamente a .venv/bin/python o .venv\Scripts\python.exe para evitar esa confusión. Instalar una biblioteca en otro Python no la instala automáticamente en este entorno.

Si aparece el mensaje de que el CSV no coincide con su procedencia, no cambies la huella para ocultar el problema. Recupera el archivo de la entrega o documenta conscientemente una captura nueva antes de entrenar con otros datos. Si aparece un fallo de convergencia, conserva el mensaje y revisa ese ajuste. El programa detiene la ejecución para que no se presente silenciosamente un modelo que no completó su optimización.

Si Excel muestra el CSV en una sola columna, impórtalo con coma como separador y punto como decimal. No guardes sobre el archivo original después de cambiar su presentación en Excel. Puedes trabajar con una copia para leer o calcular algo adicional.

Los gráficos son archivos PNG y no necesitan una aplicación de programación para verse. Un PKL se usa mediante usar_modelo.py. Para leer el detalle del entrenamiento abre la ficha JSON con un editor de texto. El archivo no tiene por qué aparecer como una tabla de Excel.

## 15 Configuraciones complementarias

experimentos/comparar_variantes.py permite revisar cambios de tendencia, estacionalidad, ventana de entrenamiento, transformación logarítmica y combinaciones con deriva. Es material técnico complementario. No se necesita para obtener el pronóstico guardado ni para ejecutar el programa principal.

Las mezclas ETS_deriva_25, ETS_deriva_50 y ETS_deriva_75 combinan ETS con historia completa y deriva, usando respectivamente 25, 50 y 75 % de peso en ETS. El resto corresponde a deriva. Los pesos son fijos en esta comparación. ETS_logaritmos ajusta sobre logaritmos y vuelve a la escala original; sus predicciones transformadas no incluyen corrección de sesgo. Esa transformación no se aplica al modelo final.

Sin amortiguación, la pendiente se prolonga sin reducirla. Sin tendencia se conservan nivel y patrón anual; sin estacionalidad se conservan nivel y tendencia amortiguada. Holt lineal combina nivel y tendencia sin amortiguar, sin patrón anual. El suavizamiento simple estima solo el nivel y produce un pronóstico constante. La estacionalidad multiplicativa hace que el efecto anual cambie en proporción al nivel; la aditiva lo expresa en puntos. Las ventanas de 60 y 120 meses limitan la historia previa utilizada. Historia completa utiliza todos los meses disponibles antes de cada corte. Los tres métodos de referencia conservan las definiciones de la sección 7.

@variantes

La tabla conserva todas las configuraciones comparadas, incluidas las que tienen peor error. La configuración de 120 meses ofrece un equilibrio favorable entre RMSE, MAE y MAPE en los períodos examinados. La estacionalidad multiplicativa alcanza menor RMSE agrupado, pero mayor MAE y MAPE. No existe un ganador universal que resulte mejor por cualquier criterio.

Seleccion_interna representa otro procedimiento: en cada corte escoge una configuración utilizando solo cuatro bloques anuales anteriores completos. Nunca utiliza para elegirla los meses posteriores a ese corte. Su RMSE agrupado es peor que el del modelo final. Se conserva el resultado para mostrar el alcance de esa comparación, no para reemplazar automáticamente el ajuste entregado.

La comparación es retrospectiva y emplea períodos examinados durante el desarrollo. Buscar más variantes sobre esos mismos meses no crea una prueba independiente. El siguiente control útil es definir por adelantado cómo evaluar meses nuevos y observar su error cuando estén disponibles. El protocolo, los diagnósticos de convergencia, las selecciones y las predicciones del experimento están en experimentos/resultados.

## 16 Regenerar documentos y conservar la entrega

El informe y esta guía se generan con documentacion/generar_documentos.py. El programa lee los CSV y la ficha para insertar cifras, tablas y figuras. Los textos se conservan en contenido_informe.md y contenido_guia.md. Las imágenes provienen de la misma ejecución que escribe las predicciones. Así puede comprobarse la relación entre datos, cálculo y explicación.

Después de ejecutar el modelo y sus comprobaciones, instala la dependencia de documentos y utiliza la orden siguiente. En Windows se adapta la ruta del Python de la misma forma que en las otras instrucciones.

```sh
.venv/bin/python -m pip install -r requirements-documentos.txt
.venv/bin/python documentacion/generar_documentos.py
```

La regeneración vuelve a escribir ambos Word. Cualquier cambio manual que se haya hecho dentro de ellos debe conservarse antes o incorporarse también en sus textos fuente. En particular, completa la declaración de IA después de la última regeneración del informe. El archivo DECLARACION_IA.md y el espacio del informe quedan reservados para el equipo.

El repositorio y la carpeta permiten conservar los archivos de la entrega. MANIFIESTO.json identifica su contenido. Después de regenerar resultados o modificar documentos, sus huellas pueden dejar de representar el nuevo contenido. Para actualizarlo conscientemente, ejecuta documentacion/generar_manifiesto.py después de terminar los cambios. Las verificaciones de cálculos y la conservación de una entrega son dos controles distintos: uno comprueba relaciones numéricas y el otro identifica qué archivos se enviaron.

## 17 Fuentes y alcance del trabajo

Los niveles utilizados proceden del [tablero de la Bolsa Mercantil de Colombia](https://www.bolsamercantil.com.co/user/tableros), selección Niveles y Total agropecuario, captura del 23 de octubre de 2026. La [metodología IPAP de julio de 2022](https://www.bolsamercantil.com.co/sites/default/files/2022-08/14.%20Metodolog%C3%ADa%20IPAP.pdf) describe la construcción del indicador a partir del registro de facturas. Sus tratamientos de insumos no se repitieron sobre el total agregado que aquí se pronostica.

El ajuste usa [ExponentialSmoothing de statsmodels 0.14.6](https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.holtwinters.ExponentialSmoothing.html). Se consultó como antecedente [Commodity Price Forecasting de María Sol Pera](https://github.com/msolpera/forecasting_agro), dedicado a otros productos y modelos. Sus bases, sus modelos entrenados y sus archivos de código no forman parte de esta entrega. La implementación utiliza la serie BMC y las bibliotecas declaradas.

El [repositorio PUJ Cali](https://github.com/sperez211/ipap-bmc-puj-cali) reúne este material. El proyecto entrega una evaluación histórica reproducible y una proyección central. No incluye intervalos calibrados, precios por finca, evaluación de impacto económico ni una garantía de precisión futura. Esos límites forman parte de la interpretación del resultado.

