import { useState } from 'react'
import { ChevronRight, Cpu } from 'lucide-react'

/* ── Token color map ─────────────────────────────────────── */
const TOKEN_CLASS = {
  KEYWORD:    'token-keyword',
  STRING:     'token-string',
  NUMBER:     'token-number',
  INTEGER:    'token-number',
  FLOAT:      'token-number',
  OPERATOR:   'token-operator',
  IDENTIFIER: 'token-ident',
  COMMENT:    'token-comment',
  PUNCT:      'token-punct',
  DELIMITER:  'token-punct',
  LPAREN:     'token-punct',
  RPAREN:     'token-punct',
  LBRACE:     'token-punct',
  RBRACE:     'token-punct',
  SEMICOLON:  'token-punct',
  COMMA:      'token-punct',
}

function getTokenClass(type = '') {
  return TOKEN_CLASS[type.toUpperCase()] || 'token-default'
}

/* ── Tab button ──────────────────────────────────────────── */
function TabBtn({ id, label, active, onClick, errorCount = 0 }) {
  return (
    <button
      onClick={() => onClick(id)}
      className={`relative px-3 py-2 text-xs transition-colors ${active ? 'tab-active' : ''}`}
      style={{
        fontFamily: '"Space Mono", monospace',
        fontWeight: active ? 700 : 400,
        fontSize: '11px',
        letterSpacing: '0.06em',
        color: active ? 'var(--fg-emphasis)' : 'var(--fg-muted)',
        background: 'transparent',
        border: 'none',
        cursor: 'pointer',
        transition: 'color 150ms ease-out',
      }}
      onMouseEnter={e => { if (!active) e.currentTarget.style.color = 'var(--fg-default)' }}
      onMouseLeave={e => { if (!active) e.currentTarget.style.color = 'var(--fg-muted)' }}
    >
      {label}
      {errorCount > 0 && (
        <span
          className="ml-1.5 inline-flex items-center justify-center rounded-full text-xs"
          style={{
            background: 'var(--crimson)',
            color: '#fff',
            width: 16, height: 16,
            fontSize: 10,
            fontFamily: '"JetBrains Mono", monospace',
            verticalAlign: 'middle',
          }}
        >
          {errorCount}
        </span>
      )}
    </button>
  )
}

