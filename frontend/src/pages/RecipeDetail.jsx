import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  Clock, Users, Tag, Pencil, Trash2, Languages, ArrowLeft, Loader2,
  Flame, ChefHat, Zap, Wheat, Droplets,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { getRecipe, deleteRecipe, translateRecipe } from '../api'

const CATEGORY_COLORS = {
  breakfast: 'bg-amber-100 text-amber-800',
  lunch:     'bg-emerald-100 text-emerald-800',
  dinner:    'bg-rose-100 text-rose-800',
  snack:     'bg-violet-100 text-violet-800',
  dessert:   'bg-pink-100 text-pink-800',
}

const LANGUAGES = [
  { code: 'es', label: 'Spanish' },
  { code: 'fr', label: 'French' },
  { code: 'de', label: 'German' },
  { code: 'it', label: 'Italian' },
  { code: 'pt', label: 'Portuguese' },
  { code: 'ja', label: 'Japanese' },
  { code: 'zh', label: 'Chinese' },
  { code: 'hi', label: 'Hindi' },
  { code: 'ar', label: 'Arabic' },
  { code: 'ko', label: 'Korean' },
]

const PLACEHOLDER_GRADIENTS = [
  'from-amber-300 via-orange-300 to-rose-300',
  'from-emerald-300 via-teal-300 to-cyan-300',
  'from-rose-300 via-pink-300 to-fuchsia-300',
]

// Simple client-side nutrition estimation (mirrors the library logic)
const NUTRITION_DB = {
  flour: [364,10,76,1], sugar: [387,0,100,0], butter: [717,1,0,81], egg: [155,13,1,11], eggs: [155,13,1,11],
  milk: [42,3,5,1], rice: [130,3,28,0], pasta: [131,5,25,1], chicken: [239,27,0,14], beef: [250,26,0,15],
  salmon: [208,20,0,13], potato: [77,2,17,0], tomato: [18,1,4,0], onion: [40,1,9,0], garlic: [149,6,33,1],
  'olive oil': [884,0,0,100], cheese: [402,25,1,33], bread: [265,9,49,3], carrot: [41,1,10,0],
  broccoli: [34,3,7,0], spinach: [23,3,4,0], banana: [89,1,23,0], apple: [52,0,14,0], lemon: [29,1,9,0],
  salt: [0,0,0,0], pepper: [251,10,64,3], cream: [340,2,3,36], yogurt: [59,10,4,0], honey: [304,0,82,0],
  mushroom: [22,3,3,0], shrimp: [99,24,0,0], tofu: [76,8,2,5], avocado: [160,2,9,15], corn: [86,3,19,1],
  beans: [347,21,63,1], lentils: [116,9,20,0], 'coconut milk': [230,2,6,24], 'soy sauce': [53,8,5,0],
}
const UNIT_G = { g:1,grams:1,kg:1000,ml:1,l:1000,cup:240,cups:240,tbsp:15,tsp:5,oz:28,lb:454,piece:100,pieces:100,whole:100,slice:30,slices:30,clove:5,cloves:5,pinch:1 }

function estimateNutrition(ingredients) {
  const totals = { calories: 0, protein: 0, carbs: 0, fat: 0 }
  for (const ing of ingredients) {
    const name = (ing.name || '').toLowerCase().trim()
    const qty = Number(ing.quantity) || 0
    const unit = (ing.unit || '').toLowerCase()
    const grams = qty * (UNIT_G[unit] || 100)
    const entry = NUTRITION_DB[name] || [0,0,0,0]
    const f = grams / 100
    totals.calories += entry[0] * f
    totals.protein += entry[1] * f
    totals.carbs += entry[2] * f
    totals.fat += entry[3] * f
  }
  return { calories: Math.round(totals.calories), protein: Math.round(totals.protein), carbs: Math.round(totals.carbs), fat: Math.round(totals.fat) }
}

