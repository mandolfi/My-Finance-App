function CardsRiepilogo({ saldi, summary }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '32px' }}>
      <Card etichetta="Patrimonio Netto" valore={saldi.patrimonio_netto_totale} />
      <Card etichetta="Entrate (mese)" valore={summary.totale_entrate} />
      <Card etichetta="Uscite (mese)" valore={summary.totale_uscite} />
      <Card etichetta="Risparmio (mese)" valore={summary.risparmio} />
    </div>
  )
}

function Card({ etichetta, valore }) {
  return (
    <div style={{ background: '#fff', border: '1px solid #ddd', borderRadius: '10px', padding: '18px 20px' }}>
      <div style={{ fontSize: '12px', color: '#666', textTransform: 'uppercase', marginBottom: '8px' }}>
        {etichetta}
      </div>
      <div style={{ fontSize: '24px', fontWeight: 600 }}>
        € {valore.toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </div>
    </div>
  )
}

export default CardsRiepilogo