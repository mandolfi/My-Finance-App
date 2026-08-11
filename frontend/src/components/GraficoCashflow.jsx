
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'

function GraficoCashflow({ dati }) {
  return (
    <div style={{ background: '#fff', border: '1px solid #ddd', borderRadius: '10px', padding: '22px', marginBottom: '32px' }}>
      <h3 style={{ marginTop: 0 }}>Cashflow</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={dati}>
          <XAxis dataKey="periodo" />
          <YAxis />
          <Tooltip formatter={(value) => `€ ${value.toLocaleString('it-IT')}`} />
          <Legend />
          <Bar dataKey="entrate" fill="#3F6B4F" name="Entrate" />
          <Bar dataKey="uscite" fill="#9C4A3A" name="Uscite" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default GraficoCashflow
