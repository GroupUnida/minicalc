#!/usr/bin/env python3
"""
Mini-Calc — Compilador minimalista (analizador léxico + sintáctico).

Uso:
    python minicalc.py <archivo.calc> [--arbol] [--dot ARCHIVO.dot] [--log ARCHIVO.log]

    --arbol   muestra el árbol de derivación si el análisis es exitoso
    --dot     exporta el árbol de derivación a Graphviz (.dot)
    --log     además de la consola, guarda la salida en un archivo de log

Código de salida: 0 = sin errores, 1 = error léxico/sintáctico, 2 = error de uso.
Sólo usa la biblioteca estándar de Python (sin generadores de lexers/parsers).
"""

import argparse
import sys
from pathlib import Path

from analizador import ErrorCompilacion, Lexer, Parser


class Salida:
    """Escribe en consola y, opcionalmente, en un archivo de log."""

    def __init__(self, ruta_log=None):
        self.archivo = open(ruta_log, "w", encoding="utf-8") if ruta_log else None

    def __call__(self, texto=""):
        print(texto)
        if self.archivo:
            self.archivo.write(texto + "\n")

    def cerrar(self):
        if self.archivo:
            self.archivo.close()


def compilar(ruta: Path, salida: Salida, mostrar_arbol=False, ruta_dot=None) -> int:
    fuente = ruta.read_text(encoding="utf-8-sig")  # utf-8-sig tolera el BOM del Bloc de notas

    # ---------------- Fase 1: análisis léxico ----------------
    salida("=== INICIO DE ANÁLISIS LÉXICO ===")
    lexer = Lexer(fuente)
    lista_tokens = []
    try:
        for tok in lexer.tokens():
            salida(str(tok))
            lista_tokens.append(tok)
    except ErrorCompilacion as e:
        salida(str(e))
        salida("Análisis detenido por error léxico.")
        return 1
    lista_tokens.append(lexer.fin())

    # ---------------- Fase 2: análisis sintáctico ----------------
    salida()
    salida("=== INICIO DE ANÁLISIS SINTÁCTICO ===")
    try:
        arbol = Parser(lista_tokens).analizar()
    except ErrorCompilacion as e:
        salida(str(e))
        salida("Análisis detenido por error sintáctico.")
        return 1
    salida("El análisis sintáctico finalizó exitosamente sin errores.")

    if mostrar_arbol:
        salida()
        salida("=== ÁRBOL DE DERIVACIÓN ===")
        salida(arbol.dibujar())
    if ruta_dot:
        Path(ruta_dot).write_text(arbol.a_dot(), encoding="utf-8")
        salida(f"Árbol exportado a {ruta_dot}")
    return 0


def main(argv=None) -> int:
    # Para que los acentos se vean bien en la consola de Windows
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="Compilador minimalista para Mini-Calc")
    ap.add_argument("archivo", help="archivo fuente con extensión .calc")
    ap.add_argument("--arbol", action="store_true", help="mostrar el árbol de derivación")
    ap.add_argument("--dot", metavar="ARCHIVO", help="exportar el árbol a Graphviz")
    ap.add_argument("--log", metavar="ARCHIVO", help="guardar la salida en un archivo de log")
    args = ap.parse_args(argv)

    ruta = Path(args.archivo)
    if ruta.suffix.lower() != ".calc":
        print(f"Error: el archivo de entrada debe tener extensión .calc ({ruta.name})",
              file=sys.stderr)
        return 2
    if not ruta.is_file():
        print(f"Error: no se encontró el archivo '{ruta}'", file=sys.stderr)
        return 2

    salida = Salida(args.log)
    try:
        return compilar(ruta, salida, args.arbol, args.dot)
    finally:
        salida.cerrar()


if __name__ == "__main__":
    sys.exit(main())
