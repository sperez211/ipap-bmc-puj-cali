import json
import platform
import numpy as np
import pandas as pd

from modelo_ipap import (BASE, VENTANA, ORIGENES, cargar_datos, cargar_modelo, evaluar,
                         huella, pronosticar, pronostico_guardado)


def comprobar_metricas(predicciones, guardadas, campos):
    for _, fila in guardadas.iterrows():
        grupo = predicciones
        for campo in campos:
            grupo = grupo[grupo[campo]==fila[campo]]
        assert len(grupo), "Hay una métrica sin predicciones asociadas."
        error = grupo.real.to_numpy()-grupo.prediccion.to_numpy()
        esperado = [np.sqrt(np.mean(error**2)), np.mean(abs(error)),
                    100*np.mean(abs(error/grupo.real.to_numpy())), len(grupo)]
        np.testing.assert_allclose(fila[["RMSE","MAE","MAPE","n"]].to_numpy(dtype=float), esperado,
                                   rtol=1e-9, atol=1e-9)


def main():
    serie = cargar_datos()
    fuente = json.loads((BASE/"datos/fuente.json").read_text(encoding="utf-8"))
    captura = BASE/"documentacion/captura_bmc.json"
    assert huella(captura)==fuente["sha256_captura_json_original"]
    filas = pd.DataFrame(json.loads(captura.read_text(encoding="utf-8"))["rows"])
    meses = pd.to_datetime(filas.fecha, format="%d/%m/%Y").dt.to_period("M")
    copia = pd.Series(filas.valor.str.replace(",",".",regex=False).astype(float).to_numpy(),
                       index=pd.PeriodIndex(meses)).sort_index()
    pd.testing.assert_series_equal(serie,copia,check_names=False)
    assert len(list((BASE/"datos").glob("*.csv")))==1

    bloques = pd.read_csv(BASE/"resultados/predicciones_6_cortes.csv")
    calendario = pd.read_csv(BASE/"resultados/predicciones_2025.csv")
    modelos = {"ETS_120_meses","Naive","Naive12","Deriva12"}
    for tabla, origenes in [(bloques,ORIGENES),(calendario,["2024-12"])]:
        assert set(tabla.modelo)==modelos
        assert not tabla.duplicated(["modelo","origen","fecha","horizonte"]).any()
        assert np.isfinite(tabla[["real","prediccion"]]).all().all()
        for _, grupo in tabla.groupby("modelo"):
            esperado = {(o,str(pd.Period(o,"M")+h),h) for o in origenes for h in range(1,13)}
            assert len(grupo)==len(esperado)
            assert set(zip(grupo.origen,grupo.fecha,grupo.horizonte))==esperado
            np.testing.assert_allclose(grupo.real, serie.reindex(pd.PeriodIndex(grupo.fecha,freq="M")))
        regenerada = evaluar(serie,origenes)
        np.testing.assert_allclose(tabla.prediccion,regenerada.prediccion,rtol=1e-8,atol=1e-8)

    tablas = [(bloques,"metricas_6_cortes.csv",["modelo"]),
              (calendario,"metricas_2025.csv",["modelo"]),
              (bloques,"metricas_por_corte.csv",["origen","modelo"]),
              (bloques,"metricas_por_horizonte.csv",["modelo","horizonte"])]
    for predicciones, archivo, campos in tablas:
        comprobar_metricas(predicciones,pd.read_csv(BASE/"resultados"/archivo),campos)

    for origen in ORIGENES+["2024-12"]:
        alterada = serie.copy()
        alterada.loc[pd.Period(origen,"M")+1:] = 1e9
        adulterada = evaluar(alterada,[origen])
        original = calendario if origen=="2024-12" else bloques[bloques.origen==origen]
        np.testing.assert_allclose(original.prediccion,adulterada.prediccion,rtol=1e-8,atol=1e-8)

    paquete = cargar_modelo()
    ficha = paquete["ficha"]
    historia = serie.iloc[-VENTANA:]
    pd.testing.assert_series_equal(paquete["historia"],historia)
    np.testing.assert_allclose(paquete["modelo"].model.endog.ravel(),historia)
    assert ficha["datos_sha256"]==huella(BASE/"datos/ipap_bmc_mensual.csv")
    assert ficha["observaciones_csv"]==len(serie)
    assert ficha["observaciones_entrenamiento"]==len(historia)
    assert ficha["inicio_entrenamiento"]==str(historia.index[0])
    assert ficha["fin_entrenamiento"]==str(historia.index[-1])
    futuro = pronostico_guardado(paquete)
    np.testing.assert_allclose(futuro.prediccion,pronosticar(serie),rtol=1e-8,atol=1e-8)
    exportado = pd.read_csv(BASE/"resultados/pronostico_12_meses.csv")
    assert exportado.fecha.tolist()==futuro.fecha.tolist()
    assert exportado.horizonte.tolist()==list(range(1,13))
    assert set(exportado.tipo)=={"pronostico_del_modelo"}
    assert "real" not in exportado.columns
    np.testing.assert_allclose(exportado.prediccion,futuro.prediccion,rtol=1e-8,atol=1e-8)
    for nombre in ["historia_ipap.png","comparacion_2025.png","error_por_corte.png",
                   "error_por_horizonte.png","pronostico_12_meses.png","LEER_RESULTADOS.md"]:
        assert (BASE/"resultados"/nombre).is_file()

    evidencia = dict(csv_coincide_con_captura=True,filas_csv=len(serie),
                     predicciones_historicas_verificadas=len(bloques)+len(calendario),
                     metricas_recalculadas=True,predicciones_regeneradas=True,
                     pruebas_sin_informacion_futura=7,modelo_recargado_y_comparado=True,
                     entrenamiento_final_meses=len(historia),pronosticos_futuros=12,
                     datos_sha256=huella(BASE/"datos/ipap_bmc_mensual.csv"),
                     codigo_sha256=huella(BASE/"modelo_ipap.py"),
                     modelo_sha256=huella(BASE/"modelos/modelo_ets.pkl"),
                     python=platform.python_version(),
                     alcance="Comprobaciones locales. No acreditan versiones históricas del portal ni precisión futura.")
    (BASE/"resultados/comprobaciones.json").write_text(json.dumps(evidencia,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Comprobaciones correctas: captura, datos, fechas, predicciones, métricas y modelo.")


if __name__ == "__main__":
    main()
