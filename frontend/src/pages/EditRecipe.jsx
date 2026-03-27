import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChefHat, ArrowLeft } from 'lucide-react'
import RecipeForm from '../components/RecipeForm'
import { getRecipe } from '../api'

export default function EditRecipe() {
  const { id } = useParams()
  const [recipe, setRecipe] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const data = await getRecipe(id)
        setRecipe(data)
      } catch (err) {
        setError('Could not load recipe')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-10 space-y-6">
        <div className="h-8 w-1/3 skeleton" />
        <div className="h-4 w-1/2 skeleton" />
        <div className="h-64 skeleton rounded-2xl" />
      </div>
    )
  }

  if (error || !recipe) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center">
        <p className="text-stone-400 text-lg mb-4">{error || 'Recipe not found'}</p>
        <Link to="/" className="text-orange-600 font-medium hover:underline">Back to recipes</Link>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <Link to={`/recipe/${id}`} className="inline-flex items-center gap-1.5 text-sm text-stone-400 hover:text-stone-600 transition mb-6">
        <ArrowLeft className="w-4 h-4" /> Back to recipe
      </Link>

      <div className="mb-8">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-100 text-orange-700 text-xs font-semibold mb-3">
          <ChefHat className="w-3.5 h-3.5" /> Edit
        </span>
        <h1 className="font-display text-3xl font-bold text-stone-800">Edit Recipe</h1>
        <p className="mt-2 text-stone-500">Update the details for <strong>{recipe.title}</strong>.</p>
      </div>

      <RecipeForm existingRecipe={recipe} />
    </div>
  )
}
