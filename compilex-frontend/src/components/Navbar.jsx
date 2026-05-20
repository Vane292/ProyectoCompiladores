import { Braces, Github, Wifi, WifiOff } from 'lucide-react'
import { useState, useEffect } from 'react'

function BackendStatus() {
  const [online, setOnline] = useState(null)

  useEffect(() => {
    let cancelled = false
    async function check() {
      try {
        const r = await fetch('/api/health', { signal: AbortSignal.timeout(3000) })
        if (!cancelled) setOnline(r.ok)
      } catch {
        if (!cancelled) setOnline(false)
      }
    }
    check()
    const id = setInterval(check, 10000)
    return () => { cancelled = true; clearInterval(id) }
  }, [])

  return (
    <div className="flex items-center gap-1.5">
      {online === null && (
        <span style={{ color: 'var(--fg-muted)', fontSize: 11, fontFamily: '"JetBrains Mono", monospace' }}>
          verificando…
        </span>
      )}
      {online === true && (
        <>
          <Wifi size={12} style={{ color: 'var(--emerald)' }} />
          <span style={{ color: 'var(--emerald)', fontSize: 11, fontFamily: '"JetBrains Mono", monospace' }}>
            backend online
          </span>
        </>
      )}
      {online === false && (
        <>
          <WifiOff size={12} style={{ color: 'var(--crimson)' }} />
          <span style={{ color: 'var(--crimson)', fontSize: 11, fontFamily: '"JetBrains Mono", monospace' }}>
            backend offline
          </span>
        </>
      )}
    </div>
  )
}

export default function Navbar() {
  return (
    <header
      className="flex items-center justify-between px-4 py-0"
      style={{
        height: 44,
        background: 'var(--bg-elevated)',
        borderBottom: '1px solid var(--bg-border)',
        flexShrink: 0,
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-2">
        <div
          className="w-6 h-6 rounded flex items-center justify-center"
          style={{ background: 'var(--plasma-glow)', border: '1px solid rgba(88,166,255,0.3)' }}
        >
          <Braces size={13} style={{ color: 'var(--plasma)' }} />
        </div>
        <span
          style={{
            fontFamily: '"Space Mono", monospace',
            fontWeight: 700,
            fontSize: 14,
            letterSpacing: '0.06em',
            color: 'var(--fg-emphasis)',
          }}
        >
          COMPILE<span style={{ color: 'var(--plasma)' }}>X</span>
        </span>
        <span
          className="ml-1 px-1.5 py-0.5 rounded text-xs"
          style={{
            background: 'rgba(88,166,255,0.1)',
            color: 'var(--plasma)',
            border: '1px solid rgba(88,166,255,0.2)',
            fontFamily: '"Space Mono", monospace',
            fontSize: 9,
            letterSpacing: '0.06em',
            fontWeight: 700,
          }}
        >
          v1.0
        </span>
      </div>

      {/* Center: breadcrumb */}
      <div
        className="hidden md:flex items-center gap-1.5 text-xs"
        style={{ color: 'var(--fg-muted)', fontFamily: '"JetBrains Mono", monospace' }}
      >
        <span>Analizador Léxico</span>
        <span>·</span>
        <span>Sintáctico</span>
        <span>·</span>
        <span>Semántico</span>
      </div>

      {/* Right: status + github */}
      <div className="flex items-center gap-4">
        <BackendStatus />
        <a
          href="#"
          style={{ color: 'var(--fg-muted)', transition: 'color 150ms ease-out' }}
          onMouseEnter={e => e.currentTarget.style.color = 'var(--fg-default)'}
          onMouseLeave={e => e.currentTarget.style.color = 'var(--fg-muted)'}
        >
          <Github size={15} />
        </a>
      </div>
    </header>
  )
}
