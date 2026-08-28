import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Analytics } from './pages/Analytics';
import { Blocklist } from './pages/Blocklist';
import { Tunneling } from './pages/Tunneling';
import { Settings } from './pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="blocklist" element={<Blocklist />} />
          <Route path="tunneling" element={<Tunneling />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
