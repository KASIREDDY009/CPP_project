import { Routes, Route, useLocation } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import AddRecipe from './pages/AddRecipe'
import RecipeDetail from './pages/RecipeDetail'
import EditRecipe from './pages/EditRecipe'

export default function App() {
  const location = useLocation()

  return (
    <div className="min-h-screen flex flex-col bg-stone-50">
      <Navbar />

      <main className="flex-1">
        <div key={location.pathname} className="animate-fade-in">
          <Routes location={location}>
            <Route path="/" element={<Home />} />
            <Route path="/add" element={<AddRecipe />} />
            <Route path="/recipe/:id" element={<RecipeDetail />} />
            <Route path="/edit/:id" element={<EditRecipe />} />
          </Routes>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-stone-200 bg-white mt-16">
        <div className="max-w-6xl mx-auto px-4 py-8 text-center">
          <p className="font-display text-lg text-stone-700 tracking-wide">CloudChef</p>
          <p className="text-sm text-stone-400 mt-1">&copy; 2026 &middot; Your Personal Recipe Collection</p>
        </div>
      </footer>

      <Toaster
        position="bottom-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#292524',
            color: '#FAFAF9',
            borderRadius: '10px',
            fontSize: '14px',
          },
          success: { iconTheme: { primary: '#059669', secondary: '#fff' } },
          error: { iconTheme: { primary: '#DC2626', secondary: '#fff' } },
        }}
      />
    </div>
  )
}
