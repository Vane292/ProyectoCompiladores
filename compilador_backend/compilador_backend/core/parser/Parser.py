from .Ast_nodes import (
    ProgramNode, VarDeclarationNode, AssignmentNode, PrintNode,
    IfNode, WhileNode, BlockNode, BinaryOpNode, NumberNode,
    StringNode, IdentifierNode, UnaryOpNode
)
from ..lexer.Tokens import TokenType

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_actual = self.tokens[self.pos] if self.tokens else None
        self.log_pasos = []
        self.errores = []

    # --- UTILIDADES ---

    def avanzar(self):
        """Avanza al siguiente token en la lista."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token_actual = self.tokens[self.pos]
        return self.token_actual

    def consumir(self, tipo_esperado):
        """Verifica que el token actual sea el esperado y avanza."""
        if self.token_actual and self.token_actual.type == tipo_esperado:
            token_consumido = self.token_actual
            self.log_pasos.append(f"Sintáctico: Consumido {tipo_esperado.name} ('{token_consumido.value}')")
            self.avanzar()
            return token_consumido
        else:
            error = f"Error Sintáctico: Se esperaba {tipo_esperado.name} pero se encontró {self.token_actual.type.name if self.token_actual else 'EOF'} en {self.token_actual.line if self.token_actual else '?'}"
            self.errores.append(error)
            # No lanzamos excepción para intentar seguir parseando otras líneas
            return None

    # --- MOTOR PRINCIPAL ---

    def parsear(self):
        """Punto de entrada: construye el nodo raíz del programa."""
        self.log_pasos.append("Sintáctico: Iniciando construcción del AST...")
        raiz = ProgramNode()
        
        while self.token_actual and self.token_actual.type != TokenType.EOF:
            instruccion = self.declaracion()
            if instruccion:
                raiz.statements.append(instruccion)
        
        self.log_pasos.append("Sintáctico: Construcción del AST finalizada.")
        return raiz

    # --- REGLAS DE GRAMÁTICA ---

    def declaracion(self):
        """Decide qué tipo de instrucción procesar."""
        # Ej: int x = 10;
        if self.token_actual.type in [TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.BOOL]:
            return self.variable_declaracion()
        
        # Ej: if (...) { ... }
        elif self.token_actual.type == TokenType.IF:
            return self.if_sentencia()
        
        # Ej: print(...);
        elif self.token_actual.type == TokenType.PRINT:
            return self.print_sentencia()
        
        # Ej: x = 20;
        elif self.token_actual.type == TokenType.ID:
            return self.asignacion_o_expresion()

        # Si llegamos aquí y hay un punto y coma suelto, lo saltamos
        elif self.token_actual.type == TokenType.SEMICOLON:
            self.avanzar()
            return None
        
        self.errores.append(f"Error: Instrucción no reconocida '{self.token_actual.value}'")
        self.avanzar()
        return None

    def variable_declaracion(self):
        """Procesa: TIPO ID = EXPRESION;"""
        tipo = self.consumir(self.token_actual.type)
        nombre = self.consumir(TokenType.ID)
        self.consumir(TokenType.ASSIGN)
        valor = self.expresion()
        self.consumir(TokenType.SEMICOLON)
        return VarDeclarationNode(tipo, nombre, valor)

    def print_sentencia(self):
        """Procesa: print(EXPRESION);"""
        self.consumir(TokenType.PRINT)
        self.consumir(TokenType.LPAREN)
        valor = self.expresion()
        self.consumir(TokenType.RPAREN)
        self.consumir(TokenType.SEMICOLON)
        return PrintNode(valor)

    def if_sentencia(self):
        """Procesa: if (CONDICION) { BLOQUE } else { BLOQUE }"""
        self.consumir(TokenType.IF)
        self.consumir(TokenType.LPAREN)
        condicion = self.expresion()
        self.consumir(TokenType.RPAREN)
        
        cuerpo_if = self.bloque()
        cuerpo_else = None
        
        if self.token_actual.type == TokenType.ELSE:
            self.consumir(TokenType.ELSE)
            cuerpo_else = self.bloque()
            
        return IfNode(condicion, cuerpo_if, cuerpo_else)

    def bloque(self):
        """Procesa un conjunto de instrucciones entre { }"""
        self.consumir(TokenType.LBRACE)
        nodo_bloque = BlockNode()
        while self.token_actual and self.token_actual.type != TokenType.RBRACE:
            instruccion = self.declaracion()
            if instruccion:
                nodo_bloque.statements.append(instruccion)
        self.consumir(TokenType.RBRACE)
        return nodo_bloque

    # --- MANEJO DE EXPRESIONES (Prioridad Matemática) ---

    def expresion(self):
        """Maneja sumas y restas (Prioridad baja)"""
        izquierda = self.termino()
        while self.token_actual and self.token_actual.type in [TokenType.PLUS, TokenType.MINUS, TokenType.GT, TokenType.LT, TokenType.GTE, TokenType.LTE]:
            op = self.token_actual
            self.avanzar()
            derecha = self.termino()
            izquierda = BinaryOpNode(izquierda, op, derecha)
        return izquierda

    def termino(self):
        """Maneja multiplicaciones y divisiones (Prioridad media)"""
        izquierda = self.factor()
        while self.token_actual and self.token_actual.type in [TokenType.MULTIPLY, TokenType.DIVIDE]:
            op = self.token_actual
            self.avanzar()
            derecha = self.factor()
            izquierda = BinaryOpNode(izquierda, op, derecha)
        return izquierda

    def factor(self):
        """Maneja números, IDs y paréntesis (Prioridad alta)"""
        token = self.token_actual
        
        if token.type == TokenType.NUMBER_INT or token.type == TokenType.NUMBER_FLOAT:
            self.avanzar()
            return NumberNode(token)
        
        elif token.type == TokenType.STR_LITERAL:
            self.avanzar()
            return StringNode(token)
            
        elif token.type == TokenType.ID:
            self.avanzar()
            return IdentifierNode(token)
            
        elif token.type == TokenType.LPAREN:
            self.avanzar()
            expr = self.expresion()
            self.consumir(TokenType.RPAREN)
            return expr
            
        self.errores.append(f"Error: Se esperaba un valor en {token.line}:{token.column}")
        return None

    def asignacion_o_expresion(self):
        """Diferencia entre x = 10; y una expresión suelta."""
        nombre = self.consumir(TokenType.ID)
        if self.token_actual.type == TokenType.ASSIGN:
            op = self.consumir(TokenType.ASSIGN)
            valor = self.expresion()
            self.consumir(TokenType.SEMICOLON)
            return AssignmentNode(nombre, op, valor)
        else:
            # Si no hay asignación, es solo una expresión (poco común solo el nombre)
            self.consumir(TokenType.SEMICOLON)
            return IdentifierNode(nombre)