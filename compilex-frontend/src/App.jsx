import { useCompiler } from './hooks/useCompiler'
import CodeEditor      from './components/CodeEditor'
import ProcessingPanel from './components/ProcessingPanel'
import OutputPanel     from './components/OutputPanel'
import Navbar          from './components/Navbar'

export default function App() {
  const {
    code, setCode,
    isLoading,
    result,
    error,
    allErrors,
    activeTab, setActiveTab,
    pdfStatus,
    elapsedMs,
    compile,
    exportPDF,
    reset,
  } = useCompiler()

  return (
    <div
      className="flex flex-col"
      style={{ height: '100vh', background: 'var(--bg-base)', overflow: 'hidden' }}
    >
      {/* ── Top bar ──────────────────────────────────────── */}
      <Navbar />

      {/* ── 3-panel grid ─────────────────────────────────── */}
      <main
        className="flex-1 min-h-0 grid gap-2 p-2"
        style={{
          gridTemplateColumns: '1fr 1fr 320px',
          gridTemplateRows: '1fr',
          overflow: 'hidden',
        }}
      >
        {/* Panel 1: Editor */}
        <CodeEditor
          code={code}
          setCode={setCode}
          onCompile={compile}
          onReset={reset}
          isLoading={isLoading}
        />

        {/* Panel 2: Processing */}
        <ProcessingPanel
          result={result}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />

        {/* Panel 3: Output */}
        <OutputPanel
          result={result}
          allErrors={allErrors}
          elapsedMs={elapsedMs}
          pdfStatus={pdfStatus}
          onExportPDF={exportPDF}
          apiError={error}
        />
      </main>

      {/* Loading scanline overlay */}
      {isLoading && (
        <div
          className="fixed inset-0 pointer-events-none"
          style={{ zIndex: 50 }}
        >
          {/* Top progress bar */}
          <div
            style={{
              position: 'absolute',
              top: 0, left: 0,
              height: 2,
              background: 'var(--plasma)',
              boxShadow: '0 0 12px var(--plasma)',
              animation: 'progress 1.5s ease-in-out infinite',
            }}
          />
          <style>{`
            @keyframes progress {
              0%   { width: 0%; left: 0; }
              50%  { width: 70%; left: 0; }
              100% { width: 0%; left: 100%; }
            }
          `}</style>
        </div>
      )}
    </div>
  )
}
