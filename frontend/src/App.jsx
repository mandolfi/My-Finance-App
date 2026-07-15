import { useState, useEffect } from 'react'

function App() {
  const [saldi, setSaldi] = useState(null)

  useEffect(() => {
    fetch('https://automatic-space-fishstick-676j5r47qj2rwwj-8000.app.github.dev/accounts/saldi')
      .then(res => res.json())
      .then(data => setSaldi(data))
  }, [])

  if (!saldi) {
    return <p>Caricamento...</p>
  }

  return (
    <div>
      <h1>Patrimonio Netto Totale: € {saldi.patrimonio_netto_totale.toLocaleString()}</h1>
      <p>Patrimonio Liquido: € {saldi.patrimonio_liquido.toLocaleString()}</p>
      <p>Valore Immobili: € {saldi.valore_immobili.toLocaleString()}</p>
      <p>Debiti: € {saldi.totale_debiti.toLocaleString()}</p>
    </div>
  )
}

export default App