/* ── Lexer view ──────────────────────────────────────────── */
function LexerView({ data }) {
  if (!data) return <EmptyState message="Ejecuta el compilador para ver los tokens." />

  const tokens = data.tokens || []
  const log    = data.log    || ''

  return (
    <div className="flex flex-col gap-4 p-3 h-full overflow-y-auto">
      {/* Token table */}
      <div>
        <SectionLabel>Tabla de Tokens ({tokens.length})</SectionLabel>
        <div className="overflow-x-auto">
          <table className="w-full text-xs" style={{ borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--bg-border)' }}>
                {['#', 'Tipo', 'Valor', 'Línea', 'Col'].map(h => (
                  <th key={h} className="text-left px-2 py-1.5" style={{ color: 'var(--fg-muted)', fontFamily: '"Space Mono", monospace', fontSize: '10px', fontWeight: 700, letterSpacing: '0.06em' }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tokens.map((tok, i) => (
                <tr
                  key={i}
                  className="stagger-row"
                  style={{ borderBottom: '1px solid rgba(33,38,45,0.6)' }}
                >
                  <td className="px-2 py-1" style={{ color: 'var(--fg-muted)', fontFamily: '"JetBrains Mono", monospace' }}>{i + 1}</td>
                  <td className="px-2 py-1">
                    <span className={`font-medium ${getTokenClass(tok.type)}`} style={{ fontFamily: '"JetBrains Mono", monospace' }}>
                      {tok.type}
                    </span>
                  </td>
                  <td className="px-2 py-1">
                    <code className="token-ident" style={{ fontFamily: '"JetBrains Mono", monospace' }}>
                      {String(tok.value).length > 28 ? String(tok.value).slice(0, 28) + '…' : tok.value}
                    </code>
                  </td>
                  <td className="px-2 py-1" style={{ color: 'var(--fg-muted)', fontFamily: '"JetBrains Mono", monospace' }}>{tok.line ?? '—'}</td>
                  <td className="px-2 py-1" style={{ color: 'var(--fg-muted)', fontFamily: '"JetBrains Mono", monospace' }}>{tok.column ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Tokenization log */}
      {log && (
        <div>
          <SectionLabel>Log de Tokenización</SectionLabel>
          <pre
            className="p-3 rounded text-xs overflow-x-auto"
            style={{
              background: 'var(--bg-base)',
              border: '1px solid var(--bg-border)',
              color: 'var(--fg-muted)',
              fontFamily: '"JetBrains Mono", monospace',
              lineHeight: 1.6,
              maxHeight: 180,
              overflowY: 'auto',
              whiteSpace: 'pre-wrap',
            }}
          >
            {log}
          </pre>
        </div>
      )}
    </div>
  )
}

/* ── AST Node recursive renderer ─────────────────────────── */
function ASTNode({ node, depth = 0 }) {
  const [open, setOpen] = useState(true)
  if (!node || typeof node !== 'object') {
    return (
      <span style={{ color: 'var(--amber)', fontFamily: '"JetBrains Mono", monospace', fontSize: 12 }}>
        {JSON.stringify(node)}
      </span>
    )
  }

  const { type, value, children, ...rest } = node
  const hasChildren = Array.isArray(children) && children.length > 0

  return (
    <div style={{ paddingLeft: depth * 14 }}>
      <div
        className="flex items-center gap-1 cursor-pointer py-0.5 rounded"
        onClick={() => hasChildren && setOpen(o => !o)}
        style={{ color: 'var(--plasma)', fontSize: 12, fontFamily: '"JetBrains Mono", monospace' }}
        onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.04)'}
        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
      >
        {hasChildren && (
          <ChevronRight
            size={10}
            style={{ flexShrink: 0, transition: 'transform 150ms ease-out', transform: open ? 'rotate(90deg)' : 'rotate(0deg)' }}
          />
        )}
        {!hasChildren && <span style={{ width: 10 }} />}
        <span style={{ color: 'var(--violet)' }}>{type || 'Node'}</span>
        {value !== undefined && (
          <span style={{ color: 'var(--amber)', marginLeft: 6 }}>= {JSON.stringify(value)}</span>
        )}
      </div>
      {open && hasChildren && (
        <div>
          {children.map((child, i) => <ASTNode key={i} node={child} depth={depth + 1} />)}
        </div>
      )}
    </div>
  )
}

/* ── Parser view ─────────────────────────────────────────── */
function ParserView({ data }) {
  if (!data) return <EmptyState message="Ejecuta el compilador para ver el análisis sintáctico." />

  const ast   = data.ast
  const valid = data.valid

  return (
    <div className="flex flex-col gap-4 p-3 h-full overflow-y-auto">
      <div className="flex items-center gap-2">
        <ValidBadge valid={valid} />
        <span style={{ color: 'var(--fg-muted)', fontSize: 12 }}>Análisis Sintáctico</span>
      </div>

      {ast && (
        <div>
          <SectionLabel>Árbol de Sintaxis Abstracta (AST)</SectionLabel>
          <div
            className="p-3 rounded overflow-auto"
            style={{
              background: 'var(--bg-base)',
              border: '1px solid var(--bg-border)',
              maxHeight: 360,
              minHeight: 80,
            }}
          >
            <ASTNode node={ast} />
          </div>
        </div>
      )}

      {!ast && valid && (
        <div style={{ color: 'var(--fg-muted)', fontSize: 12, fontStyle: 'italic' }}>
          El backend no retornó un AST serializable.
        </div>
      )}
    </div>
  )
}

/* ── Semantic view ───────────────────────────────────────── */
function SemanticView({ data }) {
  if (!data) return <EmptyState message="Ejecuta el compilador para ver el análisis semántico." />

  const table = data.symbol_table || []
  const valid = data.valid

  return (
    <div className="flex flex-col gap-4 p-3 h-full overflow-y-auto">
      <div className="flex items-center gap-2">
        <ValidBadge valid={valid} />
        <span style={{ color: 'var(--fg-muted)', fontSize: 12 }}>Análisis Semántico</span>
      </div>

      {table.length > 0 && (
        <div>
          <SectionLabel>Tabla de Símbolos ({table.length})</SectionLabel>
          <div className="overflow-x-auto">
            <table className="w-full text-xs" style={{ borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--bg-border)' }}>
                  {['Nombre', 'Tipo', 'Ámbito', 'Línea'].map(h => (
                    <th key={h} className="text-left px-2 py-1.5" style={{ color: 'var(--fg-muted)', fontFamily: '"Space Mono", monospace', fontSize: '10px', fontWeight: 700, letterSpacing: '0.06em' }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {table.map((sym, i) => (
                  <tr key={i} className="stagger-row" style={{ borderBottom: '1px solid rgba(33,38,45,0.6)' }}>
                    <td className="px-2 py-1 token-ident" style={{ fontFamily: '"JetBrains Mono", monospace' }}>{sym.name}</td>
                    <td className="px-2 py-1 token-keyword" style={{ fontFamily: '"JetBrains Mono", monospace' }}>{sym.type}</td>
                    <td className="px-2 py-1" style={{ color: 'var(--violet)', fontFamily: '"JetBrains Mono", monospace' }}>{sym.scope || 'global'}</td>
                    <td className="px-2 py-1" style={{ color: 'var(--fg-muted)', fontFamily: '"JetBrains Mono", monospace' }}>{sym.line ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

/* ── Shared sub-components ───────────────────────────────── */
function ValidBadge({ valid }) {
  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold"
      style={{
        background: valid ? 'rgba(63,185,80,0.15)' : 'rgba(248,81,73,0.15)',
        color: valid ? 'var(--emerald)' : 'var(--crimson)',
        fontFamily: '"Space Mono", monospace',
        fontSize: 10,
        letterSpacing: '0.04em',
        border: `1px solid ${valid ? 'rgba(63,185,80,0.3)' : 'rgba(248,81,73,0.3)'}`,
      }}
    >
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor', display: 'inline-block' }} />
      {valid ? 'VÁLIDO' : 'INVÁLIDO'}
    </span>
  )
}

function SectionLabel({ children }) {
  return (
    <div className="mb-1.5" style={{ color: 'var(--fg-muted)', fontFamily: '"Space Mono", monospace', fontSize: 10, letterSpacing: '0.08em', textTransform: 'uppercase', fontWeight: 700 }}>
      {children}
    </div>
  )
}

function EmptyState({ message }) {
  return (
    <div className="flex-1 flex items-center justify-center" style={{ color: 'var(--fg-muted)', fontSize: 12, fontStyle: 'italic', padding: 24, textAlign: 'center' }}>
      {message}
    </div>
  )
}

/* ── Main ProcessingPanel component ─────────────────────── */
export default function ProcessingPanel({ result, activeTab, setActiveTab }) {
  const lexerErrors    = result?.lexer?.errors?.length    || 0
  const parserErrors   = result?.parser?.errors?.length   || 0
  const semanticErrors = result?.semantic?.errors?.length || 0

  const TABS = [
    { id: 'lexer',    label: 'Léxico',     errors: lexerErrors },
    { id: 'parser',   label: 'Sintáctico', errors: parserErrors },
    { id: 'semantic', label: 'Semántico',  errors: semanticErrors },
  ]

  return (
    <div className="panel flex flex-col h-full">
      {/* Header */}
      <div className="panel-header">
        <Cpu size={12} style={{ color: 'var(--amber)' }} />
        <span>Procesamiento</span>
      </div>

      {/* Tab bar */}
      <div
        className="flex items-center gap-0 px-2"
        style={{ background: 'var(--bg-elevated)', borderBottom: '1px solid var(--bg-border)' }}
      >
        {TABS.map(tab => (
          <TabBtn
            key={tab.id}
            id={tab.id}
            label={tab.label}
            active={activeTab === tab.id}
            onClick={setActiveTab}
            errorCount={tab.errors}
          />
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {activeTab === 'lexer'    && <LexerView    data={result?.lexer}    />}
        {activeTab === 'parser'   && <ParserView   data={result?.parser}   />}
        {activeTab === 'semantic' && <SemanticView data={result?.semantic} />}
      </div>
    </div>
  )
}
