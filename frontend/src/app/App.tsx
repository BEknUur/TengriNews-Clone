import { BrowserRouter } from 'react-router-dom'
import { QueryProvider } from './providers/query-provider'
import { AppRouter } from './router'
import { Header } from '@/widgets/header/ui/Header'

export function App() {
  return (
    <QueryProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-background text-foreground">
          <Header />
          <AppRouter />
        </div>
      </BrowserRouter>
    </QueryProvider>
  )
}
