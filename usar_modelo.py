from modelo_ipap import BASE, cargar_modelo, huella, pronostico_guardado


def main():
    paquete = cargar_modelo()
    ficha = paquete["ficha"]
    if huella(BASE/"datos/ipap_bmc_mensual.csv") != ficha["datos_sha256"]:
        raise ValueError("Los datos no coinciden con los del modelo guardado.")
    futuro = pronostico_guardado(paquete)
    (BASE/"resultados").mkdir(exist_ok=True)
    futuro.to_csv(BASE/"resultados/pronostico_12_meses.csv",index=False)
    print(f"Modelo entrenado con {ficha['observaciones_entrenamiento']} meses, hasta {ficha['fin_entrenamiento']}.")
    print("Estimaciones del modelo en puntos del índice. No son observaciones oficiales.")
    print(futuro[["fecha","horizonte","prediccion"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
