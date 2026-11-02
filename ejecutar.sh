#!/bin/sh
set -eu
IPAP_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ ! -x "$IPAP_DIR/.venv/bin/python" ]; then
    echo "Primero crea .venv e instala requirements.txt. Los pasos están en el README."
    exit 1
fi
export MPLCONFIGDIR="${TMPDIR:-/tmp}/ipap-matplotlib"
export PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/ipap-pycache"
"$IPAP_DIR/.venv/bin/python" "$IPAP_DIR/modelo_ipap.py"
"$IPAP_DIR/.venv/bin/python" "$IPAP_DIR/comprobar.py"
