import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { App } from './App'
import { ThemeProvider } from './hooks/useTheme'
import { fetchDaily } from './mock/api'

const data = fetchDaily();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <App data={data} />
    </ThemeProvider>
  </StrictMode>,
)
