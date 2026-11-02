from pathlib import Path
import ast
import csv
import json
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

BASE = Path(__file__).resolve().parents[1]


def leer_csv(nombre):
    with (BASE/nombre).open(encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def numero(valor, decimales=2):
    return f"{float(valor):.{decimales}f}".replace(".", ",")


datos = leer_csv("datos/ipap_bmc_mensual.csv")
serie = {r["fecha"]: float(r["valor"]) for r in datos}
metricas = {r["modelo"]: r for r in leer_csv("resultados/metricas_6_cortes.csv")}
calendario = {r["modelo"]: r for r in leer_csv("resultados/metricas_2025.csv")}
futuro = leer_csv("resultados/pronostico_12_meses.csv")
por_corte = [r for r in leer_csv("resultados/metricas_por_corte.csv") if r["modelo"]=="ETS_120_meses"]
por_h = [r for r in leer_csv("resultados/metricas_por_horizonte.csv") if r["modelo"]=="ETS_120_meses"]
ficha = json.loads((BASE/"modelos/ficha_modelo.json").read_text(encoding="utf-8"))
control = json.loads((BASE/"resultados/comprobaciones.json").read_text(encoding="utf-8"))
assert len(datos)==189 and ficha["observaciones_entrenamiento"]==120
assert control["predicciones_historicas_verificadas"]==336

principal = metricas["ETS_120_meses"]
peor = max(por_corte,key=lambda r:float(r["RMSE"]))
plantilla = dict(rmse=numero(principal["RMSE"]), mae=numero(principal["MAE"]), mape=numero(principal["MAPE"]),
                rmse_ultimo=numero(metricas["Naive"]["RMSE"]), rmse_deriva=numero(metricas["Deriva12"]["RMSE"]),
                mejora_ultimo=numero(100*(1-float(principal["RMSE"])/float(metricas["Naive"]["RMSE"])),1),
                mejora_deriva=numero(100*(1-float(principal["RMSE"])/float(metricas["Deriva12"]["RMSE"])),1),
                rmse_2025=numero(calendario["ETS_120_meses"]["RMSE"]),
                rmse_deriva_2025=numero(calendario["Deriva12"]["RMSE"]),
                primero_futuro=numero(futuro[0]["prediccion"]), ultimo_futuro=numero(futuro[-1]["prediccion"]),
                h1=numero(next(r["RMSE"] for r in por_h if r["horizonte"]=="1")),
                h12=numero(next(r["RMSE"] for r in por_h if r["horizonte"]=="12")),
                peor_corte=peor["origen"], peor_rmse=numero(peor["RMSE"]),
                nivel=numero(ficha["parametros"]["smoothing_level"],4),
                tendencia=numero(ficha["parametros"]["smoothing_trend"],4),
                estacional=numero(ficha["parametros"]["smoothing_seasonal"],4),
                amortiguacion=numero(ficha["parametros"]["damping_trend"],4),
                dic2024=numero(serie["2024-12"]), dic2023=numero(serie["2023-12"]),
                paso_deriva=numero((serie["2024-12"]-serie["2023-12"])/12,4),
                deriva_enero=numero(serie["2024-12"]+(serie["2024-12"]-serie["2023-12"])/12))
NOMBRES = {"ETS_120_meses":"ETS hasta 120 meses","Naive":"Último valor", "Naive12":"Mismo mes del año anterior", "Deriva12":"Deriva de doce meses"}


def nuevo_documento(titulo):
    d=Document()
    s=d.sections[0]
    s.page_width=Inches(8.5);s.page_height=Inches(11)
    s.top_margin=Inches(.75);s.bottom_margin=Inches(.7)
    s.left_margin=Inches(.78);s.right_margin=Inches(.78);s.footer_distance=Inches(.28)
    for border in list(d.styles.element.xpath('//w:pBdr')):border.getparent().remove(border)
    for style in d.styles:
        if not hasattr(style,'font'):continue
        style.font.name="Arial";style.font.color.rgb=RGBColor(0,0,0)
        style.font.italic=False;style.font.underline=False;style.font.bold=False
        rp=style.element.get_or_add_rPr()
        for tag in ['spacing','position','caps','smallCaps','shadow','outline','emboss','imprint']:
            for element in list(rp.findall(qn('w:'+tag))):rp.remove(element)
        rf=rp.find(qn('w:rFonts'))
        if rf is not None:
            rf.attrib.clear()
            for key in ['ascii','hAnsi','cs','eastAsia']:rf.set(qn('w:'+key),'Arial')
    for name,size,bold in [('Normal',11,False),('Title',17,True),('Subtitle',11,False),
                          ('Heading 1',12,True),('Heading 2',11,True),('Caption',10,False)]:
        st=d.styles[name];st.font.size=Pt(size);st.font.bold=bold
        st.paragraph_format.line_spacing=1.08
        st.paragraph_format.space_before=Pt(8 if 'Heading' in name else 0)
        st.paragraph_format.space_after=Pt(5)
        st.paragraph_format.keep_with_next=name in ['Title','Subtitle','Heading 1','Heading 2']
        st.paragraph_format.widow_control=True
    code=d.styles.add_style('Codigo',1)
    code.base_style=d.styles['Normal'];code.font.size=Pt(9.5)
    code.paragraph_format.left_indent=Inches(.12);code.paragraph_format.line_spacing=1.0
    code.paragraph_format.keep_together=True
    footer=s.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    d.core_properties.title=titulo
    d.core_properties.author='Santiago Pérez; Santiago Zambrano; Martín Bastidas'
    return d


def texto(d,texto,estilo=None):
    p=d.add_paragraph(style=estilo)
    if texto.startswith('modelo_ipap.py, línea'):
        p.paragraph_format.keep_with_next=True
    if texto.startswith('El repositorio reúne datos, captura, código'):
        p.paragraph_format.keep_together=True
    texto=texto.replace('`','')
    position=0
    for match in re.finditer(r'\[([^\]]+)\]\((https?://[^)]+)\)',texto):
        p.add_run(texto[position:match.start()])
        link=OxmlElement('w:hyperlink')
        link.set(qn('r:id'),p.part.relate_to(match[2],RT.HYPERLINK,is_external=True))
        run=OxmlElement('w:r');pr=OxmlElement('w:rPr')
        color=OxmlElement('w:color');color.set(qn('w:val'),'000000');pr.append(color)
        for tag,value in [('rFonts','Arial'),('sz','22')]:
            e=OxmlElement('w:'+tag)
            if tag=='rFonts':e.set(qn('w:ascii'),value);e.set(qn('w:hAnsi'),value)
            else:e.set(qn('w:val'),value)
            pr.append(e)
        run.append(pr);t=OxmlElement('w:t');t.text=match[1];run.append(t);link.append(run);p._p.append(link)
        position=match.end()
    p.add_run(texto[position:])
    return p


def tabla(d,headers,rows,widths,padding='75',juntas=False):
    t=d.add_table(rows=1,cols=len(headers));t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for col,w in zip(t.columns,widths):col.width=Inches(w)
    for c,value in zip(t.rows[0].cells,headers):c.text=str(value)
    for values in rows:
        for c,value in zip(t.add_row().cells,values):c.text=str(value)
    borders=OxmlElement('w:tblBorders')
    for side in ['top','bottom','left','right','insideH','insideV']:
        e=OxmlElement('w:'+side)
        for k,v in [('val','single'),('sz','4'),('color','A0A0A0')]:e.set(qn('w:'+k),v)
        borders.append(e)
    t._tbl.tblPr.append(borders)
    for i,row in enumerate(t.rows):
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        if i==0:row._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
        for j,c in enumerate(row.cells):
            c.width=Inches(widths[j]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            mar=OxmlElement('w:tcMar')
            for side,value in [('top',padding),('bottom',padding),('left','90'),('right','90')]:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),value);e.set(qn('w:type'),'dxa');mar.append(e)
            c._tc.get_or_add_tcPr().append(mar)
            for p in c.paragraphs:
                p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.03
                p.alignment=WD_ALIGN_PARAGRAPH.LEFT if j==0 else WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:r.font.size=Pt(10);r.font.bold=i==0;r.font.color.rgb=RGBColor(0,0,0)
                if juntas and i<len(t.rows)-1:p.paragraph_format.keep_with_next=True
    d.add_paragraph().paragraph_format.space_after=Pt(0)


