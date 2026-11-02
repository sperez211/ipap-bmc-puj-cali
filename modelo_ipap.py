from pathlib import Path
from datetime import datetime, timezone
from importlib.metadata import version
import hashlib
import json
import pickle
import platform

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

BASE = Path(__file__).resolve().parent
VENTANA = 120
ORIGENES = [f"{anio}-09" for anio in range(2020, 2026)]
CONFIGURACION = dict(trend="add", damped_trend=True, seasonal="add",
                     seasonal_periods=12, initialization_method="estimated")
NOMBRES = {"ETS_120_meses": "ETS hasta 120 meses",
           "Naive": "Último valor", "Naive12": "Mismo mes del año anterior", "Deriva12": "Deriva de doce meses"}
ESTILOS = {"ETS_120_meses": ("-", "o"),
           "Naive": (":", "^"), "Naive12": ("-.", "D"), "Deriva12": ((0, (5, 2)), "x")}


def huella(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def cargar_datos():
    ruta = BASE / "datos/ipap_bmc_mensual.csv"
    fuente = json.loads((BASE / "datos/fuente.json").read_text(encoding="utf-8"))
    if huella(ruta) != fuente["sha256_csv"]:
        raise ValueError("El CSV no coincide con su registro de procedencia.")
    tabla = pd.read_csv(ruta)
    if list(tabla.columns) != ["fecha", "valor"]:
        raise ValueError("El CSV debe tener las columnas fecha,valor.")
    fechas = pd.to_datetime(tabla.fecha, format="%Y-%m", errors="raise").dt.to_period("M")
    serie = pd.Series(pd.to_numeric(tabla.valor, errors="raise").to_numpy(),
                      index=pd.PeriodIndex(fechas), name="IPAP").sort_index()
    if len(serie) < 36 or serie.index.hasnans or serie.index.has_duplicates:
        raise ValueError("Se necesitan al menos 36 meses y fechas válidas sin duplicados.")
    if not serie.index.equals(pd.period_range(serie.index[0], serie.index[-1], freq="M")):
        raise ValueError("Faltan meses. El programa no los rellena.")
    if not np.isfinite(serie).all() or (serie <= 0).any():
        raise ValueError("Los niveles deben ser números finitos y positivos.")
    if (len(serie) != fuente["filas"] or str(serie.index[0]) != fuente["inicio"]
            or str(serie.index[-1]) != fuente["fin"]):
        raise ValueError("La cobertura del CSV no coincide con fuente.json.")
    return serie


def entrenar(historia, ventana=VENTANA):
    datos = historia.iloc[-ventana:] if ventana else historia
    if len(datos) < 24:
        raise ValueError("El ajuste estacional necesita al menos dos años.")
    ajuste = ExponentialSmoothing(datos.to_numpy(), **CONFIGURACION).fit()
    if not ajuste.mle_retvals.success:
        raise RuntimeError("La optimización de ETS no convergió. Revisar este ajuste.")
    return ajuste


def pronosticar(historia, ventana=VENTANA):
    ajuste = entrenar(historia, ventana)
    fechas = pd.period_range(historia.index[-1] + 1, periods=12, freq="M")
    valores = np.asarray(ajuste.forecast(12), dtype=float)
    if len(valores) != 12 or not np.isfinite(valores).all():
        raise RuntimeError("El modelo no produjo doce predicciones válidas.")
    return pd.Series(valores, index=fechas, name="prediccion")


def evaluar(serie, origenes=ORIGENES):
    filas = []
    for texto in origenes:
        origen = pd.Period(texto, freq="M")
        if origen not in serie.index:
            raise ValueError(f"No existe el corte {origen}.")
        historia = serie.loc[:origen]
        ets = pronosticar(historia)
        reales = serie.reindex(ets.index)
        if reales.isna().any():
            raise ValueError(f"Faltan datos reales para evaluar el año posterior a {origen}.")
        metodos = {
            "ETS_120_meses": ets.to_numpy(),
            "Naive": np.repeat(historia.iloc[-1], 12),
            "Naive12": historia.iloc[-12:].to_numpy(),
            "Deriva12": historia.iloc[-1] + np.arange(1, 13)
                        * (historia.iloc[-1] - historia.iloc[-13]) / 12,
        }
        for nombre, valores in metodos.items():
            for h, fecha in enumerate(ets.index, 1):
                filas.append(dict(modelo=nombre, origen=str(origen), fecha=str(fecha), horizonte=h,
                                  prediccion=float(valores[h-1]), real=float(reales.loc[fecha])))
    return pd.DataFrame(filas)


def metricas(predicciones, agrupar=("modelo",)):
    filas = []
    for clave, grupo in predicciones.groupby(list(agrupar), sort=False):
        clave = clave if isinstance(clave, tuple) else (clave,)
        error = grupo.real.to_numpy() - grupo.prediccion.to_numpy()
        filas.append(dict(zip(agrupar, clave), RMSE=float(np.sqrt(np.mean(error**2))),
                          MAE=float(np.mean(abs(error))),
                          MAPE=float(100*np.mean(abs(error/grupo.real.to_numpy()))), n=len(grupo)))
    return pd.DataFrame(filas)


def guardar_modelo(serie):
    if not serie.equals(cargar_datos()):
        raise ValueError("El ajuste final debe partir del CSV completo verificado.")
    historia = serie.iloc[-VENTANA:]
    modelo = entrenar(serie)
    ficha = dict(nombre="ETS_120_meses", entrenado_utc=datetime.now(timezone.utc).isoformat(),
                 inicio_entrenamiento=str(historia.index[0]), fin_entrenamiento=str(historia.index[-1]),
                 observaciones_entrenamiento=len(historia), observaciones_csv=len(serie),
                 inicio_csv=str(serie.index[0]), fin_csv=str(serie.index[-1]), ventana_maxima_meses=VENTANA,
                 horizonte_meses=12, unidad="puntos del índice", configuracion=CONFIGURACION,
                 datos_sha256=huella(BASE/"datos/ipap_bmc_mensual.csv"),
                 python=platform.python_version(), plataforma=platform.platform(),
                 versiones={n: version(n) for n in ["numpy", "pandas", "scipy", "statsmodels", "matplotlib"]},
                 parametros={n: float(modelo.params[n]) for n in
                             ["smoothing_level", "smoothing_trend", "smoothing_seasonal", "damping_trend"]},
                 alcance="Evaluación retrospectiva sobre períodos reutilizados. Sin intervalos calibrados.")
    paquete = dict(modelo=modelo, historia=historia, ficha=ficha)
    (BASE/"modelos").mkdir(exist_ok=True)
    (BASE/"modelos/modelo_ets.pkl").write_bytes(pickle.dumps(paquete, protocol=4))
    (BASE/"modelos/ficha_modelo.json").write_text(json.dumps(ficha, indent=2, ensure_ascii=False), encoding="utf-8")
    return paquete


def cargar_modelo():
    with (BASE/"modelos/modelo_ets.pkl").open("rb") as archivo:
        paquete = pickle.load(archivo)
    if paquete["ficha"]["nombre"] != "ETS_120_meses":
        raise ValueError("El archivo no corresponde al modelo final.")
    return paquete


def pronostico_guardado(paquete):
    origen = pd.Period(paquete["ficha"]["fin_entrenamiento"], freq="M")
    fechas = pd.period_range(origen+1, periods=12, freq="M")
    valores = np.asarray(paquete["modelo"].forecast(12), dtype=float)
    if len(valores) != 12 or not np.isfinite(valores).all():
        raise RuntimeError("El modelo guardado produjo una trayectoria inválida.")
    return pd.DataFrame(dict(modelo="ETS_120_meses", origen=str(origen), fecha=list(map(str, fechas)),
                             horizonte=np.arange(1, 13), prediccion=valores, tipo="pronostico_del_modelo"))


def preparar_graficos():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
                         "font.size": 10, "text.color": "black",
                         "axes.labelcolor": "black", "xtick.color": "black", "ytick.color": "black",
                         "axes.spines.top": False, "axes.spines.right": False})
    return plt


