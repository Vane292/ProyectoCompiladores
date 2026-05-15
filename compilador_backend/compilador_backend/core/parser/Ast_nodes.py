# --- NODOS DEL ÁRBOL DE SINTAXIS ABSTRACTA (AST) ---

class ASTNode:
    """Clase base para todos los nodos del árbol."""
    def __repr__(self):
        return f"{self.__class__.__name__}"

# --- NODOS DE EXPRESIONES (Devuelven un valor) ---

class NumberNode(ASTNode):
    """Representa números enteros o flotantes."""
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __repr__(self):
        return f"Number({self.value})"

class StringNode(ASTNode):
    """Representa cadenas de texto."""
    def __init__(self, token):
        self.token = token
        self.value = token.value

class IdentifierNode(ASTNode):
    """Representa el nombre de una variable (lectura)."""
    def __init__(self, token):
        self.token = token
        self.name = token.value

class BinaryOpNode(ASTNode):
    """Representa operaciones con dos operandos (1 + 2, x > y)."""
    def __init__(self, left, op_token, right):
        self.left = left
        self.op_token = op_token
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.op_token.value} {self.right})"

class UnaryOpNode(ASTNode):
    """Representa operaciones de un solo operando (-5, !true)."""
    def __init__(self, op_token, node):
        self.op_token = op_token
        self.node = node

# --- NODOS DE SENTENCIAS (Acciones que no necesariamente devuelven valor) ---

class VarDeclarationNode(ASTNode):
    """Representa la declaración de una variable: int x = 10;"""
    def __init__(self, type_token, var_name_token, value_node):
        self.type_token = type_token      # int, float, string
        self.var_name_token = var_name_token # nombre de la variable
        self.value_node = value_node      # el valor asignado (puede ser una operacion)

class AssignmentNode(ASTNode):
    """Representa una re-asignación: x = 20; o x += 5;"""
    def __init__(self, var_name_token, op_token, value_node):
        self.var_name_token = var_name_token
        self.op_token = op_token # puede ser '=' o '+='
        self.value_node = value_node

class IfNode(ASTNode):
    """Representa una estructura condicional IF-ELSE."""
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

class WhileNode(ASTNode):
    """Representa un bucle WHILE."""
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class PrintNode(ASTNode):
    """Representa la instrucción print(...);"""
    def __init__(self, value_node):
        self.value_node = value_node

class BlockNode(ASTNode):
    """Representa un grupo de instrucciones entre llaves { ... }."""
    def __init__(self):
        self.statements = [] # Lista de nodos que contiene el bloque

class ProgramNode(ASTNode):
    """Nodo raíz que representa todo el programa analizado."""
    def __init__(self):
        self.statements = []