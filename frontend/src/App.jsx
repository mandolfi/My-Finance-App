import { BrowserRouter, Routes, Route } from 'react-router-dom'
import NavBar from './components/NavBar'
import Cockpit from './pages/Cockpit'
import ReportMensile from './pages/ReportMensile'
import ReportAnnuale from './pages/ReportAnnuale'
import ReportStorico from './pages/ReportStorico'

function App() {
  return (
    <BrowserRouter>
      <div style={{ padding: '32px', fontFamily: 'sans-serif' }}>
        <NavBar />
        <Routes>
          <Route path="/" element={<Cockpit />} />
          <Route path="/mensile" element={<ReportMensile />} />
          <Route path="/annuale" element={<ReportAnnuale />} />
          <Route path="/storico" element={<ReportStorico />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App