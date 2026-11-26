"""
Errores del compilador. Ambos detienen la ejecución y se informan con el
formato exigido por el enunciado:

    Error [Línea L, Columna C]: Mensaje descriptivo del error
"""


class ErrorCompilacion(Exception):
    tipo = "error"

    def __init__(self, linea: int, columna: int, mensaje: str):
        self.linea = linea
        self.columna = columna
        self.mensaje = mensaje
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"Error [Línea {self.linea}, Columna {self.columna}]: {self.mensaje}"


class ErrorLexico(ErrorCompilacion):
    tipo = "léxico"


class ErrorSintactico(ErrorCompilacion):
    tipo = "sintáctico"