function categorizeCalories(cal) {
  if (cal < 300) return { label: 'Light', color: 'text-emerald-600 bg-emerald-50' }
  if (cal <= 600) return { label: 'Moderate', color: 'text-amber-600 bg-amber-50' }
  return { label: 'Hearty', color: 'text-rose-600 bg-rose-50' }
}

export default function RecipeDetail() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [recipe, setRecipe] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Ingredient checkboxes
  const [checked, setChecked] = useState({})

  // Translation
  const [targetLang, setTargetLang] = useState('es')
  const [translating, setTranslating] = useState(false)
  const [translation, setTranslation] = useState(null)

  // Delete modal
  const [showDelete, setShowDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    loadRecipe()
  }, [id])

  async function loadRecipe() {
    setLoading(true)
    setError(null)
    try {
      const data = await getRecipe(id)
      setRecipe(data)
    } catch (err) {
      setError('Recipe not found')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleTranslate() {
    setTranslating(true)
    try {
      const result = await translateRecipe(id, targetLang)
      setTranslation(result)
      toast.success('Translation complete')
    } catch (err) {
      toast.error('Translation failed')
      console.error(err)
    } finally {
      setTranslating(false)
    }
  }

  async function handleDelete() {
    setDeleting(true)
    try {
      await deleteRecipe(id)
      toast.success('Recipe deleted')
      navigate('/')
    } catch (err) {
      toast.error('Failed to delete recipe')
      console.error(err)
    } finally {
      setDeleting(false)
    }
  }

  // ---------------------------------------------------------------
  // Loading / Error states
  // ---------------------------------------------------------------
  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10 space-y-6">
        <div className="h-72 skeleton rounded-2xl" />
        <div className="h-8 w-2/3 skeleton" />
        <div className="h-4 w-1/2 skeleton" />
        <div className="h-4 w-full skeleton" />
      </div>
    )
  }

  if (error || !recipe) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <p className="text-stone-400 text-lg mb-4">{error || 'Something went wrong'}</p>
        <Link to="/" className="text-orange-600 font-medium hover:underline">Back to recipes</Link>
      </div>
    )
  }

  // ---------------------------------------------------------------
  // Data extraction
  // ---------------------------------------------------------------
  const category = (recipe.cuisine || recipe.category || '').toLowerCase()
  const badgeClass = CATEGORY_COLORS[category] || 'bg-stone-100 text-stone-700'
  const prepTime = Number(recipe.prepTime || recipe.prep_time || 0)
  const cookTime = Number(recipe.cookTime || recipe.cook_time || 0)
  const totalTime = prepTime + cookTime
  const servings = Number(recipe.servings || 0)
  const imageUrl = recipe.imageUrl || recipe.image_url
  const labels = recipe.detectedLabels || recipe.detected_labels || []
  const ingredients = recipe.ingredients || []
  const instructionText = recipe.instructions || ''
  const steps = Array.isArray(instructionText) ? instructionText : instructionText.split('\n').filter(Boolean)
  const hashIdx = (recipe.title || '').length % PLACEHOLDER_GRADIENTS.length
  const nutrition = estimateNutrition(ingredients)
  const calCategory = categorizeCalories(nutrition.calories)

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Back link */}
      <Link to="/" className="inline-flex items-center gap-1.5 text-sm text-stone-400 hover:text-stone-600 transition mb-6">
        <ArrowLeft className="w-4 h-4" /> Back to recipes
      </Link>

      {/* ---- Hero image ---- */}
      <div className="rounded-2xl overflow-hidden h-64 sm:h-80 mb-8 shadow-md shadow-orange-100/40">
        {imageUrl ? (
          <img src={imageUrl} alt={recipe.title} className="w-full h-full object-cover" />
        ) : (
          <div className={`w-full h-full bg-gradient-to-br ${PLACEHOLDER_GRADIENTS[hashIdx]} flex items-center justify-center`}>
            <span className="text-6xl opacity-50 select-none">🍽</span>
          </div>
        )}
      </div>

      {/* ---- Header ---- */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-8">
        <div>
          {category && (
            <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold capitalize mb-3 ${badgeClass}`}>
              {category}
            </span>
          )}
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-stone-800 leading-tight">{recipe.title}</h1>
          {recipe.description && (
            <p className="mt-3 text-stone-500 leading-relaxed max-w-2xl">{recipe.description}</p>
          )}

          {/* Meta row */}
          <div className="flex flex-wrap items-center gap-5 mt-4 text-sm text-stone-400">
            {prepTime > 0 && (
              <span className="flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-orange-400" /> Prep: {prepTime} min
              </span>
            )}
            {cookTime > 0 && (
              <span className="flex items-center gap-1.5">
                <Flame className="w-4 h-4 text-orange-400" /> Cook: {cookTime} min
              </span>
            )}
            {totalTime > 0 && (
              <span className="flex items-center gap-1.5">
                <Zap className="w-4 h-4 text-orange-400" /> Total: {totalTime} min
              </span>
            )}
            {servings > 0 && (
              <span className="flex items-center gap-1.5">
                <Users className="w-4 h-4 text-orange-400" /> {servings} servings
              </span>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <Link
            to={`/edit/${id}`}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-stone-200 text-sm font-medium text-stone-600 hover:bg-stone-50 transition"
          >
            <Pencil className="w-4 h-4" /> Edit
          </Link>
          <button
            onClick={() => setShowDelete(true)}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-red-200 text-sm font-medium text-red-600 hover:bg-red-50 transition"
          >
            <Trash2 className="w-4 h-4" /> Delete
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* ---- Left column ---- */}
        <div className="lg:col-span-2 space-y-8">
          {/* Ingredients */}
          {ingredients.length > 0 && (
            <section className="bg-white rounded-2xl border border-stone-100 shadow-sm shadow-orange-50/60 p-6">
              <h2 className="font-display text-xl font-semibold text-stone-800 mb-4">Ingredients</h2>
              <ul className="space-y-2.5">
                {ingredients.map((ing, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={checked[i] || false}
                      onChange={() => setChecked(prev => ({ ...prev, [i]: !prev[i] }))}
                      className="ingredient-check"
                    />
                    <span className={`text-sm transition-all duration-200 ${checked[i] ? 'line-through text-stone-300' : 'text-stone-700'}`}>
                      <strong className="font-medium">{ing.quantity} {ing.unit}</strong> {ing.name}
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Instructions */}
          {steps.length > 0 && (
            <section className="bg-white rounded-2xl border border-stone-100 shadow-sm shadow-orange-50/60 p-6">
              <h2 className="font-display text-xl font-semibold text-stone-800 mb-4">Instructions</h2>
              <ol className="space-y-4">
                {steps.map((step, i) => (
                  <li key={i} className="flex gap-3">
                    <span className="w-7 h-7 rounded-full bg-orange-100 text-orange-700 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    <p className="text-sm text-stone-600 leading-relaxed">{step}</p>
                  </li>
                ))}
              </ol>
            </section>
          )}

          {/* Translation */}
          <section className="bg-white rounded-2xl border border-stone-100 shadow-sm shadow-orange-50/60 p-6">
            <h2 className="font-display text-xl font-semibold text-stone-800 mb-4 flex items-center gap-2">
              <Languages className="w-5 h-5 text-orange-500" /> Translate
            </h2>
            <div className="flex flex-wrap items-center gap-3">
              <select
                value={targetLang}
                onChange={e => setTargetLang(e.target.value)}
                className="rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-300 transition"
              >
                {LANGUAGES.map(l => (
                  <option key={l.code} value={l.code}>{l.label}</option>
                ))}
              </select>
              <button
                onClick={handleTranslate}
                disabled={translating}
                className="inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 text-white text-sm font-medium hover:from-orange-600 hover:to-orange-700 disabled:opacity-40 transition shadow-sm shadow-orange-200/60"
              >
                {translating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Languages className="w-4 h-4" />}
                Translate
              </button>
            </div>

            {translation && (
              <div className="mt-5 space-y-3 border-t border-stone-100 pt-4">
                <div>
                  <p className="text-xs font-medium text-stone-400 mb-1">Title</p>
                  <p className="text-sm text-stone-700 font-medium">{translation.title}</p>
                </div>
                {translation.description && (
                  <div>
                    <p className="text-xs font-medium text-stone-400 mb-1">Description</p>
                    <p className="text-sm text-stone-600">{translation.description}</p>
                  </div>
                )}
                {translation.instructions && (
                  <div>
                    <p className="text-xs font-medium text-stone-400 mb-1">Instructions</p>
                    <p className="text-sm text-stone-600 whitespace-pre-line">{translation.instructions}</p>
                  </div>
                )}
              </div>
            )}
          </section>
        </div>

        {/* ---- Right column (sidebar) ---- */}
        <div className="space-y-6">
          {/* Nutrition estimate */}
          {ingredients.length > 0 && (
            <section className="bg-white rounded-2xl border border-stone-100 shadow-sm shadow-orange-50/60 p-6">
              <h2 className="font-display text-lg font-semibold text-stone-800 mb-4">Nutrition Estimate</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-stone-500 flex items-center gap-1.5"><Flame className="w-4 h-4 text-orange-400" /> Calories</span>
                  <span className="text-sm font-semibold text-stone-800">{nutrition.calories} kcal</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-stone-500 flex items-center gap-1.5"><Zap className="w-4 h-4 text-rose-400" /> Protein</span>
                  <span className="text-sm font-semibold text-stone-800">{nutrition.protein}g</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-stone-500 flex items-center gap-1.5"><Wheat className="w-4 h-4 text-amber-400" /> Carbs</span>
                  <span className="text-sm font-semibold text-stone-800">{nutrition.carbs}g</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-stone-500 flex items-center gap-1.5"><Droplets className="w-4 h-4 text-yellow-500" /> Fat</span>
                  <span className="text-sm font-semibold text-stone-800">{nutrition.fat}g</span>
                </div>
                <div className="pt-2 border-t border-stone-100">
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${calCategory.color}`}>
                    {calCategory.label} meal
                  </span>
                </div>
              </div>
            </section>
          )}

          {/* Detected labels */}
          {labels.length > 0 && (
            <section className="bg-white rounded-2xl border border-stone-100 shadow-sm shadow-orange-50/60 p-6">
              <h2 className="font-display text-lg font-semibold text-stone-800 mb-3 flex items-center gap-2">
                <Tag className="w-4 h-4 text-orange-500" /> Detected Labels
              </h2>
              <div className="flex flex-wrap gap-2">
                {labels.map((label, i) => (
                  <span key={i} className="px-2.5 py-1 bg-orange-50 text-orange-700 rounded-full text-xs font-medium">
                    {typeof label === 'string' ? label : label.name}
                    {label.confidence && <span className="ml-1 text-orange-400">{label.confidence}%</span>}
                  </span>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>

      {/* ---- Delete confirmation modal ---- */}
      {showDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-sm w-full p-6 space-y-4">
            <h3 className="font-display text-lg font-semibold text-stone-800">Delete Recipe?</h3>
            <p className="text-sm text-stone-500">
              This will permanently remove <strong>{recipe.title}</strong>. This action cannot be undone.
            </p>
            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="flex-1 py-2.5 rounded-xl bg-red-600 text-white text-sm font-medium hover:bg-red-700 disabled:opacity-50 transition"
              >
                {deleting ? 'Deleting...' : 'Yes, delete'}
              </button>
              <button
                onClick={() => setShowDelete(false)}
                className="flex-1 py-2.5 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
