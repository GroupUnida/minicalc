"""
Definición de los tokens de Mini-Calc.

Teoría aplicada: sección 2.b del enunciado (categorías de tokens y
expresiones regulares). Cada token es la tupla
    <TIPO_TOKEN, "LEXEMA", LÍNEA, COLUMNA>
"""

from dataclasses import dataclass

# Tipos de token (uno por expresión regular del enunciado)
KW_PRINT = "KW_PRINT"          # print
ID = "ID"                      # [a-z]
NUM = "NUM"                    # [0-9]+
OP_ASSIGN = "OP_ASSIGN"        # =
OP_ADD = "OP_ADD"              # \+
OP_SUB = "OP_SUB"              # -
OP_MUL = "OP_MUL"              # \*
OP_DIV = "OP_DIV"              # /
PUNCT_LPAREN = "PUNCT_LPAREN"  # \(
PUNCT_RPAREN = "PUNCT_RPAREN"  # \)
PUNCT_SEMI = "PUNCT_SEMI"      # ;
EOF = "EOF"                    # fin de archivo (marca interna del parser)

# Descripción legible de cada tipo, usada en los mensajes de error
DESCRIPCION = {
    KW_PRINT: "la palabra reservada 'print'",
    ID: "un identificador",
    NUM: "un número",
    OP_ASSIGN: "'='",
    OP_ADD: "'+'",
    OP_SUB: "'-'",
    OP_MUL: "'*'",
    OP_DIV: "'/'",
    PUNCT_LPAREN: "'('",
    PUNCT_RPAREN: "')'",
    PUNCT_SEMI: "';'",
    EOF: "el fin del archivo",
}


@dataclass(frozen=True)
class Token:
    tipo: str
    lexema: str
    linea: int
    columna: int

    def __str__(self) -> str:
        # Formato exigido: <TIPO_TOKEN, "LEXEMA", LÍNEA, COLUMNA>
        return f'<{self.tipo}, "{self.lexema}", {self.linea}, {self.columna}>'

    def describir(self) -> str:
        """Texto para mensajes de error, p. ej.: el identificador 'y'."""
        if self.tipo == EOF:
            return "el fin del archivo"
        if self.tipo == ID:
            return f"el identificador '{self.lexema}'"
        if self.tipo == NUM:
            return f"el número '{self.lexema}'"
        return f"'{self.lexema}'"