def insertar(d,linea):
    if linea=='@identidad':
        for t in ['Equipo PUJ Cali, Pontificia Universidad Javeriana Cali',
                  'Santiago Pérez, Santiago Zambrano y Martín Bastidas',
                  'BMC DataLab Challenge 2026, Reto B. 1 de noviembre de 2026']:
            p=texto(d,t);p.paragraph_format.space_after=Pt(3)
            for r in p.runs:r.font.size=Pt(10.5)
    elif linea in ['@metricas','@metricas_2025']:
        source=metricas if linea=='@metricas' else calendario
        encabezado='Método en 2025' if linea=='@metricas_2025' else 'Método'
        tabla(d,[encabezado,'RMSE','MAE','MAPE (%)'],[[NOMBRES[k]]+[numero(source[k][m]) for m in ['RMSE','MAE','MAPE']]
              for k in ['ETS_120_meses','Deriva12','Naive','Naive12']],[3.55,1.05,1.05,1.2])
    elif linea=='@cortes':
        rows=[]
        for y in range(2020,2026):
            end=f'{y}-09';history=[r['fecha'] for r in datos if r['fecha']<=end][-120:]
            rows.append([end,history[0]+' a '+history[-1],len(history),f'Oct {y} a sep {y+1}'])
        tabla(d,['Corte','Entrenamiento','Meses','Evaluación'],rows,[1,2.15,.75,2.95],juntas=True)
    elif linea=='@pronostico':
        tabla(d,['Mes pronosticado','Puntos del índice'],[[r['fecha'],numero(r['prediccion'])] for r in futuro],[3.5,3.35],padding='45')
    elif linea.startswith('@figura '):
        name,caption=linea[len('@figura '):].split('|',1)
        p=d.add_paragraph();p.paragraph_format.keep_with_next=True
        shape=p.add_run().add_picture(str(BASE/'resultados'/name),width=Inches(6.8))
        shape._inline.docPr.set('descr',caption)
        texto(d,caption,'Caption')
    elif linea=='@variantes':
        table=leer_csv('experimentos/resultados/comparacion.csv')
        nombres={'Ultimo_valor':'Último valor','Mismo_mes_anio_anterior':'Mismo mes del año anterior','Seleccion_interna':'Selección interna'}
        tabla(d,['Configuración','RMSE','MAE','MAPE (%)'],[[nombres.get(r['modelo'],r['modelo'].replace('_',' '))]+[numero(r[k]) for k in ['RMSE','MAE','MAPE']] for r in table],[3.55,1.05,1.05,1.2])
    elif linea=='@codigo':
        explicar_codigo(d)
    else:raise ValueError('Marcador desconocido: '+linea)


