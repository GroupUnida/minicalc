"""
Analizador léxico de Mini-Calc.

Teoría aplicada (sección 2 del informe — Modelado léxico):
el lexer es la implementación directa del AFD unificado
    M = (Q, Σ, δ, q0, F)
donde la función de transición δ : Q × Σ → Q está guardada como una
tabla (diccionario de diccionarios) y no como una cadena de if/else.
El lexer sólo recorre la tabla; para cambiar el lenguaje basta cambiar
la tabla.

Estrategia: "máxima coincidencia" (maximal munch). Desde q0 se consumen
caracteres mientras exista transición. Al detenerse:
  * si el estado es de aceptación  -> se emite el token de ese estado;
  * si no lo es (q3, q4, q5, q7)   -> error léxico.
Los espacios, tabulaciones y saltos de línea se descartan en q0.
"""

from . import tokens as T
from .errores import ErrorLexico

# ---------------------------------------------------------------------------
# Q: conjunto de estados
# ---------------------------------------------------------------------------
Q0 = "q0"    # estado inicial
Q1 = "q1"    # una letra distinta de 'p'            -> ID
Q2 = "q2"    # 'p'                                  -> ID
Q3 = "q3"    # 'pr'                                 (no aceptación)
Q4 = "q4"    # 'pri'                                (no aceptación)
Q5 = "q5"    # 'prin'                               (no aceptación)
Q6 = "q6"    # 'print'                              -> KW_PRINT
Q7 = "q7"    # dos o más letras que no son 'print'  (no aceptación)
Q8 = "q8"    # uno o más dígitos                    -> NUM
Q9 = "q9"    # '='                                  -> OP_ASSIGN
Q10 = "q10"  # '+'                                  -> OP_ADD
Q11 = "q11"  # '-'                                  -> OP_SUB
Q12 = "q12"  # '*'                                  -> OP_MUL
Q13 = "q13"  # '/'                                  -> OP_DIV
Q14 = "q14"  # '('                                  -> PUNCT_LPAREN
Q15 = "q15"  # ')'                                  -> PUNCT_RPAREN
Q16 = "q16"  # ';'                                  -> PUNCT_SEMI

ESTADOS = [Q0, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8,
           Q9, Q10, Q11, Q12, Q13, Q14, Q15, Q16]

# ---------------------------------------------------------------------------
# Σ: alfabeto agrupado en clases de caracteres (columnas de la tabla)
#   'p','r','i','n','t' : letras de la palabra reservada
#   'L'                 : cualquier otra letra minúscula
#   'D'                 : dígito 0-9
#   '=','+','-','*','/','(',')',';' : símbolos
# ---------------------------------------------------------------------------
LETRAS_PRINT = "print"
SIMBOLOS = "=+-*/();"
ESPACIOS = " \t\r\n"
COLUMNAS = ["p", "r", "i", "n", "t", "L", "D"] + list(SIMBOLOS)


def clase(c: str):
    """Devuelve la columna de la tabla para el carácter c, o None si c ∉ Σ."""
    if c in LETRAS_PRINT:
        return c
    if "a" <= c <= "z":
        return "L"
    if "0" <= c <= "9":
        return "D"
    if c in SIMBOLOS:
        return c
    return None


# ---------------------------------------------------------------------------
# δ: tabla de transición  (Q × Σ -> Q).  Una celda ausente = sin transición.
# ---------------------------------------------------------------------------
_LETRAS = ["p", "r", "i", "n", "t", "L"]


def _todas_las_letras_a(destino, excepto=None, destino_excepcion=None):
    fila = {letra: destino for letra in _LETRAS}
    if excepto:
        fila[excepto] = destino_excepcion
    return fila


