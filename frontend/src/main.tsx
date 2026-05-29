import { createRoot } from 'react-dom/client';
import './index.css';
import './components/soundmind-components/IC74HC595';
import './components/soundmind-components/LogicGateElements';
import './components/soundmind-components/TransistorElements';
import './components/soundmind-components/OpAmpElements';
import './components/soundmind-components/PowerElements';
import './components/soundmind-components/DiodeElements';
import './components/soundmind-components/RelayElements';
import './components/soundmind-components/LogicICElements';
import './components/soundmind-components/FlipFlopElements';
import './components/soundmind-components/RaspberryPi3Element';
import './components/soundmind-components/Bmp280Element';
import App from './App.tsx';

createRoot(document.getElementById('root')!).render(<App />);