def explicar_codigo(d):
    source=(BASE/'modelo_ipap.py').read_text(encoding='utf-8')
    lines=source.splitlines();nodes={n.name:n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
    segments=[
      ('huella','Identificar un archivo','Calcula SHA256, una huella del contenido. Si cambia un byte, normalmente cambia la huella. Sirve para detectar una sustitución del archivo; por sí sola no demuestra que el productor haya publicado esos datos.'),
      ('cargar_datos','Leer y comprobar la serie','Abre el CSV y su registro de procedencia. Convierte los meses a períodos mensuales y los niveles a números. Ordena las fechas y rechaza duplicados, huecos, valores no finitos o no positivos. No corrige ni rellena datos. El resultado es una Series de pandas, una columna de valores identificada por mes.'),
      ('entrenar','Ajustar el modelo','Recibe la historia anterior al corte y toma sus últimos 120 meses, o todos si hay menos. La llamada fit estima el nivel, la tendencia, el patrón anual y los parámetros de suavizamiento. Comprueba la convergencia del optimizador. Convergencia significa que el cálculo encontró una solución numérica, no que el pronóstico vaya a acertar.'),
      ('pronosticar','Asignar los doce meses futuros','Llama a entrenar y pide forecast(12). Construye las doce fechas posteriores al último mes disponible y verifica que existan doce números finitos. La función no recibe los valores reales futuros.'),
      ('evaluar','Comparar los cuatro métodos','Recorre las fechas de corte. Separa historia y doce valores reales posteriores. Genera ETS, último valor, repetición anual y deriva con la misma historia. Después une predicción y real en filas. Los reales intervienen al calcular el error, no en el ajuste de ese corte.'),
      ('metricas','Resumir los errores','Agrupa por método, por corte o por horizonte. Resta predicción a real y calcula RMSE, MAE, MAPE y número de filas. Para el resultado agrupado se usan los 72 errores de cada método, en vez de promediar seis RMSE anuales.'),
      ('guardar_modelo','Conservar el ajuste final','Entrena con los últimos 120 meses y reúne el ajuste, la historia utilizada y una ficha. La ficha distingue 189 observaciones del CSV de 120 meses de entrenamiento y registra fechas, configuración, versiones y huella. Guarda el paquete en PKL y la ficha legible en JSON.'),
      ('cargar_modelo','Recuperar el archivo entrenado','Lee el PKL del proyecto y comprueba su nombre de modelo. No estima parámetros otra vez. Un PKL es un archivo para el programa, no una tabla que se abra con doble clic.'),
      ('pronostico_guardado','Usar el ajuste sin reentrenar','Pide doce meses al modelo cargado, crea sus fechas y arma una tabla marcada como pronostico_del_modelo. No agrega una columna de reales inventados ni introduce estas predicciones en el CSV oficial.'),
      ('preparar_graficos','Fijar el aspecto de los gráficos','Configura Matplotlib para guardar imágenes y utiliza letra negra y una fuente común. Las líneas se diferencian con trazos y marcadores. La presentación no cambia las predicciones.'),
      ('graficar','Dibujar las cinco figuras','Recibe la serie, las predicciones históricas, el caso de 2025 y el futuro. Guarda historia, comparación anual, RMSE por corte, RMSE por horizonte y proyección. Los datos se dibujan desde las mismas tablas de la evaluación; no se escriben números a mano para los gráficos.'),
      ('tabla_markdown','Dar formato a una tabla de lectura','Convierte las tablas de métricas en texto con columnas para el archivo de resultados. Redondea lo mostrado a dos decimales. Los CSV mantienen más precisión y el redondeo no se utiliza para calcular errores.'),
      ('escribir_resultados','Explicar las salidas','Toma las métricas calculadas y produce LEER_RESULTADOS.md. Describe los períodos, la comparación con el último valor, el entrenamiento final y las limitaciones. Los valores del texto se obtienen de las tablas.'),
      ('main','Ejecutar el recorrido completo','Organiza las etapas: cargar datos, evaluar seis cortes y 2025, exportar tablas, entrenar y guardar el ajuste final, recargarlo, pronosticar, graficar y escribir los resultados. El bloque if __name__ == "__main__" llama a esta función cuando se ejecuta el archivo directamente.'),
    ]
    for name,title,description in segments:
        texto(d,title,'Heading 2');texto(d,description)
        n=nodes[name];excerpt=lines[n.lineno-1:min(n.lineno+4,n.end_lineno)]
        texto(d,f'modelo_ipap.py, línea {n.lineno}.','Caption')
        texto(d,'\n'.join(excerpt),'Codigo')


def construir(nombre_plantilla,nombre_salida):
    template=(BASE/'documentacion'/nombre_plantilla).read_text(encoding='utf-8')
    for key,value in plantilla.items():template=template.replace('{{'+key+'}}',str(value))
    assert not re.search(r'\{\{[a-z_]+\}\}',template), 'Variable sin resolver'
    d=nuevo_documento(template.splitlines()[0].lstrip('# '))
    buffer=[];code=[];inside=False
    def flush():
        if buffer:texto(d,' '.join(buffer));buffer.clear()
    for line in template.splitlines()+['']:
        if line.startswith('```'):
            flush()
            if inside:texto(d,'\n'.join(code),'Codigo');code.clear()
            inside=not inside;continue
        if inside:code.append(line);continue
        if not line.strip():flush();continue
        if line.startswith('@'):flush();insertar(d,line);continue
        if line.startswith('### '):flush();texto(d,line[4:],'Heading 2');continue
        if line.startswith('## '):flush();texto(d,line[3:],'Heading 1');continue
        if line.startswith('# '):flush();texto(d,line[2:],'Title');continue
        buffer.append(line)
    d.save(BASE/nombre_salida)
    print(nombre_salida)


if __name__=='__main__':
    construir('contenido_informe.md','Informe_tecnico_PUJ_Cali.docx')
    construir('contenido_guia.md','Guia_del_proyecto_PUJ_Cali.docx')
