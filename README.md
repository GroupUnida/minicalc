# Mini-Calc — Compilador minimalista

Trabajo Práctico Final de **Teoría de Autómatas** — Ingeniería Informática, UNIDA.

Analizador léxico (lexer) y analizador sintáctico (parser) para **Mini-Calc**, un lenguaje
de expresiones aritméticas y asignaciones. Está escrito en **Python puro**: no usa
bibliotecas de terceros ni generadores de lexers/parsers (Lex/Flex, Yacc/Bison, PLY, ANTLR).

- **Lexer:** Autómata Finito Determinista guardado como tabla de transición `δ : Q × Σ → Q`.
- **Parser:** descenso recursivo, una función por cada no terminal de la gramática
  sin recursión por la izquierda.
- **Errores:** se detiene en el primer error léxico o sintáctico y muestra
  `Error [Línea L, Columna C]: mensaje`.

## Cómo ejecutarlo (paso a paso)

### 1. Requisitos

- **Python 3.8 o superior** (Windows, Linux o macOS). No hay que instalar ninguna
  dependencia con `pip`: el programa usa sólo la biblioteca estándar.
- Para comprobar si Python está instalado, abrir una terminal y escribir:

  ```bash
  python --version
  ```

  En Windows también puede funcionar `py --version`; en Linux/macOS, `python3 --version`.
  Si no está instalado, descargarlo de <https://www.python.org/downloads/> y, en Windows,
  marcar la casilla **"Add python.exe to PATH"** durante la instalación.

### 2. Descargar el programa

Opción A, con Git:

```bash
git clone https://github.com/GroupUnida/minicalc.git
cd minicalc
```

Opción B, sin Git: en la página del repositorio, botón verde **Code → Download ZIP**,
descomprimir y entrar a la carpeta `minicalc-main`.

### 3. Abrir una terminal en la carpeta del proyecto

- **Windows:** abrir la carpeta `minicalc` en el Explorador, escribir `cmd` en la barra de
  direcciones y presionar Enter.
- **Linux / macOS:** `cd ruta/a/minicalc`.

### 4. Analizar un archivo

```bash
python minicalc.py ejemplos/ejemplo.calc
```

(En Linux/macOS usar `python3` en lugar de `python`; en Windows, si `python` no funciona, usar `py`.)

### 5. Probar todo de una vez

- **Windows:** doble clic en `probar_todo.bat`.
- **Linux / macOS:** `sh probar_todo.sh`

El script analiza los 12 archivos de `ejemplos/` (4 correctos y 8 con errores) y luego
corre las 36 pruebas automáticas.

### 6. Probar con un archivo propio

Crear un archivo de texto con extensión `.calc` (por ejemplo `prueba.calc`) con el Bloc de
notas o cualquier editor, escribir un programa Mini-Calc y ejecutar:

```bash
python minicalc.py prueba.calc
```

## Opciones

```bash
python minicalc.py <archivo.calc> [--arbol] [--dot ARCHIVO.dot] [--log ARCHIVO.log]
```

| Opción  | Qué hace |
|---------|----------|
| `--arbol` | Muestra el árbol de derivación cuando el análisis es exitoso |
| `--dot`   | Exporta el árbol a Graphviz (se dibuja con `dot -Tpng arbol.dot -o arbol.png`) |
| `--log`   | Guarda la misma salida de la consola en un archivo de log |

El programa sólo acepta archivos con extensión `.calc`.
Devuelve código de salida `0` si no hay errores y `1` si hubo un error léxico o sintáctico.

### Ejemplo

`ejemplos/ejemplo.calc`:

```
x = 10 + 5 * 2;
y = (x - 4) / 2;
print y;
```

```bash
python minicalc.py ejemplos/ejemplo.calc
```

```
=== INICIO DE ANÁLISIS LÉXICO ===
<ID, "x", 1, 1>
<OP_ASSIGN, "=", 1, 3>
<NUM, "10", 1, 5>
<OP_ADD, "+", 1, 8>
<NUM, "5", 1, 10>
<OP_MUL, "*", 1, 12>
<NUM, "2", 1, 14>
<PUNCT_SEMI, ";", 1, 15>
...
=== INICIO DE ANÁLISIS SINTÁCTICO ===
El análisis sintáctico finalizó exitosamente sin errores.
```

### Ejemplos de errores

