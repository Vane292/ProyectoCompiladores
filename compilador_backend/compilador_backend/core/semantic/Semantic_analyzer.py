from .Symbol_table import SymbolTable

class SemanticAnalyzer:
    def __init__(self):
        self.tabla_simbolos = SymbolTable()
        self.errores = []
        self.log_pasos = []

    def analizar(self, nodo):
        """Método principal que decide qué hacer según el tipo de nodo."""
        if nodo is None: return None
        metodo_nombre = f'visitar_{type(nodo).__name__}'
        visitante = getattr(self, metodo_nombre, self.visita_generica)
        return visitante(nodo)

    def visita_generica(self, nodo):
        """Recorre nodos que contienen listas de instrucciones."""
        if hasattr(nodo, 'statements'):
            for instruccion in nodo.statements:
                self.analizar(instruccion)

    def _obtener_valor_literal(self, nodo):
        """
        Función auxiliar para extraer el valor real de un nodo.
        Si es una operación matemática simple, intenta resolverla.
        """
        # Si es un número o un string directo
        if hasattr(nodo, 'value'):
            return nodo.value
        
        # Si es una variable, busca su valor actual en la tabla
        if hasattr(nodo, 'name'): # IdentifierNode
            simbolo = self.tabla_simbolos.buscar(nodo.name)
            return simbolo['valor'] if simbolo else None

        # Si es una operación binaria (ej: 5 + 5)
        if hasattr(nodo, 'left') and hasattr(nodo, 'right'):
            izq = self._obtener_valor_literal(nodo.left)
            der = self._obtener_valor_literal(nodo.right)
            op = nodo.op_token.value

            try:
                if op == '+': return izq + der
                if op == '-': return izq - der
                if op == '*': return izq * der
                if op == '/': return izq / der
            except:
                return None
        
        return None

    # --- VISITANTES ESPECÍFICOS (CORREGIDOS) ---

    def visitar_VarDeclarationNode(self, nodo):
        nombre = nodo.var_name_token.value
        tipo = nodo.type_token.value
        
        self.log_pasos.append(f"Semántico: Validando declaración de '{nombre}' como {tipo}")
        
        # 1. Intentar insertar en la tabla (Reserva de espacio)
        exito, mensaje = self.tabla_simbolos.insertar(nombre, tipo)
        if not exito:
            self.errores.append(f"Error Semántico en {nodo.var_name_token.line}:{nodo.var_name_token.column} -> {mensaje}")
            return

        # 2. EXTRAER Y ASIGNAR VALOR (Aquí se corrige el NULL)
        if nodo.value_node:
            valor = self._obtener_valor_literal(nodo.value_node)
            self.tabla_simbolos.asignar(nombre, valor)
            self.log_pasos.append(f"Semántico: '{nombre}' inicializada con valor: {valor}")

    def visitar_AssignmentNode(self, nodo):
        nombre = nodo.var_name_token.value
        
        if not self.tabla_simbolos.existe(nombre):
            self.errores.append(f"Error Semántico: Variable '{nombre}' no declarada.")
            return

        # EXTRAER NUEVO VALOR Y ACTUALIZAR TABLA
        valor = self._obtener_valor_literal(nodo.value_node)
        self.tabla_simbolos.asignar(nombre, valor)
        self.log_pasos.append(f"Semántico: Actualizando valor de '{nombre}' a: {valor}")

    def visitar_IdentifierNode(self, nodo):
        if not self.tabla_simbolos.existe(nodo.name):
            self.errores.append(f"Error Semántico: Variable '{nodo.name}' no definida.")

    def visitar_BinaryOpNode(self, nodo):
        self.analizar(nodo.left)
        self.analizar(nodo.right)

    def visitar_PrintNode(self, nodo):
        self.analizar(nodo.value_node)

    def visitar_IfNode(self, nodo):
        self.analizar(nodo.condition)
        self.analizar(nodo.then_block)
        if nodo.else_block:
            self.analizar(nodo.else_block)

    def visitar_BlockNode(self, nodo):
        self.visita_generica(nodo)

    def visitar_ProgramNode(self, nodo):
        self.visita_generica(nodo)
    
    def visitar_VarDeclarationNode(self, nodo):
        nombre = nodo.var_name_token.value
        tipo_declarado = nodo.type_token.value.lower()
        
        # 1. Registro en Tabla de Símbolos
        exito, mensaje = self.tabla_simbolos.insertar(nombre, tipo_declarado)
        if not exito:
            self.errores.append(f"Error Semántico: {mensaje}")
            return

        # 2. VALIDACIÓN DE TIPOS ESTRICTA
        if nodo.value_node:
            valor = self._obtener_valor_literal(nodo.value_node)
            
            # Verificamos la compatibilidad
            es_valido = False
            
            if tipo_declarado == "int" and isinstance(valor, int):
                es_valido = True
            elif tipo_declarado == "float" and (isinstance(valor, float) or isinstance(valor, int)):
                # Un float puede aceptar un int (promoción), pero no al revés
                es_valido = True
            elif tipo_declarado == "string" and isinstance(valor, str):
                es_valido = True
            elif tipo_declarado == "bool" and isinstance(valor, bool):
                es_valido = True

            if not es_valido:
                tipo_real = type(valor).__name__
                # Traducimos el nombre del tipo para el error
                mapping = {"str": "string", "int": "int", "float": "float"}
                tipo_real = mapping.get(tipo_real, tipo_real)
                
                self.errores.append(
                    f"Incompatibilidad de tipos: No se puede asignar {tipo_real} a una variable {tipo_declarado.upper()} ('{nombre}')"
                )
                return

            # Si pasa la validación, asignamos el valor
            self.tabla_simbolos.asignar(nombre, valor)
            self.log_pasos.append(f"Semántico: '{nombre}' inicializada correctamente con {valor}")
    
   