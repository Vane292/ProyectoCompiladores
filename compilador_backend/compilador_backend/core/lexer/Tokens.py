from enum import Enum, auto

# --- CATEGORIAS DE TOKENS ---
# Usamos Enum para que el sistema sea inmune a errores de dedo (typos)
class TokenType(Enum):
    # Palabras reservadas (Keywords)
    INT = auto()       # int
    FLOAT = auto()     # float
    STRING = auto()    # string
    BOOL = auto()      # bool
    IF = auto()        # if
    ELSE = auto()      # else
    WHILE = auto()     # while
    FOR = auto()       # for
    PRINT = auto()     # print
    RETURN = auto()    # return
    TRUE = auto()      # true
    FALSE = auto()     # false

    # Identificadores y Literales
    ID = auto()          # Nombre de variables o funciones
    NUMBER_INT = auto()  # Numeros enteros (10, 20)
    NUMBER_FLOAT = auto()# Numeros decimales (10.5, 3.14)
    STR_LITERAL = auto() # Texto entre comillas ("hola")

    # Operadores Aritmeticos
    PLUS = auto()      # +
    MINUS = auto()     # -
    MULTIPLY = auto()  # *
    DIVIDE = auto()    # /
    MODULO = auto()    # %
    POWER = auto()     # ^

    # Operadores de Asignacion
    ASSIGN = auto()         # =
    PLUS_ASSIGN = auto()    # +=
    MINUS_ASSIGN = auto()   # -=

    # Operadores de Comparacion y Logicos
    EQ = auto()      # ==
    NEQ = auto()     # !=
    LT = auto()      # <
    GT = auto()      # >
    LTE = auto()     # <=
    GTE = auto()     # >=
    AND = auto()     # &&
    OR = auto()      # ||
    NOT = auto()     # !

    # Delimitadores y Simbolos de Puntuacion
    LPAREN = auto()    # (
    RPAREN = auto()    # )
    LBRACE = auto()    # {
    RBRACE = auto()    # }
    SEMICOLON = auto() # ;
    COMMA = auto()     # ,
    DOT = auto()       # .

    # Tokens Especiales
    EOF = auto()      # Fin del archivo (End of File)
    ERROR = auto()    # Simbolo no reconocido
    COMMENT = auto()  # Comentarios (para ignorar o resaltar)

# --- CLASE TOKEN (OBJETO DE DATOS) ---
class Token:
    # Esta clase empaqueta toda la informacion de cada palabra encontrada
    def __init__(self, type, value, line, column):
        self.type = type      # Tipo de token (de la clase TokenType)
        self.value = value    # El texto real capturado
        self.line = line      # Numero de linea para reporte de errores
        self.column = column  # Columna exacta para el frontend

    # Metodo para imprimir el token de forma legible en consola
    def __repr__(self):
        return f"<{self.type.name}: '{self.value}' en {self.line}:{self.column}>"

    # Metodo para convertir el objeto a diccionario (ideal para JSON/Frontend)
    def to_dict(self):
        return {
            "type": self.type.name,
            "value": self.value,
            "line": self.line,
            "column": self.column
        }