```bash
python minicalc.py ejemplos/error_lexico_dolar.calc
# Error [Línea 1, Columna 8]: Carácter no válido '$'

python minicalc.py ejemplos/error_falta_punto_coma.calc
# Error [Línea 1, Columna 11]: Falta ';' al final de la sentencia (se encontró el identificador 'y')

python minicalc.py ejemplos/error_parentesis_sin_cerrar.calc
# Error [Línea 1, Columna 15]: Paréntesis desbalanceados: falta ')' para cerrar el '(' de la línea 1, columna 5
```

## Pruebas

### Pruebas automáticas (36 casos)

Desde la carpeta raíz del proyecto:

```bash
python -m unittest -v
```

- `tests/test_lexer.py`: tabla de transición, todos los tokens, palabra reservada `print`,
  espacios/tabs/saltos de línea, posiciones (línea y columna) y errores léxicos.
- `tests/test_parser.py`: programas válidos, precedencia de operadores, paréntesis y
  errores sintácticos con su ubicación exacta.

### Archivos de ejemplo (`ejemplos/`)

| Archivo | Resultado esperado |
|---------|--------------------|
| `ejemplo.calc` | Correcto (ejemplo del enunciado) |
| `precedencia.calc` | Correcto (precedencia y asociatividad) |
| `parentesis.calc` | Correcto (paréntesis anidados, tabulaciones, líneas vacías) |
| `vacio.calc` | Correcto (programa vacío, regla `lista_sentencias → ε`) |
| `error_lexico_dolar.calc` | Error léxico: carácter `$` |
| `error_lexico_arroba.calc` | Error léxico: carácter `@` en la línea 2 |
| `error_lexico_identificador.calc` | Error léxico: variable de varias letras (`suma`) |
| `error_falta_punto_coma.calc` | Error sintáctico: falta `;` |
| `error_falta_punto_coma_eof.calc` | Error sintáctico: falta `;` al final del archivo |
| `error_parentesis_sin_cerrar.calc` | Error sintáctico: falta `)` |
| `error_parentesis_sobrante.calc` | Error sintáctico: `)` de más |
| `error_operador.calc` | Error sintáctico: dos operadores seguidos |

Para correr todos los ejemplos de una vez: `probar_todo.bat` (Windows) o `sh probar_todo.sh` (Linux/macOS).

## Estructura del proyecto

```
minicalc/
├── minicalc.py              # programa principal (lee el .calc y ejecuta las dos fases)
├── probar_todo.bat          # corre todos los ejemplos y las pruebas (Windows)
├── probar_todo.sh           # ídem para Linux / macOS
├── analizador/
│   ├── tokens.py            # tipos de token y clase Token
│   ├── lexer.py             # AFD: estados, alfabeto, tabla δ y estados de aceptación
│   ├── parser.py            # descenso recursivo (una función por no terminal)
│   ├── arbol.py             # árbol de derivación (consola y Graphviz)
│   └── errores.py           # ErrorLexico y ErrorSintactico
├── ejemplos/                # archivos .calc válidos y con errores
├── tests/                   # pruebas automáticas (unittest)
└── Documentación/
    ├── README.md            # este archivo
    └── demo.mp4             # video corto de demostración
```

## Especificación de Mini-Calc

**Tokens**

| Token | Expresión regular |
|-------|-------------------|
| `KW_PRINT` | `print` |
| `ID` | `[a-z]` (una sola letra) |
| `NUM` | `[0-9]+` |
| `OP_ASSIGN` | `=` |
| `OP_ADD`, `OP_SUB`, `OP_MUL`, `OP_DIV` | `\+`, `-`, `\*`, `/` |
| `PUNCT_LPAREN`, `PUNCT_RPAREN`, `PUNCT_SEMI` | `\(`, `\)`, `;` |

Los espacios, tabulaciones y saltos de línea se ignoran. La tabulación cuenta como una columna.

**Gramática usada por el parser (sin recursión por la izquierda)**

```
programa          → lista_sentencias
lista_sentencias  → sentencia lista_sentencias | ε
sentencia         → ID OP_ASSIGN expresion PUNCT_SEMI
                  | KW_PRINT expresion PUNCT_SEMI
expresion         → termino expresion'
expresion'        → OP_ADD termino expresion' | OP_SUB termino expresion' | ε
termino           → factor termino'
termino'          → OP_MUL factor termino' | OP_DIV factor termino' | ε
factor            → PUNCT_LPAREN expresion PUNCT_RPAREN | ID | NUM
```

## Integrantes

| Nombre | Usuario de GitHub |
|--------|-------------------|
| Alejandro Martínez | Alejandro-Codedev |
| Mauricio González | MauriGonza |
| Sergio Sanabria | sergioalex0528-glitch |
| Ismael Hermosilla | |
| Ruth Nuñez | |
| Leandro Gimenez | |
