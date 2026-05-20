# ============================================================
#  compilador_backend/api/routes.py  —  REEMPLAZA el archivo actual
# ============================================================
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from core.lexer.Lexer import Lexer
from core.parser.Parser import Parser
from core.semantic.Semantic_analyzer import SemanticAnalyzer
from reports.pdf_manager import generar_reporte_pdf
import os

router = APIRouter()

# ── Modelo de entrada ────────────────────────────────────────
class CodeRequest(BaseModel):
    code: str

# ── Helper: convierte nodos AST a dict serializable ─────────
def ast_to_dict(nodo):
    """Convierte recursivamente cualquier nodo AST en un dict JSON-serializable."""
    if nodo is None:
        return None

    nombre_clase = type(nodo).__name__
    resultado = {"type": nombre_clase}

    # ProgramNode / BlockNode: tienen lista de statements
    if hasattr(nodo, "statements"):
        resultado["children"] = [ast_to_dict(s) for s in nodo.statements if s]
        return resultado

    # BinaryOpNode
    if hasattr(nodo, "left") and hasattr(nodo, "right"):
        resultado["value"]    = nodo.op_token.value if hasattr(nodo, "op_token") else None
        resultado["children"] = [ast_to_dict(nodo.left), ast_to_dict(nodo.right)]
        return resultado

    # VarDeclarationNode
    if hasattr(nodo, "var_name_token") and hasattr(nodo, "type_token"):
        resultado["value"]    = f"{nodo.type_token.value} {nodo.var_name_token.value}"
        resultado["children"] = [ast_to_dict(nodo.value_node)]
        return resultado

    # AssignmentNode
    if hasattr(nodo, "var_name_token") and hasattr(nodo, "op_token"):
        resultado["value"]    = nodo.var_name_token.value
        resultado["children"] = [ast_to_dict(nodo.value_node)]
        return resultado

    # IfNode
    if hasattr(nodo, "condition") and hasattr(nodo, "then_block"):
        hijos = [ast_to_dict(nodo.condition), ast_to_dict(nodo.then_block)]
        if nodo.else_block:
            hijos.append(ast_to_dict(nodo.else_block))
        resultado["children"] = hijos
        return resultado

    # PrintNode
    if hasattr(nodo, "value_node") and nombre_clase == "PrintNode":
        resultado["children"] = [ast_to_dict(nodo.value_node)]
        return resultado

    # NumberNode / StringNode
    if hasattr(nodo, "value"):
        resultado["value"] = str(nodo.value)
        return resultado

    # IdentifierNode
    if hasattr(nodo, "name"):
        resultado["value"] = nodo.name
        return resultado

    # UnaryOpNode
    if hasattr(nodo, "node") and hasattr(nodo, "op_token"):
        resultado["value"]    = nodo.op_token.value
        resultado["children"] = [ast_to_dict(nodo.node)]
        return resultado

    return resultado


# ── Helper: extrae errores con línea y mensaje ───────────────
def parsear_errores(lista_errores):
    """
    Convierte la lista de strings de error del backend al formato
    { line, column, message } que espera el frontend.
    """
    resultado = []
    for err in lista_errores:
        # Intentar extraer línea del formato "... en 3:5"
        import re
        m = re.search(r"en\s+(\d+):?(\d*)", err)
        line   = int(m.group(1)) if m else None
        column = int(m.group(2)) if (m and m.group(2)) else None
        resultado.append({"line": line, "column": column, "message": err})
    return resultado


# ── POST /analyze ─────────────────────────────────────────────
@router.post("/analyze")
async def analyze(request: CodeRequest):
    """
    Punto de entrada principal.
    Recibe { "code": "..." } y ejecuta los 3 análisis.
    Retorna la estructura completa que consume el frontend.
    """
    codigo = request.code.strip()
    if not codigo:
        raise HTTPException(status_code=400, detail="El campo 'code' no puede estar vacío.")

    # ── 1. LÉXICO ──────────────────────────────────────────
    lexer  = Lexer()
    tokens = lexer.analizar(codigo)

    lexer_errores = parsear_errores(lexer.errores)
    tokens_dict   = [
        t.to_dict() for t in tokens
        if t.type.name != "EOF"
    ]
    log_lexico = "\n".join(lexer.log_pasos)

    # ── 2. SINTÁCTICO ──────────────────────────────────────
    parser    = Parser(tokens)
    arbol_ast = parser.parsear()

    parser_errores = parsear_errores(parser.errores)
    parser_valido  = len(parser_errores) == 0
    ast_dict       = ast_to_dict(arbol_ast) if parser_valido else None

    # ── 3. SEMÁNTICO ───────────────────────────────────────
    # Solo ejecutar si no hay errores sintácticos
    semantic_errores  = []
    symbol_table_list = []
    semantic_valido   = False

    if parser_valido:
        semantico = SemanticAnalyzer()
        semantico.analizar(arbol_ast)

        semantic_errores = parsear_errores(semantico.errores)
        semantic_valido  = len(semantic_errores) == 0

        # Convertir la tabla de símbolos a lista de dicts
        for nombre, datos in semantico.tabla_simbolos.tabla.items():
            symbol_table_list.append({
                "name":  nombre,
                "type":  datos["tipo"],
                "value": str(datos["valor"]) if datos["inicializada"] else "NULL",
                "scope": "global",
                "line":  None,   # El backend actual no almacena línea en la tabla
            })

    # ── Veredicto global ───────────────────────────────────
    overall_valid = (
        len(lexer_errores) == 0 and
        parser_valido and
        semantic_valido
    )

    return {
        "lexer": {
            "tokens": tokens_dict,
            "log":    log_lexico,
            "errors": lexer_errores,
        },
        "parser": {
            "valid":  parser_valido,
            "ast":    ast_dict,
            "errors": parser_errores,
        },
        "semantic": {
            "valid":        semantic_valido,
            "symbol_table": symbol_table_list,
            "errors":       semantic_errores,
        },
        "overall_valid": overall_valid,
    }


# ── POST /report/pdf ──────────────────────────────────────────
@router.post("/report/pdf")
async def report_pdf(request: CodeRequest):
    """
    Genera el PDF del reporte y lo devuelve como descarga.
    Primero ejecuta el análisis completo, luego llama al gestor de PDF.
    """
    # Reutilizamos el análisis completo
    resultado = await analyze(request)

    pdf_path = generar_reporte_pdf(
        codigo=request.code,
        resultado=resultado,
    )

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="No se pudo generar el archivo PDF.")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename="reporte_compilador.pdf",
    )


# ── GET /health ───────────────────────────────────────────────
@router.get("/health")
async def health():
    """Ping para el indicador de estado en la Navbar del frontend."""
    return {"status": "ok", "message": "Backend activo"}