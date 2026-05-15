from core.lexer.Lexer import Lexer
from core.parser.Parser import Parser
from core.semantic.Semantic_analyzer import SemanticAnalyzer

def ejecutar_interactivo():
    # La memoria persiste durante toda la sesión
    analizador_semantico = SemanticAnalyzer()
    
    print("="*70)
    print(f"{'MODO DE DIAGNÓSTICO PROFUNDO DEL COMPILADOR':^70}")
    print("="*70)
    print(" Instrucciones: Escribe código (ej: int x = 10 + 5;)")
    print(" Comandos: 'tabla' (ver memoria), 'salir' (finalizar)")
    print("="*70)

    while True:
        try:
            entrada = input("\n📝 FUENTE >>> ")

            if entrada.lower() == 'salir': break
            if entrada.lower() == 'tabla':
                analizador_semantico.tabla_simbolos.mostrar()
                continue
            if not entrada.strip(): continue

            print("\n" + "·"*70)
            print(f"{'INICIANDO PROCESO DE COMPILACIÓN':^70}")
            print("·"*70)

            # --- 1. FASE LÉXICA (IDENTIFICACIÓN) ---
            print("\n[FASE 1: LÉXICO]")
            lexer = Lexer()
            tokens = lexer.analizar(entrada)
            
            # Mostramos cómo el Lexer ignoró espacios y clasificó cada cosa
            for t in tokens:
                if t.type.name != 'EOF':
                    print(f"  → Token detectado: {t.type.name:<15} | Valor: '{t.value}'")
            
            print(f"✔ Lexer finalizado: Espacios omitidos y {len(tokens)-1} componentes identificados.")

            # --- 2. FASE SINTÁCTICA (ESTRUCTURA) ---
            print("\n[FASE 2: SINTÁCTICO]")
            parser = Parser(tokens)
            arbol_ast = parser.parsear()
            
            # Mostramos los pasos que el Parser registró al "armar" la oración
            for paso in parser.log_pasos:
                print(f"  → {paso}")

            if parser.errores:
                print(f"\n❌ ERROR DE ESTRUCTURA:")
                for err in parser.errores: print(f"     └─ {err}")
                continue
            
            print("✔ Parser finalizado: La jerarquía del árbol es válida.")

            # --- 3. FASE SEMÁNTICA (LÓGICA Y MEMORIA) ---
            print("\n[FASE 3: SEMÁNTICO]")
            analizador_semantico.analizar(arbol_ast)
            
            # Aquí se muestra el proceso de tu Tabla de Símbolos
            if analizador_semantico.log_pasos:
                for paso in analizador_semantico.log_pasos:
                    print(f"  → {paso}")
                analizador_semantico.log_pasos = [] # Limpiar logs

            if analizador_semantico.errores:
                print(f"\n❌ ERROR DE LÓGICA:")
                for err in analizador_semantico.errores: 
                    print(f"     └─ {err}")
                analizador_semantico.errores = [] 
            else:
                print("✔ Semántico finalizado: Datos guardados en memoria correctamente.")
                print(f"\n✅ COMPILACIÓN EXITOSA: La instrucción ha sido procesada.")

        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO DEL SISTEMA: {e}")

if __name__ == "__main__":
    ejecutar_interactivo()