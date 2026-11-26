"""
Analizador sintáctico de Mini-Calc por DESCENSO RECURSIVO.

Teoría aplicada (Parte 1.2 del informe — Transformación gramatical):
la gramática del enunciado tiene recursión por la izquierda en
<expresion> y <termino>, que haría entrar en un bucle infinito a un
parser descendente. Se usa la gramática transformada (LL(1)):

  programa          -> lista_sentencias
  lista_sentencias  -> sentencia lista_sentencias | ε
  sentencia         -> ID OP_ASSIGN expresion PUNCT_SEMI
                     | KW_PRINT expresion PUNCT_SEMI
  expresion         -> termino expresion'
  expresion'        -> OP_ADD termino expresion' | OP_SUB termino expresion' | ε
  termino           -> factor termino'
  termino'          -> OP_MUL factor termino' | OP_DIV factor termino' | ε
  factor            -> PUNCT_LPAREN expresion PUNCT_RPAREN | ID | NUM

Hay UNA función por cada no terminal. Cada función decide qué producción
aplicar mirando un solo token (el símbolo de preanálisis), según los
conjuntos PRIMERO/SIGUIENTE. Cada función devuelve el nodo del árbol de
derivación correspondiente.
"""

from . import tokens as T
from .arbol import Nodo
from .errores import ErrorSintactico

PRIMERO_FACTOR = {T.PUNCT_LPAREN, T.ID, T.NUM}
PRIMERO_SENTENCIA = {T.ID, T.KW_PRINT}


class Parser:
    def __init__(self, lista_tokens):
        # La lista debe terminar con un token EOF
        self.tokens = lista_tokens
        self.i = 0

    # -- utilidades -----------------------------------------------------------
    @property
    def actual(self) -> T.Token:
        return self.tokens[self.i]

    @property
    def anterior(self) -> T.Token:
        return self.tokens[self.i - 1] if self.i > 0 else self.actual

    def _error(self, mensaje, token=None):
        tok = token or self.actual
        raise ErrorSintactico(tok.linea, tok.columna, mensaje)

    def _error_despues_del_anterior(self, mensaje):
        """Ubica el error justo después del último token aceptado
        (el lugar exacto donde falta el símbolo)."""
        prev = self.anterior
        raise ErrorSintactico(prev.linea, prev.columna + len(prev.lexema), mensaje)

    def _consumir(self, tipo, padre: Nodo) -> T.Token:
        """Empareja (match) el terminal esperado y lo cuelga en el árbol."""
        tok = self.actual
        if tok.tipo != tipo:
            self._error(f"Se esperaba {T.DESCRIPCION[tipo]}, "
                        f"pero se encontró {tok.describir()}")
        padre.agregar(Nodo(tok.tipo, tok.lexema))
        self.i += 1
        return tok

    # -- punto de entrada ---------------------------------------------------------
    def analizar(self) -> Nodo:
        arbol = self.programa()
        if self.actual.tipo != T.EOF:  # no debería ocurrir, por seguridad
            self._error(f"Símbolo inesperado {self.actual.describir()}")
        return arbol

    # programa -> lista_sentencias
    def programa(self) -> Nodo:
        nodo = Nodo("programa")
        nodo.agregar(self.lista_sentencias())
        return nodo

    # lista_sentencias -> sentencia lista_sentencias | ε
    def lista_sentencias(self) -> Nodo:
        nodo = Nodo("lista_sentencias")
        if self.actual.tipo in PRIMERO_SENTENCIA:
            nodo.agregar(self.sentencia())
            nodo.agregar(self.lista_sentencias())
        elif self.actual.tipo == T.EOF:          # SIGUIENTE(lista_sentencias) = {EOF}
            nodo.agregar(Nodo("ε"))
        elif self.actual.tipo == T.PUNCT_RPAREN:
            self._error("Paréntesis desbalanceados: ')' sin un '(' de apertura")
        else:
            self._error("Se esperaba el inicio de una sentencia (un identificador "
                        f"o 'print'), pero se encontró {self.actual.describir()}")
        return nodo

    # sentencia -> ID OP_ASSIGN expresion PUNCT_SEMI
    #            | KW_PRINT expresion PUNCT_SEMI
    def sentencia(self) -> Nodo:
        nodo = Nodo("sentencia")
        if self.actual.tipo == T.ID:
            ident = self._consumir(T.ID, nodo)
            if self.actual.tipo != T.OP_ASSIGN:
                self._error(f"Se esperaba '=' después de '{ident.lexema}', "
                            f"pero se encontró {self.actual.describir()}")
            self._consumir(T.OP_ASSIGN, nodo)
        else:
            self._consumir(T.KW_PRINT, nodo)
        nodo.agregar(self.expresion())
        self._fin_de_sentencia(nodo)
        return nodo

    def _fin_de_sentencia(self, nodo):
        tok = self.actual
        if tok.tipo == T.PUNCT_SEMI:
            self._consumir(T.PUNCT_SEMI, nodo)
        elif tok.tipo == T.PUNCT_RPAREN:
            self._error("Paréntesis desbalanceados: ')' sin un '(' de apertura")
        else:
            self._error_despues_del_anterior(
                f"Falta ';' al final de la sentencia (se encontró {tok.describir()})")

    # expresion -> termino expresion'
    def expresion(self) -> Nodo:
        nodo = Nodo("expresion")
        nodo.agregar(self.termino())
        nodo.agregar(self.expresion_prima())
        return nodo

    # expresion' -> OP_ADD termino expresion' | OP_SUB termino expresion' | ε
    def expresion_prima(self) -> Nodo:
        nodo = Nodo("expresion'")
        if self.actual.tipo in (T.OP_ADD, T.OP_SUB):
            self._consumir(self.actual.tipo, nodo)
            nodo.agregar(self.termino())
            nodo.agregar(self.expresion_prima())
        else:                                     # ε  (SIGUIENTE = { ; , ) })
            nodo.agregar(Nodo("ε"))
        return nodo

    # termino -> factor termino'
    def termino(self) -> Nodo:
        nodo = Nodo("termino")
        nodo.agregar(self.factor())
        nodo.agregar(self.termino_prima())
        return nodo

    # termino' -> OP_MUL factor termino' | OP_DIV factor termino' | ε
    def termino_prima(self) -> Nodo:
        nodo = Nodo("termino'")
        if self.actual.tipo in (T.OP_MUL, T.OP_DIV):
            self._consumir(self.actual.tipo, nodo)
            nodo.agregar(self.factor())
            nodo.agregar(self.termino_prima())
        else:                                     # ε  (SIGUIENTE = { + - ; ) })
            nodo.agregar(Nodo("ε"))
        return nodo

    # factor -> PUNCT_LPAREN expresion PUNCT_RPAREN | ID | NUM
    def factor(self) -> Nodo:
        nodo = Nodo("factor")
        tok = self.actual
        if tok.tipo == T.PUNCT_LPAREN:
            apertura = self._consumir(T.PUNCT_LPAREN, nodo)
            nodo.agregar(self.expresion())
            if self.actual.tipo != T.PUNCT_RPAREN:
                self._error_despues_del_anterior(
                    "Paréntesis desbalanceados: falta ')' para cerrar el '(' de "
                    f"la línea {apertura.linea}, columna {apertura.columna}")
            self._consumir(T.PUNCT_RPAREN, nodo)
        elif tok.tipo in (T.ID, T.NUM):
            self._consumir(tok.tipo, nodo)
        else:
            self._error("Se esperaba un número, un identificador o '(', "
                        f"pero se encontró {tok.describir()}")
        return nodo