def graficar(serie, bloques, calendario, futuro):
    plt = preparar_graficos()
    salida = BASE/"resultados"

    def guardar(figura, nombre):
        figura.tight_layout()
        figura.savefig(salida/nombre, dpi=220)
        plt.close(figura)

    def curva(eje, x, y, modelo):
        linea, marcador = ESTILOS[modelo]
        eje.plot(x, y, color="black", linestyle=linea, marker=marcador, markersize=3.5,
                 linewidth=1.5, markerfacecolor="white", label=NOMBRES[modelo])

    fig, eje = plt.subplots(figsize=(8, 3.6))
    eje.plot(serie.index.to_timestamp(), serie.to_numpy(), color="black", linewidth=1.4)
    eje.set(xlabel="Mes", ylabel="Puntos del IPAP")
    eje.grid(axis="y", color=".88", linewidth=.6)
    guardar(fig, "historia_ipap.png")

    fig, eje = plt.subplots(figsize=(8, 3.6))
    real = calendario[calendario.modelo=="ETS_120_meses"]
    eje.plot(pd.to_datetime(real.fecha), real.real, color="black", linewidth=2.3, label="Observado BMC")
    for nombre, grupo in calendario.groupby("modelo", sort=False):
        curva(eje, pd.to_datetime(grupo.fecha), grupo.prediccion, nombre)
    eje.set(xlabel="Mes de 2025", ylabel="Puntos del IPAP")
    eje.legend(fontsize=9, ncol=2, frameon=False)
    eje.grid(axis="y", color=".88", linewidth=.6)
    fig.autofmt_xdate()
    guardar(fig, "comparacion_2025.png")

    for campo, nombre, titulo in [("origen", "error_por_corte.png", "Corte de entrenamiento"),
                                  ("horizonte", "error_por_horizonte.png", "Meses después del corte")]:
        resumen = metricas(bloques, ("modelo", campo))
        fig, eje = plt.subplots(figsize=(8, 3.0))
        for modelo, grupo in resumen.groupby("modelo", sort=False):
            x = [int(p[:4]) for p in grupo.origen] if campo=="origen" else grupo.horizonte
            curva(eje, x, grupo.RMSE, modelo)
        eje.set(xlabel=titulo, ylabel="RMSE en puntos")
        eje.set_xticks(range(2020,2026) if campo=="origen" else range(1,13))
        eje.legend(fontsize=9, ncol=2, frameon=False)
        eje.grid(axis="y", color=".88", linewidth=.6)
        guardar(fig, nombre)

    fig, eje = plt.subplots(figsize=(8, 3.6))
    reciente = serie.iloc[-24:]
    eje.plot(reciente.index.to_timestamp(), reciente.to_numpy(), color="black", linewidth=1.6, label="Observado BMC")
    fechas = [reciente.index[-1].to_timestamp()]+list(pd.to_datetime(futuro.fecha))
    eje.plot(fechas, [reciente.iloc[-1]]+futuro.prediccion.tolist(), "--", color="black", linewidth=1.6, label="Pronóstico ETS")
    eje.axvline(reciente.index[-1].to_timestamp(), color="black", linestyle=":", linewidth=.8)
    eje.set(xlabel="Mes", ylabel="Puntos del IPAP")
    eje.legend(fontsize=10, frameon=False)
    eje.grid(axis="y", color=".88", linewidth=.6)
    fig.autofmt_xdate()
    guardar(fig, "pronostico_12_meses.png")


