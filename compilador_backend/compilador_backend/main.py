# ============================================================
#  compilador_backend/main.py  —  REEMPLAZA el archivo actual
# ============================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="CompileX — Backend",
    description="Analizador Léxico, Sintáctico y Semántico",
    version="1.0.0"
)

# ── CORS ────────────────────────────────────────────────────
# Permite que el frontend en localhost:5173 (Vite) consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # CRA / alternativa
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rutas ────────────────────────────────────────────────────
app.include_router(router)

# ── Inicio (modo consola, solo si se corre directamente) ─────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)