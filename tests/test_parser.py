"""Pruebas del analizador sintáctico (descenso recursivo). Ejecutar: python -m unittest -v"""

import unittest
from pathlib import Path

from analizador import ErrorSintactico, Lexer, Parser

EJEMPLOS = Path(__file__).resolve().parent.parent / "ejemplos"


def analizar(fuente):
    lexer = Lexer(fuente)
    lista = list(lexer.tokens()) + [lexer.fin()]
    return Parser(lista).analizar()


def hojas(nodo):
    """Hojas del árbol sin ε: deben reconstruir la entrada (frontera del árbol)."""
    if not nodo.hijos:
        return [] if nodo.etiqueta == "ε" else [nodo.lexema]
    return [h for hijo in nodo.hijos for h in hojas(hijo)]


class TestProgramasValidos(unittest.TestCase):
    def test_ejemplo_del_enunciado(self):
        analizar("x = 10 + 5 * 2;\ny = (x - 4) / 2;\nprint y;")

    def test_programa_vacio(self):
        arbol = analizar("")
        self.assertEqual(arbol.hijos[0].hijos[0].etiqueta, "ε")

    def test_parentesis_anidados(self):
        analizar("p = ((1 + 2) * (3 - 4)) / (5);")

    def test_print_de_expresion(self):
        analizar("print (a + b) * 2;")

    def test_frontera_del_arbol_reconstruye_la_entrada(self):
        fuente = "c = a + b * 3 - 4 / 2;"
        lexemas = [t.lexema for t in Lexer(fuente).tokens()]
        self.assertEqual(hojas(analizar(fuente)), lexemas)

    def test_archivos_validos_de_ejemplo(self):
        for nombre in ("ejemplo.calc", "precedencia.calc", "parentesis.calc", "vacio.calc"):
            with self.subTest(archivo=nombre):
                analizar((EJEMPLOS / nombre).read_text(encoding="utf-8"))


class TestPrecedencia(unittest.TestCase):
    def test_multiplicacion_queda_debajo_de_la_suma(self):
        # x = 10 + 5 * 2 : el '*' debe aparecer dentro del 'termino' derecho del '+'
        sentencia = analizar("x = 10 + 5 * 2;").hijos[0].hijos[0]
        expresion = sentencia.hijos[2]
        expr_prima = expresion.hijos[1]
        self.assertEqual(expr_prima.hijos[0].etiqueta, "OP_ADD")
        termino_derecho = expr_prima.hijos[1]
        self.assertEqual(termino_derecho.hijos[1].hijos[0].etiqueta, "OP_MUL")

    def test_el_parentesis_sube_la_prioridad(self):
        # y = (x - 4) / 2 : el '-' queda dentro de un factor, debajo del '/'
        sentencia = analizar("y = (x - 4) / 2;").hijos[0].hijos[0]
        termino = sentencia.hijos[2].hijos[0]
        factor = termino.hijos[0]
        self.assertEqual(factor.hijos[0].etiqueta, "PUNCT_LPAREN")
        self.assertEqual(termino.hijos[1].hijos[0].etiqueta, "OP_DIV")


class TestErroresSintacticos(unittest.TestCase):
    def assertErrorEn(self, fuente, linea, columna, fragmento):
        with self.assertRaises(ErrorSintactico) as ctx:
            analizar(fuente)
        e = ctx.exception
        self.assertEqual((e.linea, e.columna), (linea, columna), str(e))
        self.assertIn(fragmento, e.mensaje)

    def test_falta_punto_y_coma(self):
        self.assertErrorEn("x = 10 + 5\ny = x * 2;", 1, 11, "Falta ';'")

    def test_falta_punto_y_coma_al_final_del_archivo(self):
        self.assertErrorEn("print x", 1, 8, "Falta ';'")

    def test_parentesis_sin_cerrar(self):
        self.assertErrorEn("y = (x - 4 / 2;", 1, 15, "falta ')'")

    def test_parentesis_sobrante(self):
        self.assertErrorEn("y = x - 4) / 2;", 1, 10, "sin un '('")

    def test_dos_operadores_seguidos(self):
        self.assertErrorEn("x = 5 + * 3;", 1, 9, "Se esperaba un número")

    def test_falta_igual(self):
        self.assertErrorEn("x 5;", 1, 3, "Se esperaba '='")

    def test_expresion_vacia(self):
        self.assertErrorEn("x = ;", 1, 5, "Se esperaba un número")

    def test_sentencia_que_empieza_con_numero(self):
        self.assertErrorEn("5 = x;", 1, 1, "inicio de una sentencia")

    def test_parentesis_vacios(self):
        self.assertErrorEn("x = ();", 1, 6, "Se esperaba un número")

    def test_dos_identificadores_seguidos(self):
        self.assertErrorEn("x = a b;", 1, 6, "Falta ';'")


if __name__ == "__main__":
    unittest.main()