def tabla_markdown(tabla):
    lineas = ["| "+" | ".join(tabla.columns)+" |", "| "+" | ".join(["---"]*len(tabla.columns))+" |"]
    for fila in tabla.itertuples(index=False, name=None):
        lineas.append("| "+" | ".join(f"{x:.2f}" if isinstance(x,float) else str(x) for x in fila)+" |")
    return "\n".join(lineas)


def escribir_resultados(bloques, calendario, ficha):
    resumen = metricas(bloques)
    indice = resumen.set_index("modelo")
    mejora = 100*(1-indice.loc["ETS_120_meses","RMSE"]/indice.loc["Naive","RMSE"])
    texto = f"""# Resultados del pronóstico IPAP BMC

ETS usa hasta 120 meses anteriores a cada corte y pronostica doce meses sin recibir datos reales intermedios. El CSV oficial conserva sus 189 meses completos.

## Evaluación histórica

Los seis cortes de septiembre de 2020 a septiembre de 2025 generan 72 predicciones por método, de octubre de 2020 a septiembre de 2026.

{tabla_markdown(resumen)}

RMSE y MAE están en puntos del índice. MAPE está en porcentaje. ETS reduce el RMSE {mejora:.2f}% frente a repetir el último valor. La ventana de hasta 120 meses se definió durante el desarrollo. Los períodos evaluados ya se examinaron, por lo que estos resultados son retrospectivos y no una nueva validación independiente.

![RMSE por corte](error_por_corte.png)
![RMSE por horizonte](error_por_horizonte.png)

## Ejemplo de 2025

Se entrena hasta diciembre de 2024 y se pronostica enero a diciembre de 2025. Este ejercicio comparte meses con los seis cortes y no es otra prueba independiente.

{tabla_markdown(metricas(calendario))}

![Valores y pronósticos de 2025](comparacion_2025.png)

## Pronóstico final

El modelo guardado se ajustó con {ficha['observaciones_entrenamiento']} meses, de {ficha['inicio_entrenamiento']} a {ficha['fin_entrenamiento']}. Los doce valores futuros están en pronostico_12_meses.csv. Son estimaciones del modelo, no observaciones oficiales ni precios en pesos. No hay intervalos calibrados en esta entrega.

![Historia y pronóstico](pronostico_12_meses.png)

La captura BMC puede incorporar revisiones y no permite recuperar todas las versiones históricas. Se conservaron los niveles publicados sin imputar ni reescalar. El nivel 99,13 de diciembre de 2014 sigue pendiente de aclaración frente a la base declarada por el productor.
"""
    (BASE/"resultados/LEER_RESULTADOS.md").write_text(texto, encoding="utf-8")


