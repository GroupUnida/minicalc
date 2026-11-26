#!/usr/bin/env sh
# Ejecuta Mini-Calc con todos los archivos de ejemplo y luego las pruebas automáticas.
# Uso: sh probar_todo.sh
cd "$(dirname "$0")" || exit 1
PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

for f in ejemplos/*.calc; do
    echo
    echo "==================== $f ===================="
    "$PY" minicalc.py "$f"
done

echo
echo "==================== PRUEBAS AUTOMÁTICAS ===================="
"$PY" -m unittest -v
