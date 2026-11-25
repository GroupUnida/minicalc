"""
Árbol de derivación (árbol sintáctico concreto) que construye el parser.
Sirve para mostrar los casos de prueba teóricos (Parte 1.3) y se puede
imprimir en consola o exportar a Graphviz (.dot).
"""


class Nodo:
    def __init__(self, etiqueta: str, lexema: str = None):
        self.etiqueta = etiqueta    # no terminal, tipo de token o "ε"
        self.lexema = lexema        # sólo para hojas que son tokens
        self.hijos = []

    def agregar(self, hijo: "Nodo") -> "Nodo":
        self.hijos.append(hijo)
        return hijo

    def texto(self) -> str:
        if self.lexema is not None:
            return f'{self.etiqueta} "{self.lexema}"'
        return self.etiqueta

    # -- salida en consola ---------------------------------------------------
    def dibujar(self) -> str:
        lineas = [self.texto()]
        self._dibujar_hijos("", lineas)
        return "\n".join(lineas)

    def _dibujar_hijos(self, prefijo, lineas):
        for i, hijo in enumerate(self.hijos):
            ultimo = i == len(self.hijos) - 1
            lineas.append(prefijo + ("└── " if ultimo else "├── ") + hijo.texto())
            hijo._dibujar_hijos(prefijo + ("    " if ultimo else "│   "), lineas)

    # -- exportación a Graphviz ---------------------------------------------
    def a_dot(self) -> str:
        lineas = [
            "digraph arbol {",
            '  node [fontname="Helvetica", fontsize=11];',
            "  edge [arrowhead=none];",
        ]
        contador = [0]

        def visitar(nodo):
            ident = f"n{contador[0]}"
            contador[0] += 1
            if nodo.lexema is not None:
                etiqueta = (f'<<TABLE BORDER="0" CELLSPACING="3" CELLPADDING="1">'
                            f'<TR><TD>{nodo.etiqueta}</TD></TR>'
                            f'<TR><TD><B>&quot;{nodo.lexema}&quot;</B></TD></TR></TABLE>>')
                lineas.append(f'  {ident} [label={etiqueta}, shape=box, '
                              f'style="rounded,filled", fillcolor="#e8f0fe"];')
            elif nodo.etiqueta == "ε":
                lineas.append(f'  {ident} [label="ε", shape=plaintext];')
            else:
                lineas.append(f'  {ident} [label="{nodo.etiqueta}", shape=ellipse];')
            for hijo in nodo.hijos:
                lineas.append(f"  {ident} -> {visitar(hijo)};")
            return ident

        visitar(self)
        lineas.append("}")
        return "\n".join(lineas)