def main():
    serie = cargar_datos()
    (BASE/"resultados").mkdir(exist_ok=True)
    bloques = evaluar(serie)
    calendario = evaluar(serie, ["2024-12"])
    tablas = {"predicciones_6_cortes": bloques, "predicciones_2025": calendario,
              "metricas_6_cortes": metricas(bloques), "metricas_2025": metricas(calendario),
              "metricas_por_corte": metricas(bloques, ("origen","modelo")),
              "metricas_por_horizonte": metricas(bloques, ("modelo","horizonte"))}
    for nombre, tabla in tablas.items():
        tabla.to_csv(BASE/"resultados"/f"{nombre}.csv", index=False)
    guardar_modelo(serie)
    paquete = cargar_modelo()
    futuro = pronostico_guardado(paquete)
    futuro.to_csv(BASE/"resultados/pronostico_12_meses.csv", index=False)
    graficar(serie, bloques, calendario, futuro)
    escribir_resultados(bloques, calendario, paquete["ficha"])
    print(f"Datos oficiales: {len(serie)} meses, {serie.index[0]} a {serie.index[-1]}.")
    print("Evaluación retrospectiva: 72 objetivos por método.")
    print(metricas(bloques).round(4).to_string(index=False))
    print(f"Modelo final: {len(paquete['historia'])} meses de entrenamiento.")
    print(f"Pronóstico: {futuro.fecha.iloc[0]} a {futuro.fecha.iloc[-1]}.")


if __name__ == "__main__":
    main()
