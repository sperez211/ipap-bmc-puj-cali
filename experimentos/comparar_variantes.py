from pathlib import Path
from functools import lru_cache
from datetime import datetime, timezone
import json
import warnings
import sys
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

SOURCE = Path(__file__).resolve().parents[1]
OUT = SOURCE/'experimentos/resultados'
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0, str(SOURCE))
from modelo_ipap import cargar_datos, huella

series = cargar_datos()
outer = [pd.Period(f'{year}-09', 'M') for year in range(2020, 2026)]
specs = {
 'ETS_historia_completa': dict(trend='add', damped=True, seasonal='add'),
 'ETS_sin_amortiguar': dict(trend='add', damped=False, seasonal='add'),
 'ETS_sin_tendencia': dict(trend=None, damped=False, seasonal='add'),
 'ETS_sin_estacionalidad': dict(trend='add', damped=True, seasonal=None),
 'Holt_lineal': dict(trend='add', damped=False, seasonal=None),
 'Suavizamiento_simple': dict(trend=None, damped=False, seasonal=None),
 'ETS_estacionalidad_multiplicativa': dict(trend='add', damped=True, seasonal='mul'),
 'ETS_logaritmos': dict(trend='add', damped=True, seasonal='add', logarithm=True),
 'ETS_60_meses': dict(trend='add', damped=True, seasonal='add', window=60),
 'ETS_120_meses': dict(trend='add', damped=True, seasonal='add', window=120),
}
mixtures = {'ETS_deriva_25': .25, 'ETS_deriva_50': .50, 'ETS_deriva_75': .75}
baselines = ['Ultimo_valor', 'Mismo_mes_anio_anterior', 'Deriva_12']
names = list(specs) + list(mixtures) + baselines
eligible = list(specs) + list(mixtures) + ['Deriva_12']
protocol = dict(
 fecha=datetime.now(timezone.utc).isoformat(), datos_sha256=huella(SOURCE/'datos/ipap_bmc_mensual.csv'),
 origenes=list(map(str,outer)), horizonte=12, especificaciones=specs, mezclas_peso_ETS=mixtures,
 seleccion='RMSE agrupado en los últimos cuatro cortes anuales internos completos; desempate MAE y nombre.',
 corte_interno='Septiembre, al menos 60 meses de historia, doce objetivos que terminan como máximo en el corte exterior.',
 fallos='Una variante solo puede seleccionarse si sus cuatro ajustes internos convergen y sus pronósticos son finitos. Si el ajuste exterior seleccionado falla se usa ETS_historia_completa y se registra.',
 alcance='Exploración retrospectiva sobre períodos reutilizados. No constituye una nueva prueba independiente. Las alternativas son material complementario. El modelo del proyecto usa una ventana fija de hasta 120 meses.',
)
(OUT/'protocolo.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2))
diagnostics=[]

def scores(actual, forecast):
 error=np.asarray(actual)-np.asarray(forecast)
 return dict(RMSE=float(np.sqrt(np.mean(error**2))), MAE=float(np.mean(abs(error))),
             MAPE=float(100*np.mean(abs(error/np.asarray(actual)))), n=len(error))

@lru_cache(None)
def forecast(name, origin):
 history=series.loc[:origin]
 if name=='Ultimo_valor':return np.repeat(history.iloc[-1],12),True
 if name=='Mismo_mes_anio_anterior':return history.iloc[-12:].to_numpy(),True
 drift=history.iloc[-1]+np.arange(1,13)*(history.iloc[-1]-history.iloc[-13])/12
 if name=='Deriva_12':return drift,True
 if name in mixtures:
  values,ok=forecast('ETS_historia_completa',origin)
  return mixtures[name]*values+(1-mixtures[name])*drift,ok
 s=specs[name]
 if 'window' in s:history=history.iloc[-s['window']:]
 values=np.log(history.to_numpy()) if s.get('logarithm') else history.to_numpy()
 with warnings.catch_warnings(record=True) as captured:
  warnings.simplefilter('always')
  model=ExponentialSmoothing(values,trend=s['trend'],damped_trend=s['damped'],seasonal=s['seasonal'],
                            seasonal_periods=12 if s['seasonal'] else None,
                            initialization_method='estimated').fit()
  predicted=np.asarray(model.forecast(12))
  if s.get('logarithm'):predicted=np.exp(predicted)
 ok=bool(model.mle_retvals.success) and bool(np.isfinite(predicted).all())
 diagnostics.append(dict(modelo=name,origen=str(origin),entrenamiento=len(history),convergio=ok,
                         avisos=[str(w.message) for w in captured]))
 return predicted,ok

def internal_origins(origin):
 valid=[p for p in pd.period_range(series.index[0],origin-12,freq='M')
        if p.month==9 and len(series.loc[:p])>=60]
 return valid[-4:]

predictions=[]
selection=[]
internal_scores=[]
for origin in outer:
 inner=internal_origins(origin)
 assert len(inner)==4
 rankings=[]
 for name in eligible:
  y=[];p=[];oks=[]
  for cut in inner:
   dates=pd.period_range(cut+1,periods=12,freq='M')
   assert dates[-1]<=origin
   predicted,ok=forecast(name,cut)
   y.extend(series.loc[dates].to_numpy());p.extend(predicted);oks.append(ok)
  item=dict(origen_exterior=str(origin),modelo=name,convergio=all(oks),
            origenes_internos=','.join(map(str,inner)),**scores(y,p))
  internal_scores.append(item)
  if all(oks):rankings.append(item)
 selected=min(rankings,key=lambda r:(r['RMSE'],r['MAE'],r['modelo']))['modelo']
 chosen,ok=forecast(selected,origin)
 fallback=None
 if not ok:fallback=selected;selected='ETS_historia_completa';chosen,ok=forecast(selected,origin)
 assert ok
 selection.append(dict(origen=str(origin),seleccionado=selected,fallback_desde=fallback,
                       inicio_validacion=str(inner[0]+1),fin_validacion=str(inner[-1]+12)))
 dates=pd.period_range(origin+1,periods=12,freq='M')
 for name in names+['Seleccion_interna']:
  predicted,ok=(chosen,True) if name=='Seleccion_interna' else forecast(name,origin)
  for h,date in enumerate(dates,1):
   predictions.append(dict(modelo=name,origen=str(origin),fecha=str(date),horizonte=h,
                           prediccion=float(predicted[h-1]),real=float(series.loc[date]),convergio=ok))
 print(f'Corte {origin}: selección interna {selected}',flush=True)

frame=pd.DataFrame(predictions)
summary=pd.DataFrame([dict(modelo=name,**scores(g.real,g.prediccion),
                           ajustes_convergieron=bool(g.convergio.all())) for name,g in frame.groupby('modelo')])
reference=summary.set_index('modelo').loc['ETS_historia_completa','RMSE']
summary['mejora_RMSE_frente_historia_completa_pct']=100*(1-summary.RMSE/reference)
summary=summary.sort_values('RMSE')
per_origin=pd.DataFrame([dict(modelo=name,origen=origin,**scores(g.real,g.prediccion))
                        for (name,origin),g in frame.groupby(['modelo','origen'])])
for name,table in [('comparacion',summary),('predicciones',frame),('metricas_por_origen',per_origin),
                   ('seleccion_por_origen',pd.DataFrame(selection)),('validacion_interna',pd.DataFrame(internal_scores))]:
 table.to_csv(OUT/f'{name}.csv',index=False)
(OUT/'diagnosticos.json').write_text(json.dumps(diagnostics,ensure_ascii=False,indent=2))
original=pd.read_csv(SOURCE/'resultados/predicciones_6_cortes.csv')
new=frame[frame.modelo=='ETS_120_meses'].sort_values(['origen','horizonte'])
old=original[original.modelo=='ETS_120_meses'].sort_values(['origen','horizonte'])
np.testing.assert_allclose(new.prediccion,old.prediccion,rtol=1e-10,atol=1e-10)
assert len(new)==72 and frame.groupby('modelo').size().eq(72).all()
print(summary.round(4).to_string(index=False),flush=True)
print('Directorio de pruebas:',OUT,flush=True)
