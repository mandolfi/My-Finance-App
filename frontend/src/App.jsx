import { useState, useEffect } from 'react'
import CardsRiepilogo from './components/CardsRiepilogo'

const API_URL = 'https://automatic-space-fishstick-676j5r47qj2rwwj-8000.app.github.dev'

function App() {
  const [saldi, setSaldi] = useState(null)
  const [summary, setSummary] = useState(null)

  useEffect(() => {
    fetch(`${API_URL}/accounts/saldi`)
      .then(res => res.json())
      .then(data => setSaldi(data))

    fetch(`${API_URL}/dashboard/summary`)
      .then(res => res.json())
      .then(data => setSummary(data))
  }, [])

  if (!saldi || !summary) {
    return <p>Caricamento...</p>
  }

  return (
    <div style={{ padding: '32px', fontFamily: 'sans-serif' }}>
      <h1>Patrimonio</h1>
      <CardsRiepilogo saldi={saldi} summary={summary} />
    </div>
  )
}

export default App