import { useState, useCallback, useRef } from 'react'
import { analyzeCode, generateAndDownloadPDF } from '../lib/api'

const IDLE       = 'idle'
const LOADING    = 'loading'
const SUCCESS    = 'success'
const ERROR      = 'error'

const DEFAULT_CODE = `// Escribe tu código fuente aquí
// Ejemplo básico para probar el compilador:

programa suma {
  entero a = 10;
  entero b = 20;
  entero resultado;

  resultado = a + b;

  si (resultado > 0) {
    imprimir(resultado);
  }
}
`

export function useCompiler() {
  const [code,         setCode]         = useState(DEFAULT_CODE)
  const [status,       setStatus]       = useState(IDLE)
  const [result,       setResult]       = useState(null)
  const [error,        setError]        = useState(null)
  const [activeTab,    setActiveTab]    = useState('lexer')   // 'lexer' | 'parser' | 'semantic'
  const [pdfStatus,    setPdfStatus]    = useState(IDLE)
  const [elapsedMs,    setElapsedMs]    = useState(null)
  const startRef = useRef(null)

  const compile = useCallback(async () => {
    if (!code.trim()) return

    setStatus(LOADING)
    setError(null)
    setResult(null)
    setElapsedMs(null)
    startRef.current = performance.now()

    try {
      const data = await analyzeCode(code)
      const elapsed = Math.round(performance.now() - startRef.current)
      setResult(data)
      setElapsedMs(elapsed)
      setStatus(SUCCESS)
    } catch (err) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        'Error de conexión con el backend.'
      setError(message)
      setStatus(ERROR)
    }
  }, [code])

  const exportPDF = useCallback(async () => {
    if (!code.trim()) return
    setPdfStatus(LOADING)
    try {
      await generateAndDownloadPDF(code)
      setPdfStatus(SUCCESS)
      setTimeout(() => setPdfStatus(IDLE), 2000)
    } catch {
      setPdfStatus(ERROR)
      setTimeout(() => setPdfStatus(IDLE), 2500)
    }
  }, [code])

  const reset = useCallback(() => {
    setStatus(IDLE)
    setResult(null)
    setError(null)
    setElapsedMs(null)
  }, [])

  /* ── Derived: aggregated errors from all phases ── */
  const allErrors = result
    ? [
        ...(result.lexer?.errors   || []).map(e => ({ ...e, phase: 'Léxico' })),
        ...(result.parser?.errors  || []).map(e => ({ ...e, phase: 'Sintáctico' })),
        ...(result.semantic?.errors|| []).map(e => ({ ...e, phase: 'Semántico' })),
      ]
    : []

  return {
    code, setCode,
    status,
    result,
    error,
    allErrors,
    activeTab, setActiveTab,
    pdfStatus,
    elapsedMs,
    compile,
    exportPDF,
    reset,
    isIdle:    status === IDLE,
    isLoading: status === LOADING,
    isSuccess: status === SUCCESS,
    isError:   status === ERROR,
  }
}
