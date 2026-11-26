"""Pruebas del analizador léxico (AFD). Ejecutar: python -m unittest -v"""

import unittest

from analizador import ErrorLexico, Lexer
from analizador import lexer as L


def tipos(fuente):
    return [t.tipo for t in Lexer(fuente).tokens()]


class TestTablaDeTransicion(unittest.TestCase):
    def test_cada_estado_tiene_fila(self):
        self.assertEqual(set(L.DELTA), set(L.ESTADOS))

    def test_estados_de_no_aceptacion(self):
        # q0 (inicial), q3-q5 (prefijos de 'print') y q7 (palabra inválida)
        no_aceptacion = set(L.ESTADOS) - set(L.ACEPTACION)
        self.assertEqual(no_aceptacion, {L.Q0, L.Q3, L.Q4, L.Q5, L.Q7})


class TestTokensValidos(unittest.TestCase):
    def test_ejemplo_del_enunciado(self):
        toks = list(Lexer("x = 10 + 5 * 2;").tokens())
        self.assertEqual([str(t) for t in toks], [
            '<ID, "x", 1, 1>', '<OP_ASSIGN, "=", 1, 3>', '<NUM, "10", 1, 5>',
            '<OP_ADD, "+", 1, 8>', '<NUM, "5", 1, 10>', '<OP_MUL, "*", 1, 12>',
            '<NUM, "2", 1, 14>', '<PUNCT_SEMI, ";", 1, 15>',
        ])

    def test_todos_los_operadores_y_delimitadores(self):
        self.assertEqual(tipos("= + - * / ( ) ;"), [
            "OP_ASSIGN", "OP_ADD", "OP_SUB", "OP_MUL", "OP_DIV",
            "PUNCT_LPAREN", "PUNCT_RPAREN", "PUNCT_SEMI"])

    def test_palabra_reservada_print(self):
        self.assertEqual(tipos("print x;"), ["KW_PRINT", "ID", "PUNCT_SEMI"])

    def test_p_sola_es_identificador(self):
        self.assertEqual(tipos("p = 1;"), ["ID", "OP_ASSIGN", "NUM", "PUNCT_SEMI"])

    def test_letras_de_print_son_identificadores(self):
        self.assertEqual(tipos("r i n t"), ["ID"] * 4)

    def test_numero_de_varios_digitos(self):
        toks = list(Lexer("1234567890").tokens())
        self.assertEqual((toks[0].tipo, toks[0].lexema), ("NUM", "1234567890"))

    def test_sin_espacios(self):
        self.assertEqual(tipos("x=(a+1)*b;"), [
            "ID", "OP_ASSIGN", "PUNCT_LPAREN", "ID", "OP_ADD", "NUM",
            "PUNCT_RPAREN", "OP_MUL", "ID", "PUNCT_SEMI"])

    def test_espacios_tabs_y_saltos_ignorados_con_posicion(self):
        toks = list(Lexer("\n\n\t  x\r\n  =").tokens())
        self.assertEqual((toks[0].linea, toks[0].columna), (3, 4))
        self.assertEqual((toks[1].linea, toks[1].columna), (4, 3))

    def test_archivo_vacio(self):
        self.assertEqual(tipos("   \n\t"), [])


class TestErroresLexicos(unittest.TestCase):
    def assertErrorEn(self, fuente, linea, columna):
        with self.assertRaises(ErrorLexico) as ctx:
            list(Lexer(fuente).tokens())
        self.assertEqual((ctx.exception.linea, ctx.exception.columna), (linea, columna))
        return ctx.exception

    def test_dolar(self):
        e = self.assertErrorEn("x = 10 $ 5;", 1, 8)
        self.assertEqual(str(e), "Error [Línea 1, Columna 8]: Carácter no válido '$'")

    def test_arroba_en_segunda_linea(self):
        self.assertErrorEn("x = 3;\ny = x @ 2;", 2, 7)

    def test_mayuscula(self):
        e = self.assertErrorEn("X = 1;", 1, 1)
        self.assertIn("minúsculas", e.mensaje)

    def test_identificador_de_varias_letras(self):
        e = self.assertErrorEn("x = 1;\nsuma = 2;", 2, 1)
        self.assertIn("'suma'", e.mensaje)

    def test_print_incompleto(self):
        e = self.assertErrorEn("prin x;", 1, 1)
        self.assertIn("print", e.mensaje)

    def test_print_con_letras_extra(self):
        self.assertErrorEn("printx;", 1, 1)

    def test_decimal_no_permitido(self):
        self.assertErrorEn("x = 3.5;", 1, 6)


if __name__ == "__main__":
    unittest.main()
