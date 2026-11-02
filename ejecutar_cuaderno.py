"""Ejecuta el cuaderno con el Python actual y un kernel temporal, sin instalación global."""
import json
import os
import sys
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

BASE = Path(__file__).resolve().parent


def main():
    cuaderno = nbformat.read(BASE / "Proyecto_IPAP.ipynb", as_version=4)
    os.environ.setdefault("IPYTHONDIR", str(Path(tempfile.gettempdir()) / "ipap-bmc-ipython"))
    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "ipap-bmc-matplotlib"))
    with tempfile.TemporaryDirectory(prefix="ipap-bmc-kernel-") as temporal:
        carpeta = Path(temporal) / "ipap-bmc"
        carpeta.mkdir()
        (carpeta / "kernel.json").write_text(json.dumps(dict(
            argv=[sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            display_name="IPAP BMC", language="python")), encoding="utf-8")
        gestor = KernelManager(kernel_name="ipap-bmc",
                               kernel_spec_manager=KernelSpecManager(kernel_dirs=[temporal]))
        cliente = NotebookClient(cuaderno, km=gestor, timeout=180,
                                  resources={"metadata": {"path": str(BASE)}}, allow_errors=False)
        cliente.execute(cleanup_kc=True)
    celdas = [c for c in cuaderno.cells if c.cell_type == "code"]
    assert all(c.execution_count is not None for c in celdas)
    assert not any(o.output_type == "error" for c in celdas for o in c.outputs)
    nbformat.write(cuaderno, BASE / "Proyecto_IPAP_ejecutado.ipynb")
    from modelo_ipap import huella
    evidencia = dict(celdas_codigo=len(celdas), errores=0, python=sys.version.split()[0],
                     fuente_sha256=huella(BASE / "Proyecto_IPAP.ipynb"),
                     ejecutado_sha256=huella(BASE / "Proyecto_IPAP_ejecutado.ipynb"),
                     modelo_sha256=huella(BASE / "modelos/modelo_ets.pkl"))
    (BASE / "resultados/comprobacion_cuaderno.json").write_text(
        json.dumps(evidencia, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Cuaderno ejecutado: {len(celdas)} celdas de código, cero errores.")


if __name__ == "__main__":
    main()
