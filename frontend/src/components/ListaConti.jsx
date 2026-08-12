function ListaConti({ saldi }) {
  // Raggruppa i conti per categoria
  const perCategoria = {}
  for (const conto of saldi.conti) {
    if (!perCategoria[conto.categoria]) {
      perCategoria[conto.categoria] = []
    }
    perCategoria[conto.categoria].push(conto)
  }

  return (
    <div style={{ background: '#fff', border: '1px solid #ddd', borderRadius: '10px', padding: '22px' }}>
      <h3 style={{ marginTop: 0 }}>Conti</h3>
      {Object.entries(perCategoria).map(([categoria, conti]) => (
        <div key={categoria} style={{ marginBottom: '20px' }}>
          <div style={{
            fontSize: '12px',
            textTransform: 'uppercase',
            color: '#666',
            marginBottom: '8px',
            fontWeight: 600
          }}>
            {categoria}
          </div>
          {conti.map(conto => (
            <div
              key={conto.id}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                padding: '8px 0',
                borderBottom: '1px solid #f0f0f0'
              }}
            >
              <span>{conto.nome}</span>
              <span style={{
                fontFamily: 'monospace',
                color: conto.saldo < 0 ? '#9C4A3A' : '#1B3A36'
              }}>
                € {conto.saldo.toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}

export default ListaConti