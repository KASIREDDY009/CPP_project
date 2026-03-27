import { useNavigate } from 'react-router-dom'
import { Clock, Users, Tag } from 'lucide-react'

const CATEGORY_COLORS = {
  breakfast: 'bg-amber-100 text-amber-800',
  lunch:     'bg-emerald-100 text-emerald-800',
  dinner:    'bg-rose-100 text-rose-800',
  snack:     'bg-violet-100 text-violet-800',
  dessert:   'bg-pink-100 text-pink-800',
}

const PLACEHOLDER_GRADIENTS = [
  'from-amber-200 via-orange-200 to-rose-200',
  'from-emerald-200 via-teal-200 to-cyan-200',
  'from-rose-200 via-pink-200 to-fuchsia-200',
  'from-violet-200 via-purple-200 to-indigo-200',
  'from-orange-200 via-amber-200 to-yellow-200',
]

function hashIndex(str, mod) {
  let h = 0
  for (let i = 0; i < str.length; i++) h = (h + str.charCodeAt(i)) % mod
  return h
}

export default function RecipeCard({ recipe }) {
  const navigate = useNavigate()
  const id = recipe.recipeId || recipe.recipe_id
  const category = (recipe.cuisine || recipe.category || '').toLowerCase()
  const badgeClass = CATEGORY_COLORS[category] || 'bg-stone-100 text-stone-700'
  const gradient = PLACEHOLDER_GRADIENTS[hashIndex(recipe.title || '', PLACEHOLDER_GRADIENTS.length)]

  const prepTime = Number(recipe.prepTime || recipe.prep_time || 0)
  const cookTime = Number(recipe.cookTime || recipe.cook_time || 0)
  const totalTime = prepTime + cookTime
  const servings = Number(recipe.servings || 0)

  const description = recipe.description || ''
  const truncated = description.length > 100 ? description.slice(0, 100) + '...' : description

  const labels = recipe.detectedLabels || recipe.detected_labels || []
  const displayLabels = labels.slice(0, 4)

  return (
    <article
      onClick={() => navigate(`/recipe/${id}`)}
      className="group bg-white rounded-2xl overflow-hidden cursor-pointer
                 border border-stone-100
                 shadow-sm shadow-orange-100/40
                 hover:shadow-lg hover:shadow-orange-100/60
                 hover:-translate-y-1
                 transition-all duration-300 ease-out"
    >
      {/* Image or gradient placeholder */}
      <div className="relative h-48 overflow-hidden">
        {recipe.imageUrl || recipe.image_url ? (
          <img
            src={recipe.imageUrl || recipe.image_url}
            alt={recipe.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        ) : (
          <div className={`w-full h-full bg-gradient-to-br ${gradient} flex items-center justify-center`}>
            <span className="text-4xl opacity-60 select-none">🍽</span>
          </div>
        )}

        {/* Category badge overlay */}
        {category && (
          <span className={`absolute top-3 left-3 px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${badgeClass}`}>
            {category}
          </span>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-2.5">
        <h3 className="font-display text-lg font-semibold text-stone-800 leading-tight group-hover:text-orange-700 transition-colors">
          {recipe.title}
        </h3>

        {truncated && (
          <p className="text-sm text-stone-500 leading-relaxed">{truncated}</p>
        )}

        {/* Time & servings */}
        <div className="flex items-center gap-4 text-xs text-stone-400 pt-1">
          {totalTime > 0 && (
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {totalTime} min
            </span>
          )}
          {servings > 0 && (
            <span className="flex items-center gap-1">
              <Users className="w-3.5 h-3.5" />
              {servings} servings
            </span>
          )}
        </div>

        {/* Detected labels */}
        {displayLabels.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {displayLabels.map((label, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-stone-50 text-stone-500 rounded text-[11px] font-medium"
              >
                <Tag className="w-2.5 h-2.5" />
                {typeof label === 'string' ? label : label.name}
              </span>
            ))}
          </div>
        )}
      </div>
    </article>
  )
}
