import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, Plus, BookOpen, ChefHat, Flame, UtensilsCrossed } from 'lucide-react'
import RecipeCard from '../components/RecipeCard'
import { getRecipes } from '../api'

const CATEGORIES = ['All', 'Breakfast', 'Lunch', 'Dinner', 'Snack', 'Dessert']

const CATEGORY_ICONS = {
  All: UtensilsCrossed,
  Breakfast: Flame,
  Lunch: BookOpen,
  Dinner: UtensilsCrossed,
  Snack: ChefHat,
  Dessert: ChefHat,
}

const CATEGORY_ACTIVE_COLORS = {
  All:       'bg-orange-600 text-white shadow-orange-200',
  Breakfast: 'bg-amber-600 text-white shadow-amber-200',
  Lunch:     'bg-emerald-600 text-white shadow-emerald-200',
  Dinner:    'bg-rose-600 text-white shadow-rose-200',
  Snack:     'bg-violet-600 text-white shadow-violet-200',
  Dessert:   'bg-pink-600 text-white shadow-pink-200',
}

function SkeletonCard() {
  return (
    <div className="bg-white rounded-2xl overflow-hidden border border-stone-100">
      <div className="h-48 skeleton" />
      <div className="p-4 space-y-3">
        <div className="h-5 w-3/4 skeleton" />
        <div className="h-4 w-full skeleton" />
        <div className="h-3 w-1/2 skeleton" />
      </div>
    </div>
  )
}

export default function Home() {
  const [recipes, setRecipes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeCategory, setActiveCategory] = useState('All')
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetchRecipes()
  }, [])

  async function fetchRecipes() {
    setLoading(true)
    setError(null)
    try {
      const data = await getRecipes()
      setRecipes(data)
    } catch (err) {
      setError('Could not load recipes. Is the API running?')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Filtering
  const filtered = recipes.filter(r => {
    const cat = (r.cuisine || r.category || '').toLowerCase()
    const matchCategory = activeCategory === 'All' || cat === activeCategory.toLowerCase()
    const matchSearch =
      !search.trim() ||
      (r.title || '').toLowerCase().includes(search.toLowerCase()) ||
      (r.description || '').toLowerCase().includes(search.toLowerCase())
    return matchCategory && matchSearch
  })

  // Unique categories count
  const uniqueCategories = new Set(recipes.map(r => (r.cuisine || r.category || '').toLowerCase()).filter(Boolean))

  return (
    <div>
      {/* ---- Hero ---- */}
      <section className="hero-pattern bg-gradient-to-br from-orange-50 via-stone-50 to-amber-50 border-b border-stone-100">
        <div className="max-w-6xl mx-auto px-4 py-14 sm:py-20">
          <div className="max-w-2xl">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-100 text-orange-700 text-xs font-semibold mb-4">
              <ChefHat className="w-3.5 h-3.5" /> CloudChef
            </span>
            <h1 className="font-display text-4xl sm:text-5xl font-bold text-stone-800 leading-tight">
              Your Personal
              <br />
              <span className="text-orange-600">Recipe Collection</span>
            </h1>
            <p className="mt-4 text-stone-500 text-lg leading-relaxed max-w-lg">
              Store your favourite recipes, detect ingredients with AI, and translate them into any language. All in one place.
            </p>
            <Link
              to="/add"
              className="mt-6 inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 text-white font-semibold text-sm
                         hover:from-orange-600 hover:to-orange-700 shadow-lg shadow-orange-200/60 transition-all duration-200"
            >
              <Plus className="w-4 h-4" /> Add a Recipe
            </Link>
          </div>
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* ---- Stats bar ---- */}
        {!loading && recipes.length > 0 && (
          <div className="flex items-center gap-6 mb-6 text-sm text-stone-500">
            <span className="flex items-center gap-1.5">
              <BookOpen className="w-4 h-4 text-orange-500" />
              <strong className="text-stone-700">{recipes.length}</strong> {recipes.length === 1 ? 'recipe' : 'recipes'}
            </span>
            <span className="flex items-center gap-1.5">
              <Flame className="w-4 h-4 text-orange-500" />
              <strong className="text-stone-700">{uniqueCategories.size}</strong> {uniqueCategories.size === 1 ? 'category' : 'categories'}
            </span>
          </div>
        )}

        {/* ---- Search + filter bar ---- */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search recipes..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-stone-200 bg-white text-sm placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-orange-300 focus:border-orange-400 transition"
            />
          </div>
        </div>

        {/* Category pills */}
        <div className="flex flex-wrap gap-2 mb-8">
          {CATEGORIES.map(cat => {
            const active = activeCategory === cat
            return (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`
                  px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
                  ${active
                    ? `${CATEGORY_ACTIVE_COLORS[cat]} shadow-md`
                    : 'bg-white text-stone-500 border border-stone-200 hover:border-stone-300 hover:text-stone-700'
                  }
                `}
              >
                {cat}
              </button>
            )
          })}
        </div>

        {/* ---- Content ---- */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        ) : error ? (
          <div className="text-center py-20">
            <p className="text-stone-400 text-lg mb-2">{error}</p>
            <button onClick={fetchRecipes} className="text-orange-600 font-medium hover:underline">Try again</button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-20 h-20 rounded-full bg-orange-50 flex items-center justify-center mx-auto mb-4">
              <UtensilsCrossed className="w-9 h-9 text-orange-300" />
            </div>
            {recipes.length === 0 ? (
              <>
                <h3 className="font-display text-xl text-stone-700 mb-2">No recipes yet</h3>
                <p className="text-stone-400 mb-6">Time to cook something up!</p>
                <Link to="/add" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-orange-600 text-white text-sm font-medium hover:bg-orange-700 transition">
                  <Plus className="w-4 h-4" /> Add your first recipe
                </Link>
              </>
            ) : (
              <>
                <h3 className="font-display text-xl text-stone-700 mb-2">No matches found</h3>
                <p className="text-stone-400">Try a different search or category.</p>
              </>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map(recipe => (
              <RecipeCard key={recipe.recipeId || recipe.recipe_id} recipe={recipe} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
