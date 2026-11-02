from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

BASE = Path(__file__).resolve().parents[1]
OMITIR = {'.git','.venv','__pycache__','.ipynb_checkpoints','.DS_Store'}


def main():
    archivos=[]
    for ruta in sorted(BASE.rglob('*')):
        relativa=ruta.relative_to(BASE)
        if not ruta.is_file() or OMITIR.intersection(relativa.parts):continue
        if relativa.as_posix()=='MANIFIESTO.json':continue
        contenido=ruta.read_bytes()
        archivos.append(dict(ruta=relativa.as_posix(),bytes=len(contenido),
                             sha256=hashlib.sha256(contenido).hexdigest()))
    manifiesto=dict(proyecto='Pronóstico IPAP BMC, PUJ Cali',
                     preparado_utc=datetime.now(timezone.utc).isoformat(),archivos=archivos)
    (BASE/'MANIFIESTO.json').write_text(json.dumps(manifiesto,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Manifiesto generado: {len(archivos)} archivos.')


if __name__=='__main__':
    main()
