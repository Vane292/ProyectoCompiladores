class SymbolTable:
    """
    Gestor de la memoria simbólica del compilador.
    Encargado de almacenar nombres, tipos, valores y metadatos de las variables.
    """
    def __init__(self):
        # Diccionario principal: { 'nombre': {datos} }
        self.tabla = {}
        # Historial para el reporte del compilador
        self.log_pasos = []

    def insertar(self, nombre, tipo):
        """
        Registra una nueva variable en la tabla. 
        Implementa la lógica de clase con soporte extendido para float y string.
        """
        tipo = tipo.lower()
        
        # 1. Verificación de Reduplicación
        if nombre in self.tabla:
            self.log_pasos.append(f"[!] Error: La variable '{nombre}' ya existe.")
            return False, f"La variable '{nombre}' ya fue declarada anteriormente."

        # 2. Soporte de tipos (Requisito de clase: int, float, string)
        especificaciones_tipo = {
            "int": {"memoria": 4, "descripcion": "Entero"},
            "float": {"memoria": 8, "descripcion": "Punto Flotante"},
            "string": {"memoria": 16, "descripcion": "Cadena de Texto"},
            "bool": {"memoria": 1, "descripcion": "Booleano"}
        }

        if tipo not in especificaciones_tipo:
            return False, f"Tipo de dato '{tipo}' no reconocido por el sistema."

        # 3. Inserción Robusta
        self.tabla[nombre] = {
            "tipo": tipo,
            "valor": None,
            "memoria": especificaciones_tipo[tipo]["memoria"],
            "inicializada": False
        }
        
        self.log_pasos.append(f"✔ Variable '{nombre}' insertada ({tipo}, {especificaciones_tipo[tipo]['memoria']} bytes)")
        return True, None

    def asignar(self, nombre, valor):
        """
        Asigna un valor a una variable existente.
        """
        if nombre not in self.tabla:
            self.log_pasos.append(f"[!] Error: '{nombre}' no declarada.")
            return False, f"La variable '{nombre}' no ha sido declarada."

        # Aquí guardamos el valor
        self.tabla[nombre]["valor"] = valor
        self.tabla[nombre]["inicializada"] = True
        
        self.log_pasos.append(f"✔ Asignación: {nombre} = {valor}")
        return True, None

    def buscar(self, nombre):
        """Busca y retorna la información de un símbolo."""
        return self.tabla.get(nombre, None)

    def existe(self, nombre):
        """Verificación rápida de existencia."""
        return nombre in self.tabla

    def obtener_tipo(self, nombre):
        """Retorna el tipo de una variable si existe."""
        simbolo = self.buscar(nombre)
        return simbolo["tipo"] if simbolo else None

    def mostrar(self):
        """Genera una representación visual de la tabla para el reporte final."""
        print("\n" + "="*65)
        print(f"{'TABLA DE SÍMBOLOS (ESTADO DE MEMORIA)':^65}")
        print("="*65)
        print(f"{'NOMBRE':<15} | {'TIPO':<10} | {'VALOR':<20} | {'MEMORIA'}")
        print("-" * 65)
        
        for nombre, datos in self.tabla.items():
            valor = datos['valor'] if datos['inicializada'] else "NULL"
            print(f"{nombre:<15} | {datos['tipo']:<10} | {str(valor):<20} | {datos['memoria']} bytes")
        print("="*65 + "\n")