import axios from 'axios'

// Base URL — Vite proxy rewrites /api → http://localhost:8000
const BASE = '/api'

const client = axios.create({
  baseURL: BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

/**
 * POST /analyze
 * Envía el código fuente al backend y recibe los tres análisis.
 *
 * Respuesta esperada del backend:
 * {
 *   lexer: {
 *     tokens: [ { type, value, line, column } ],
 *     log:    string,
 *     errors: [ { line, message } ]
 *   },
 *   parser: {
 *     valid:  boolean,
 *     ast:    object | null,
 *     errors: [ { line, message } ]
 *   },
 *   semantic: {
 *     valid:        boolean,
 *     symbol_table: [ { name, type, scope, line } ],
 *     errors:       [ { line, message } ]
 *   },
 *   overall_valid: boolean
 * }
 */
export async function analyzeCode(sourceCode) {
  const { data } = await client.post('/analyze', { code: sourceCode })
  return data
}

/**
 * GET /report/pdf
 * Descarga el último reporte generado como PDF.
 * El backend usa reportlab/fpdf para crearlo.
 */
export async function downloadPDF() {
  const response = await client.get('/report/pdf', { responseType: 'blob' })
  const url = window.URL.createObjectURL(
    new Blob([response.data], { type: 'application/pdf' })
  )
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `compilador_report_${Date.now()}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

/**
 * POST /report/pdf  (alternativa si el backend necesita el código para generar el PDF)
 */
export async function generateAndDownloadPDF(sourceCode) {
  const response = await client.post(
    '/report/pdf',
    { code: sourceCode },
    { responseType: 'blob' }
  )
  const url = window.URL.createObjectURL(
    new Blob([response.data], { type: 'application/pdf' })
  )
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `compilador_report_${Date.now()}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
