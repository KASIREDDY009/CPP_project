import RecipeForm from '../components/RecipeForm'
import { ChefHat } from 'lucide-react'

export default function AddRecipe() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="mb-8">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-100 text-orange-700 text-xs font-semibold mb-3">
          <ChefHat className="w-3.5 h-3.5" /> New Recipe
        </span>
        <h1 className="font-display text-3xl font-bold text-stone-800">Add a Recipe</h1>
        <p className="mt-2 text-stone-500">Share your culinary creation with the world.</p>
      </div>

      <RecipeForm />
    </div>
  )
}
