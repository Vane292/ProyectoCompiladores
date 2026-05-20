import { useRef } from 'react'
import Editor from '@monaco-editor/react'
import { Play, RotateCcw, Loader2, Code2 } from 'lucide-react'

const MONACO_THEME = {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment',              foreground: '6E7681', fontStyle: 'italic' },
    { token: 'keyword',              foreground: 'FF7B72', fontStyle: 'bold' },
    { token: 'string',               foreground: 'A5D6FF' },
    { token: 'number',               foreground: '79C0FF' },
    { token: 'identifier',           foreground: 'FFA657' },
    { token: 'delimiter',            foreground: '8B949E' },
    { token: 'operator',             foreground: 'FF7B72' },
  ],
  colors: {
    'editor.background':            '#0D1117',
    'editor.foreground':            '#C9D1D9',
    'editorLineNumber.foreground':  '#484F58',
    'editorLineNumber.activeForeground': '#8B949E',
    'editor.selectionBackground':   '#264F78',
    'editor.lineHighlightBackground': '#161B22',
    'editorCursor.foreground':      '#58A6FF',
    'editorIndentGuide.background': '#21262D',
    'editorIndentGuide.activeBackground': '#30363D',
    'scrollbarSlider.background':   '#21262D',
    'scrollbarSlider.hoverBackground': '#30363D',
  },
}

export default function CodeEditor({ code, setCode, onCompile, onReset, isLoading }) {
  const editorRef = useRef(null)

  function handleMount(editor, monaco) {
    editorRef.current = editor
    monaco.editor.defineTheme('compilex-dark', MONACO_THEME)
    monaco.editor.setTheme('compilex-dark')
    // Keyboard shortcut: Ctrl+Enter / Cmd+Enter → compile
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, onCompile)
  }

  return (
    <div className="panel flex flex-col h-full">
      {/* Header */}
      <div className="panel-header justify-between">
        <div className="flex items-center gap-2">
          <Code2 size={12} className="text-plasma-DEFAULT" style={{ color: 'var(--plasma)' }} />
          <span>Editor de Código</span>
          <span className="ml-1 opacity-40">·</span>
          <span className="opacity-40 normal-case font-normal tracking-normal" style={{ fontFamily: 'inherit', fontSize: '11px' }}>
            Ctrl+Enter para compilar
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          {/* Dot indicators */}
          <span className="w-2.5 h-2.5 rounded-full bg-[#FF5F57]" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#FEBC2E]" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#28C840]" />
        </div>
      </div>

      {/* Monaco Editor */}
      <div className="flex-1 min-h-0">
        <Editor
          defaultLanguage="plaintext"
          value={code}
          onChange={(val) => setCode(val || '')}
          onMount={handleMount}
          options={{
            fontSize: 13,
            fontFamily: '"JetBrains Mono", "Fira Code", monospace',
            fontLigatures: true,
            lineNumbers: 'on',
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            padding: { top: 12, bottom: 12 },
            renderLineHighlight: 'line',
            cursorBlinking: 'smooth',
            cursorSmoothCaretAnimation: 'on',
            smoothScrolling: true,
            tabSize: 2,
            wordWrap: 'off',
            scrollbar: {
              verticalScrollbarSize: 6,
              horizontalScrollbarSize: 6,
            },
            bracketPairColorization: { enabled: true },
            guides: { indentation: true },
            renderWhitespace: 'selection',
          }}
        />
      </div>

      {/* Action bar */}
      <div
        className="flex items-center gap-2 px-3 py-2.5"
        style={{ borderTop: '1px solid var(--bg-border)', background: 'var(--bg-elevated)' }}
      >
        <button
          onClick={onCompile}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all"
          style={{
            background: isLoading ? '#1F6FEB' : 'var(--plasma)',
            color: '#fff',
            fontFamily: '"Space Mono", monospace',
            letterSpacing: '0.04em',
            opacity: isLoading ? 0.8 : 1,
            transform: 'none',
            transition: 'background 150ms ease-out, transform 100ms ease-out, opacity 150ms ease-out',
            cursor: isLoading ? 'not-allowed' : 'pointer',
          }}
          onMouseDown={e => { if (!isLoading) e.currentTarget.style.transform = 'scale(0.97)' }}
          onMouseUp={e => { e.currentTarget.style.transform = 'scale(1)' }}
          onMouseLeave={e => { e.currentTarget.style.transform = 'scale(1)' }}
        >
          {isLoading
            ? <><Loader2 size={12} className="animate-spin" /> Compilando…</>
            : <><Play size={12} style={{ fill: '#fff' }} /> Compilar</>
          }
        </button>

        <button
          onClick={onReset}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-all"
          style={{
            background: 'var(--bg-border)',
            color: 'var(--fg-muted)',
            fontFamily: '"Space Mono", monospace',
            letterSpacing: '0.04em',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            transition: 'background 150ms ease-out, color 150ms ease-out',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.background = '#30363D'
            e.currentTarget.style.color = 'var(--fg-default)'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = 'var(--bg-border)'
            e.currentTarget.style.color = 'var(--fg-muted)'
          }}
        >
          <RotateCcw size={11} /> Limpiar
        </button>

        {/* Line/col info */}
        <div
          className="ml-auto text-xs"
          style={{ color: 'var(--fg-muted)', fontFamily: '"JetBrains Mono", monospace' }}
        >
          {code.split('\n').length} líneas · {code.length} chars
        </div>
      </div>
    </div>
  )
}
