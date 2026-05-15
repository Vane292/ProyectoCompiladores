import re
# Importamos las definiciones del archivo anterior
from .Tokens import TokenType, Token

class Lexer:
    def __init__(self):
        # Lista de objetos Token encontrados
        self.tokens = []
        # Bitacora detallada para la ventana de procesamiento del frontend
        self.log_pasos = []
        # Registro de errores lexicos
        self.errores = []

    def analizar(self, codigo_fuente):
        # Reiniciar todas las listas para un nuevo proceso
        self.tokens = []
        self.log_pasos = []
        self.errores = []
        
        # Definicion de patrones con prioridad (los mas largos primero)
        especificaciones = [
            ('NUMBER_FLOAT', r'\d+\.\d+'),     # Ej: 10.5
            ('NUMBER_INT',   r'\d+'),           # Ej: 10
            ('ID',           r'[a-zA-Z_]\w*'),  # Variables y palabras clave
            ('STR_LITERAL',  r'\"[^\"]*\"'),    # Texto entre comillas
            ('COMMENT',      r'//.*'),          # Ignorar comentarios
            ('PLUS_ASSIGN',  r'\+='),           # Operadores compuestos
            ('MINUS_ASSIGN', r'-='),
            ('EQ',           r'=='),            # Comparadores
            ('NEQ',          r'!='),
            ('LTE',          r'<='),
            ('GTE',          r'>='),
            ('AND',          r'&&'),
            ('OR',           r'\|\|'),
            ('PLUS',         r'\+'),            # Operadores simples
            ('MINUS',        r'-'),
            ('MULTIPLY',     r'\*'),
            ('DIVIDE',       r'/'),
            ('MODULO',       r'%'),
            ('POWER',        r'\^'),
            ('ASSIGN',       r'='),
            ('LT',           r'<'),
            ('GT',           r'>'),
            ('NOT',          r'!'),
            ('LPAREN',       r'\('),            # Simbolos de agrupacion
            ('RPAREN',       r'\)'),
            ('LBRACE',       r'\{'),
            ('RBRACE',       r'\}'),
            ('SEMICOLON',    r';'),
            ('COMMA',        r','),
            ('DOT',          r'\.'),
            ('NEWLINE',      r'\n'),            # Control de lineas
            ('SKIP',         r'[ \t\r]+'),      # Espacios y tabulaciones
            ('MISMATCH',     r'.'),             # Caracter ilegal
        ]

        # Crear una regex maestra uniendo todos los grupos
        regex_maestra = '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in especificaciones)
        
        linea_actual = 1
        inicio_linea = 0

        # Escaneo del codigo usando el motor de regex de Python
        for coincidencia in re.finditer(regex_maestra, codigo_fuente):
            tipo = coincidencia.lastgroup
            valor = coincidencia.group()
            columna = coincidencia.start() - inicio_linea + 1

            # Procesar el tipo de token encontrado
            if tipo == 'NEWLINE':
                # Actualizar posicion para el conteo de lineas
                inicio_linea = coincidencia.end()
                linea_actual += 1
                self.log_pasos.append(f"Linea {linea_actual}: Salto de linea detectado.")
            
            elif tipo == 'SKIP' or tipo == 'COMMENT':
                # No generar tokens para espacios o comentarios
                continue
            
            elif tipo == 'ID':
                # Verificar si el nombre es una palabra reservada
                tipo_final = self._buscar_palabra_reservada(valor)
                self._crear_token(tipo_final, valor, linea_actual, columna)
            
            elif tipo == 'NUMBER_FLOAT':
                self._crear_token(TokenType.NUMBER_FLOAT, valor, linea_actual, columna)
            
            elif tipo == 'NUMBER_INT':
                self._crear_token(TokenType.NUMBER_INT, valor, linea_actual, columna)
            
            elif tipo == 'STR_LITERAL':
                # Guardar el texto sin las comillas
                self._crear_token(TokenType.STR_LITERAL, valor[1:-1], linea_actual, columna)
            
            elif tipo == 'MISMATCH':
                # Registrar error lexico sin detener el compilador
                msg_error = f"Error Lexico: Simbolo '{valor}' no valido en {linea_actual}:{columna}"
                self.errores.append(msg_error)
                self.log_pasos.append(msg_error)
            
            else:
                # Procesar operadores y delimitadores segun el nombre del grupo
                self._crear_token(TokenType[tipo], valor, linea_actual, columna)

        # Agregar el token de fin de archivo al terminar
        self.tokens.append(Token(TokenType.EOF, "EOF", linea_actual, 0))
        self.log_pasos.append("Analisis lexico finalizado: EOF alcanzado.")
        
        return self.tokens

    def _crear_token(self, tipo, valor, linea, columna):
        # Metodo auxiliar para generar el objeto y registrar en el log
        nuevo_token = Token(tipo, valor, linea, columna)
        self.tokens.append(nuevo_token)
        self.log_pasos.append(f"Token generado: {tipo.name} ('{valor}') en [{linea}:{columna}]")

    def _buscar_palabra_reservada(self, valor):
        # Diccionario para convertir identificadores en palabras clave
        palabras_clave = {
            'int': TokenType.INT, 'float': TokenType.FLOAT, 'string': TokenType.STRING,
            'bool': TokenType.BOOL, 'if': TokenType.IF, 'else': TokenType.ELSE,
            'while': TokenType.WHILE, 'for': TokenType.FOR, 'print': TokenType.PRINT,
            'return': TokenType.RETURN, 'true': TokenType.TRUE, 'false': TokenType.FALSE
        }
        return palabras_clave.get(valor, TokenType.ID)