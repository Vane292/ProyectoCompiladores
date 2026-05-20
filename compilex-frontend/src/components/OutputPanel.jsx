import { useState } from 'react'
import { FileDown, Loader2, CheckCircle2, XCircle, AlertTriangle, Terminal, Clock } from 'lucide-react'

/* ── Phase pill ──────────────────────────────────────────── */
const PHASE_COLORS = {
  'Léxico':     { bg: 'rgba(88, 166, 255, 0.12)', color: '#58A6FF', border: 'rgba(88,166,255,0.25)' },
  'Sintáctico': { bg: 'rgba(188, 140, 255, 0.12)', color: '#BC8CFF', border: 'rgba(188,140,255,0.25)' },
  'Semántico':  { bg: 'rgba(255, 166, 87, 0.12)',  color: '#FFA657', border: 'rgba(255,166,87,0.25)' },
}

function PhasePill({ phase }) {
  const c = PHASE_COLORS[phase] || { bg: 'rgba(110,118,129,0.12)', color: '#8B949E', border: 'rgba(110,118,129,0.25)' }
  return (
    <span
      className="inline-block px-1.5 py-0.5 rounded text-xs flex-shrink-0"
      style={{ background: c.bg, color: c.color, border: `1px solid ${c.border}`, fontFamily: '"Space Mono", monospace', fontSize: 9, letterSpacing: '0.06em', fontWeight: 700 }}
    >
      {phase.toUpperCase()}
    </span>
  )
}

