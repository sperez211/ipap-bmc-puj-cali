from pathlib import Path
from functools import lru_cache
import sys
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

SOURCE = Path(__file__).resolve().parents[1]
OUT = SOURCE/'experimentos'
sys.path.insert(0, str(SOURCE))
from modelo_ipap import cargar_datos

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
 model=ExponentialSmoothing(values,trend=s['trend'],damped_trend=s['damped'],seasonal=s['seasonal'],
                            seasonal_periods=12 if s['seasonal'] else None,
                            initialization_method='estimated').fit()
 predicted=np.asarray(model.forecast(12))
 if s.get('logarithm'):predicted=np.exp(predicted)
 ok=bool(model.mle_retvals.success) and bool(np.isfinite(predicted).all())
 return predicted,ok

def internal_origins(origin):
 valid=[p for p in pd.period_range(series.index[0],origin-12,freq='M')
        if p.month==9 and len(series.loc[:p])>=60]
 return valid[-4:]

predictions=[]
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
  if all(oks):rankings.append(item)
 selected=min(rankings,key=lambda r:(r['RMSE'],r['MAE'],r['modelo']))['modelo']
 chosen,ok=forecast(selected,origin)
 fallback=None
 if not ok:fallback=selected;selected='ETS_historia_completa';chosen,ok=forecast(selected,origin)
 assert ok
 if fallback:print(f'Corte {origin}: {fallback} no convergió; se usa {selected}.',flush=True)
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
summary.to_csv(OUT/'comparacion.csv',index=False)
original=pd.read_csv(SOURCE/'resultados/predicciones_6_cortes.csv')
new=frame[frame.modelo=='ETS_120_meses'].sort_values(['origen','horizonte'])
old=original[original.modelo=='ETS_120_meses'].sort_values(['origen','horizonte'])
np.testing.assert_allclose(new.prediccion,old.prediccion,rtol=1e-10,atol=1e-10)
assert len(new)==72 and frame.groupby('modelo').size().eq(72).all()
print(summary.round(4).to_string(index=False),flush=True)
print('Directorio de pruebas:',OUT,flush=True)