DELTA = {
    Q0: {"p": Q2, "r": Q1, "i": Q1, "n": Q1, "t": Q1, "L": Q1, "D": Q8,
         "=": Q9, "+": Q10, "-": Q11, "*": Q12, "/": Q13,
         "(": Q14, ")": Q15, ";": Q16},
    Q1: _todas_las_letras_a(Q7),
    Q2: _todas_las_letras_a(Q7, excepto="r", destino_excepcion=Q3),
    Q3: _todas_las_letras_a(Q7, excepto="i", destino_excepcion=Q4),
    Q4: _todas_las_letras_a(Q7, excepto="n", destino_excepcion=Q5),
    Q5: _todas_las_letras_a(Q7, excepto="t", destino_excepcion=Q6),
    Q6: _todas_las_letras_a(Q7),
    Q7: _todas_las_letras_a(Q7),
    Q8: {"D": Q8},
    Q9: {}, Q10: {}, Q11: {}, Q12: {}, Q13: {}, Q14: {}, Q15: {}, Q16: {},
}

# F: estados de aceptación y el token que reconoce cada uno
ACEPTACION = {
    Q1: T.ID, Q2: T.ID, Q6: T.KW_PRINT, Q8: T.NUM,
    Q9: T.OP_ASSIGN, Q10: T.OP_ADD, Q11: T.OP_SUB, Q12: T.OP_MUL,
    Q13: T.OP_DIV, Q14: T.PUNCT_LPAREN, Q15: T.PUNCT_RPAREN, Q16: T.PUNCT_SEMI,
}


class Lexer:
    def __init__(self, fuente: str):
        self.fuente = fuente
        self.pos = 0
        self.linea = 1
        self.columna = 1

    # -- utilidades de lectura ---------------------------------------------
    def _actual(self):
        return self.fuente[self.pos] if self.pos < len(self.fuente) else None

    def _avanzar(self):
        c = self.fuente[self.pos]
        self.pos += 1
        if c == "\n":
            self.linea += 1
            self.columna = 1
        else:
            self.columna += 1
        return c

    def _saltar_espacios(self):
        # Bucle q0 --(espacio, \t, \r, \n)--> q0 : se ignoran
        while self._actual() is not None and self._actual() in ESPACIOS:
            self._avanzar()

    # -- reconocimiento de un token con el AFD -----------------------------
    def siguiente_token(self) -> T.Token:
        self._saltar_espacios()
        linea, columna = self.linea, self.columna
        c = self._actual()
        if c is None:
            return T.Token(T.EOF, "", linea, columna)

        if clase(c) is None:
            ayuda = ""
            if "A" <= c <= "Z":
                ayuda = " (solo se permiten letras minúsculas)"
            raise ErrorLexico(linea, columna, f"Carácter no válido '{c}'{ayuda}")

        estado = Q0
        lexema = ""
        # Recorrido del AFD: se aplica δ mientras haya transición definida
        while True:
            c = self._actual()
            if c is None:
                break
            columna_c = clase(c)
            siguiente = DELTA[estado].get(columna_c) if columna_c else None
            if siguiente is None:
                break
            estado = siguiente
            lexema += self._avanzar()

        if estado in ACEPTACION:
            return T.Token(ACEPTACION[estado], lexema, linea, columna)

        # El autómata se detuvo en un estado de no aceptación
        ayuda = ""
        if estado in (Q3, Q4, Q5) or (estado == Q7 and lexema.startswith("print")):
            ayuda = " (¿quiso escribir 'print'?)"
        raise ErrorLexico(
            linea, columna,
            f"Identificador no válido '{lexema}': las variables deben ser de "
            f"una sola letra minúscula{ayuda}",
        )

    def tokens(self):
        """Generador de tokens (sin el EOF). Se detiene ante el primer error."""
        while True:
            tok = self.siguiente_token()
            if tok.tipo == T.EOF:
                return
            yield tok

    def fin(self) -> T.Token:
        """Token EOF ubicado después del último carácter del archivo."""
        return T.Token(T.EOF, "", self.linea, self.columna)