/* ── Verdict banner ──────────────────────────────────────── */
function VerdictBanner({ valid, elapsedMs }) {
  if (valid === undefined || valid === null) return null

  return (
    <div
      className="relative overflow-hidden rounded-lg p-4 flex items-center gap-3 noise"
      style={{
        background: valid
          ? 'linear-gradient(135deg, rgba(35,134,54,0.25) 0%, rgba(63,185,80,0.1) 100%)'
          : 'linear-gradient(135deg, rgba(218,54,51,0.25) 0%, rgba(248,81,73,0.1) 100%)',
        border: `1px solid ${valid ? 'rgba(63,185,80,0.35)' : 'rgba(248,81,73,0.35)'}`,
        boxShadow: valid
          ? '0 0 30px rgba(63,185,80,0.08), inset 0 1px 0 rgba(63,185,80,0.1)'
          : '0 0 30px rgba(248,81,73,0.08), inset 0 1px 0 rgba(248,81,73,0.1)',
        animation: 'fadeUp 0.25s cubic-bezier(0.23, 1, 0.32, 1) forwards',
      }}
    >
      {valid
        ? <CheckCircle2 size={24} style={{ color: 'var(--emerald)', flexShrink: 0 }} />
        : <XCircle      size={24} style={{ color: 'var(--crimson)', flexShrink: 0 }} />
      }
      <div>
        <div
          style={{
            fontFamily: '"Space Mono", monospace',
            fontWeight: 700,
            fontSize: 15,
            letterSpacing: '0.05em',
            color: valid ? 'var(--emerald-glow, #56D364)' : 'var(--crimson-glow, #FF7B72)',
          }}
        >
          CÓDIGO {valid ? 'VÁLIDO' : 'INVÁLIDO'}
        </div>
        <div style={{ color: 'var(--fg-muted)', fontSize: 11, marginTop: 2 }}>
          {valid
            ? 'El análisis completo no encontró errores.'
            : 'Se detectaron errores durante el análisis.'}
          {elapsedMs != null && (
            <span className="ml-2 inline-flex items-center gap-1" style={{ color: 'var(--fg-muted)' }}>
              <Clock size={10} /> {elapsedMs}ms
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

/* ── Error console ───────────────────────────────────────── */
function ErrorConsole({ errors }) {
  if (!errors || errors.length === 0) {
    return (
      <div
        className="flex items-center gap-2 px-3 py-2 rounded"
        style={{ background: 'rgba(63,185,80,0.06)', border: '1px solid rgba(63,185,80,0.15)' }}
      >
        <CheckCircle2 size={13} style={{ color: 'var(--emerald)' }} />
        <span style={{ color: 'var(--emerald)', fontSize: 12, fontFamily: '"JetBrains Mono", monospace' }}>
          Sin errores detectados.
        </span>
      </div>
    )
  }

  return (
    <div
      className="rounded overflow-hidden"
      style={{ border: '1px solid var(--bg-border)' }}
    >
      {/* Console header */}
      <div
        className="flex items-center gap-2 px-3 py-1.5"
        style={{ background: 'var(--bg-elevated)', borderBottom: '1px solid var(--bg-border)' }}
      >
        <Terminal size={11} style={{ color: 'var(--crimson)' }} />
        <span style={{ color: 'var(--fg-muted)', fontFamily: '"Space Mono", monospace', fontSize: 10, letterSpacing: '0.06em', fontWeight: 700 }}>
          ERRORES ({errors.length})
        </span>
      </div>

      {/* Error list */}
      <div style={{ maxHeight: 240, overflowY: 'auto', background: 'var(--bg-base)' }}>
        {errors.map((err, i) => (
          <div
            key={i}
            className="stagger-row flex items-start gap-2 px-3 py-2"
            style={{ borderBottom: i < errors.length - 1 ? '1px solid rgba(33,38,45,0.8)' : 'none' }}
          >
            <AlertTriangle size={12} style={{ color: 'var(--amber)', flexShrink: 0, marginTop: 1 }} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-0.5">
                <PhasePill phase={err.phase} />
                {err.line != null && (
                  <span
                    className="text-xs"
                    style={{ color: 'var(--fg-muted)', fontFamily: '"JetBrains Mono", monospace', fontSize: 11 }}
                  >
                    línea {err.line}{err.column != null ? `:${err.column}` : ''}
                  </span>
                )}
              </div>
              <p
                className="text-xs break-words"
                style={{ color: 'var(--fg-default)', fontFamily: '"JetBrains Mono", monospace', lineHeight: 1.5 }}
              >
                {err.message || JSON.stringify(err)}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ── PDF Export button ───────────────────────────────────── */
function PDFButton({ onClick, status }) {
  const isLoading = status === 'loading'
  const isSuccess = status === 'success'
  const isError   = status === 'error'

  const label = isLoading ? 'Generando…' : isSuccess ? '¡Descargado!' : isError ? 'Error al generar' : 'Exportar PDF'
  const icon  = isLoading
    ? <Loader2 size={13} className="animate-spin" />
    : isSuccess
    ? <CheckCircle2 size={13} />
    : <FileDown size={13} />

  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className="flex items-center gap-2 px-4 py-2 rounded-md text-sm font-semibold w-full justify-center"
      style={{
        fontFamily: '"Space Mono", monospace',
        fontSize: 12,
        letterSpacing: '0.04em',
        background: isSuccess ? 'rgba(63,185,80,0.15)' : isError ? 'rgba(248,81,73,0.15)' : 'var(--bg-border)',
        color:  isSuccess ? 'var(--emerald)' : isError ? 'var(--crimson)' : 'var(--fg-default)',
        border: `1px solid ${isSuccess ? 'rgba(63,185,80,0.3)' : isError ? 'rgba(248,81,73,0.3)' : 'var(--bg-border)'}`,
        cursor: isLoading ? 'not-allowed' : 'pointer',
        transition: 'background 150ms ease-out, color 150ms ease-out, border-color 150ms ease-out, transform 100ms ease-out',
      }}
      onMouseEnter={e => { if (!isLoading && !isSuccess) { e.currentTarget.style.background = '#30363D'; e.currentTarget.style.color = '#fff' } }}
      onMouseLeave={e => { if (!isLoading && !isSuccess) { e.currentTarget.style.background = 'var(--bg-border)'; e.currentTarget.style.color = 'var(--fg-default)' } }}
      onMouseDown={e => { if (!isLoading) e.currentTarget.style.transform = 'scale(0.98)' }}
      onMouseUp={e => { e.currentTarget.style.transform = 'scale(1)' }}
    >
      {icon} {label}
    </button>
  )
}

/* ── Main OutputPanel ────────────────────────────────────── */
export default function OutputPanel({ result, allErrors, elapsedMs, pdfStatus, onExportPDF, apiError }) {
  const overallValid = result?.overall_valid ?? null

  return (
    <div className="panel flex flex-col h-full">
      {/* Header */}
      <div className="panel-header">
        <Terminal size={12} style={{ color: 'var(--emerald)' }} />
        <span>Salida & Veredicto</span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-4">
        {/* API error */}
        {apiError && (
          <div
            className="flex items-start gap-2 p-3 rounded"
            style={{ background: 'rgba(248,81,73,0.1)', border: '1px solid rgba(248,81,73,0.25)' }}
          >
            <XCircle size={14} style={{ color: 'var(--crimson)', flexShrink: 0, marginTop: 1 }} />
            <div>
              <div style={{ color: 'var(--crimson)', fontFamily: '"Space Mono", monospace', fontSize: 10, fontWeight: 700, letterSpacing: '0.06em', marginBottom: 2 }}>
                ERROR DE CONEXIÓN
              </div>
              <p style={{ color: 'var(--fg-muted)', fontSize: 12, fontFamily: '"JetBrains Mono", monospace' }}>{apiError}</p>
            </div>
          </div>
        )}

        {/* Idle state */}
        {!result && !apiError && (
          <div
            className="flex-1 flex flex-col items-center justify-center gap-3 py-10"
            style={{ color: 'var(--fg-muted)' }}
          >
            <div
              className="w-12 h-12 rounded-full flex items-center justify-center"
              style={{ background: 'var(--bg-elevated)', border: '1px solid var(--bg-border)' }}
            >
              <Terminal size={20} style={{ color: 'var(--fg-muted)' }} />
            </div>
            <p style={{ fontSize: 12, textAlign: 'center', lineHeight: 1.6 }}>
              Escribe código en el editor<br />y presiona <span style={{ color: 'var(--plasma)', fontFamily: '"Space Mono", monospace' }}>Compilar</span> para ver los resultados.
            </p>
          </div>
        )}

        {/* Verdict */}
        {result && <VerdictBanner valid={overallValid} elapsedMs={elapsedMs} />}

        {/* Error console */}
        {result && (
          <div>
            <div style={{ color: 'var(--fg-muted)', fontFamily: '"Space Mono", monospace', fontSize: 10, letterSpacing: '0.08em', textTransform: 'uppercase', fontWeight: 700, marginBottom: 8 }}>
              Consola de Errores
            </div>
            <ErrorConsole errors={allErrors} />
          </div>
        )}

        {/* PDF Export */}
        {result && (
          <div style={{ marginTop: 'auto' }}>
            <div style={{ color: 'var(--fg-muted)', fontFamily: '"Space Mono", monospace', fontSize: 10, letterSpacing: '0.08em', textTransform: 'uppercase', fontWeight: 700, marginBottom: 8 }}>
              Exportar Reporte
            </div>
            <PDFButton onClick={onExportPDF} status={pdfStatus} />
            <p style={{ color: 'var(--fg-muted)', fontSize: 11, textAlign: 'center', marginTop: 6 }}>
              Genera un PDF paso a paso con reportlab
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
