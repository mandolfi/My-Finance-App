import { useState, useEffect } from 'react'
import CardsRiepilogo from '../components/CardsRiepilogo'
import GraficoCashflow from '../components/GraficoCashflow'
import ListaConti from '../components/ListaConti'

const API_URL = 'https://automatic-space-fishstick-676j5r47qj2rwwj-8000.app.github.dev'

function ReportMensile() {
  const [saldi, setSaldi] = useState(null)
  const [summary, setSummary] = useState(null)
  const [cashflow, setCashflow] = useState(null)
  const [periodo, setPeriodo] = useState({ anno: 2026, mese: 6 })

  useEffect(() => {
    fetch(`${API_URL}/accounts/saldi`)
      .then(res => res.json())
      .then(data => setSaldi(data))

    fetch(`${API_URL}/dashboard/cashflow`)
      .then(res => res.json())
      .then(data => setCashflow(data))
  }, [])

  useEffect(() => {
    fetch(`${API_URL}/dashboard/summary?anno=${periodo.anno}&mese=${periodo.mese}`)
      .then(res => res.json())
      .then(data => setSummary(data))
  }, [periodo])

  if (!saldi || !summary || !cashflow) {
    return <p>Caricamento...</p>
  }

  const mesiNomi = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']
  const opzioniMese = []
  for (let anno = 2023; anno <= 2026; anno++) {
    for (let mese = 1; mese <= 12; mese++) {
      if (anno === 2026 && mese > 6) break
      opzioniMese.push({ anno, mese })
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ margin: 0 }}>Report Mensile</h1>
        <select
          value={`${periodo.anno}-${periodo.mese}`}
          onChange={(e) => {
            const [anno, mese] = e.target.value.split('-').map(Number)
            setPeriodo({ anno, mese })
          }}
          style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #ddd' }}
        >
          {opzioniMese.map(({ anno, mese }) => (
            <option key={`${anno}-${mese}`} value={`${anno}-${mese}`}>
              {mesiNomi[mese - 1]} {anno}
            </option>
          ))}
        </select>
      </div>
      <CardsRiepilogo saldi={saldi} summary={summary} />
      <GraficoCashflow dati={cashflow} />
      <ListaConti saldi={saldi} />
    </div>
  )
}

export default ReportMensile