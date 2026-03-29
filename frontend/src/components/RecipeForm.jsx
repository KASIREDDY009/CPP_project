import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Plus, Trash2, Upload, Sparkles, Loader2, GripVertical, ImageIcon,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { createRecipe, updateRecipe, analyzeImage } from '../api'

const CATEGORIES = ['breakfast', 'lunch', 'dinner', 'snack', 'dessert']
const UNITS = ['g', 'kg', 'ml', 'l', 'cup', 'cups', 'tbsp', 'tsp', 'oz', 'lb', 'piece', 'pieces', 'whole', 'slice', 'slices', 'clove', 'cloves', 'pinch']

const emptyIngredient = () => ({ name: '', quantity: '', unit: 'g' })

export default function RecipeForm({ existingRecipe = null }) {
  const navigate = useNavigate()
  const fileRef = useRef(null)
  const isEdit = Boolean(existingRecipe)

  // Form state
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('dinner')
  const [prepTime, setPrepTime] = useState('')
  const [cookTime, setCookTime] = useState('')
  const [servings, setServings] = useState('')
  const [ingredients, setIngredients] = useState([emptyIngredient()])
  const [instructions, setInstructions] = useState([''])
  const [imagePreview, setImagePreview] = useState(null)
  const [imageBase64, setImageBase64] = useState(null)
  const [detectedLabels, setDetectedLabels] = useState([])
  const [analyzing, setAnalyzing] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  // Populate form when editing
  useEffect(() => {
    if (!existingRecipe) return
    setTitle(existingRecipe.title || '')
    setDescription(existingRecipe.description || '')
    setCategory((existingRecipe.cuisine || existingRecipe.category || 'dinner').toLowerCase())
    setPrepTime(existingRecipe.prepTime || existingRecipe.prep_time || '')
    setCookTime(existingRecipe.cookTime || existingRecipe.cook_time || '')
    setServings(existingRecipe.servings || '')
    setImagePreview(existingRecipe.imageUrl || existingRecipe.image_url || null)
    setDetectedLabels(existingRecipe.detectedLabels || existingRecipe.detected_labels || [])

    const ings = existingRecipe.ingredients || []
    if (ings.length > 0) {
      setIngredients(ings.map(i => ({
        name: i.name || '',
        quantity: i.quantity?.toString() || '',
        unit: i.unit || 'g',
      })))
    }

    const instrs = existingRecipe.instructions || []
    if (Array.isArray(instrs) && instrs.length > 0) {
      setInstructions(instrs)
    } else if (typeof instrs === 'string' && instrs.trim()) {
      setInstructions(instrs.split('\n').filter(Boolean))
    }
  }, [existingRecipe])

  // ---------------------------------------------------------------
  // Ingredient helpers
  // ---------------------------------------------------------------
  const updateIngredient = (index, field, value) => {
    setIngredients(prev => {
      const updated = [...prev]
      updated[index] = { ...updated[index], [field]: value }
      return updated
    })
  }
  const addIngredient = () => setIngredients(prev => [...prev, emptyIngredient()])
  const removeIngredient = (index) => {
    setIngredients(prev => {
      if (prev.length <= 1) return prev
      return prev.filter((_, i) => i !== index)
    })
  }

  // ---------------------------------------------------------------
  // Instruction helpers
  // ---------------------------------------------------------------
  const updateInstruction = (index, value) => {
    const updated = [...instructions]
    updated[index] = value
    setInstructions(updated)
  }
  const addInstruction = () => setInstructions([...instructions, ''])
  const removeInstruction = (index) => {
    if (instructions.length <= 1) return
    setInstructions(instructions.filter((_, i) => i !== index))
  }

  // ---------------------------------------------------------------
  // Image handling
  // ---------------------------------------------------------------
  const handleImageSelect = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image must be under 5 MB')
      return
    }
    const reader = new FileReader()
    reader.onload = () => {
      setImagePreview(reader.result)
      const base64 = reader.result.split(',')[1]
      setImageBase64(base64)
    }
    reader.readAsDataURL(file)
  }

  const handleAnalyze = async () => {
    if (!imageBase64) {
      toast.error('Upload an image first')
      return
    }
    setAnalyzing(true)
    try {
      const result = await analyzeImage(imageBase64)
      setDetectedLabels(result.labels || [])
      toast.success(`Detected ${(result.labels || []).length} labels`)
    } catch (err) {
      toast.error('Image analysis failed')
      console.error(err)
    } finally {
      setAnalyzing(false)
    }
  }

  // ---------------------------------------------------------------
  // Submit
  // ---------------------------------------------------------------
  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!title.trim()) {
      toast.error('Give your recipe a name')
      return
    }

    const filteredIngredients = ingredients
      .filter(i => i.name.trim())
      .map(i => ({ name: i.name.trim(), quantity: Number(i.quantity) || 0, unit: i.unit }))

    const filteredInstructions = instructions.filter(s => s.trim())

    const payload = {
      title: title.trim(),
      description: description.trim(),
      cuisine: category,
      prepTime: prepTime.toString(),
      cookTime: cookTime.toString(),
      servings: Number(servings) || 0,
      ingredients: filteredIngredients,
      instructions: filteredInstructions.join('\n'),
    }

    if (imageBase64) payload.image = imageBase64

    setSubmitting(true)
    try {
      if (isEdit) {
        const id = existingRecipe.recipeId || existingRecipe.recipe_id
        await updateRecipe(id, payload)
        toast.success('Recipe updated')
        navigate(`/recipe/${id}`)
      } else {
        const created = await createRecipe(payload)
        toast.success('Recipe created')
        navigate(`/recipe/${created.recipeId || created.recipe_id}`)
      }
    } catch (err) {
      toast.error(isEdit ? 'Failed to update recipe' : 'Failed to create recipe')
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  // ---------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------
  const inputBase = 'w-full rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm text-stone-800 placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-orange-300 focus:border-orange-400 transition'
  const labelBase = 'block text-sm font-medium text-stone-700 mb-1.5'

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* ---- Basic info ---- */}
      <section className="bg-white rounded-2xl border border-stone-100 shadow-sm shadow-orange-50/60 p-6 space-y-5">
        <h2 className="font-display text-xl font-semibold text-stone-800">Basic Information</h2>

        <div>
          <label className={labelBase}>Recipe Title *</label>
          <input type="text" value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g. Grandma's Apple Pie" className={inputBase} required />
        </div>

        <div>
          <label className={labelBase}>Description</label>
          <textarea value={description} onChange={e => setDescription(e.target.value)} rows={3} placeholder="A short description of your dish..." className={`${inputBase} resize-none`} />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <label className={labelBase}>Category</label>
            <select value={category} onChange={e => setCategory(e.target.value)} className={inputBase}>
              {CATEGORIES.map(c => (
                <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelBase}>Prep (min)</label>
            <input type="number" min="0" value={prepTime} onChange={e => setPrepTime(e.target.value)} placeholder="15" className={inputBase} />
          </div>
          <div>
            <label className={labelBase}>Cook (min)</label>
            <input type="number" min="0" value={cookTime} onChange={e => setCookTime(e.target.value)} placeholder="30" className={inputBase} />
          </div>
          <div>
            <label className={labelBase}>Servings</label>
            <input type="number" min="0" value={servings} onChange={e => setServings(e.target.value)} placeholder="4" className={inputBase} />
          </div>
        </div>
      </section>

      {/* ---- Image upload ---- */}
      <section className="bg-white rounded-2xl border border-stone-100 shadow-sm shadow-orange-50/60 p-6 space-y-4">
        <h2 className="font-display text-xl font-semibold text-stone-800">Recipe Photo</h2>

        <div className="flex flex-col sm:flex-row gap-4 items-start">
          {/* Preview */}
          <div
            onClick={() => fileRef.current?.click()}
            className="w-full sm:w-48 h-40 rounded-xl border-2 border-dashed border-stone-200 hover:border-orange-300 flex items-center justify-center cursor-pointer overflow-hidden transition-colors"
          >
            {imagePreview ? (
              <img src={imagePreview} alt="Preview" className="w-full h-full object-cover" />
            ) : (
              <div className="text-center text-stone-400">
                <ImageIcon className="w-8 h-8 mx-auto mb-1" />
                <span className="text-xs">Click to upload</span>
              </div>
            )}
          </div>

          <input ref={fileRef} type="file" accept="image/*" onChange={handleImageSelect} className="hidden" />

          <div className="flex flex-col gap-2">
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-stone-200 text-sm font-medium text-stone-600 hover:bg-stone-50 transition"
            >
              <Upload className="w-4 h-4" />
              {imagePreview ? 'Change image' : 'Upload image'}
            </button>

            <button
              type="button"
              onClick={handleAnalyze}
              disabled={!imageBase64 || analyzing}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-orange-500 to-orange-600 text-white text-sm font-medium hover:from-orange-600 hover:to-orange-700 disabled:opacity-40 disabled:cursor-not-allowed transition shadow-sm shadow-orange-200/60"
            >
              {analyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              Analyse Image
            </button>
          </div>
        </div>

        {/* Detected labels */}
        {detectedLabels.length > 0 && (
          <div className="pt-2">
            <p className="text-xs font-medium text-stone-500 mb-2">Detected labels:</p>
            <div className="flex flex-wrap gap-2">
              {detectedLabels.map((label, i) => (
                <span key={i} className="px-2.5 py-1 bg-orange-50 text-orange-700 rounded-full text-xs font-medium">
                  {typeof label === 'string' ? label : label.name}
                  {label.confidence && <span className="ml-1 text-orange-400">{label.confidence}%</span>}
                </span>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* ---- Ingredients ---- */}
      <section className="bg-white rounded-2xl border border-stone-100 shadow-sm shadow-orange-50/60 p-6 space-y-4">
        <h2 className="font-display text-xl font-semibold text-stone-800">Ingredients</h2>

        <div className="space-y-3">
          {ingredients.map((ing, i) => (
            <div key={i} className="flex items-center gap-2">
              <GripVertical className="w-4 h-4 text-stone-300 flex-shrink-0 hidden sm:block" />
              <input
                type="text"
                value={ing.name}
                onChange={e => updateIngredient(i, 'name', e.target.value)}
                placeholder="Ingredient"
                className={`flex-1 ${inputBase}`}
              />
              <input
                type="number"
                min="0"
                step="any"
                value={ing.quantity}
                onChange={e => updateIngredient(i, 'quantity', e.target.value)}
                placeholder="Qty"
                className={`w-20 ${inputBase}`}
              />
              <select
                value={ing.unit}
                onChange={e => updateIngredient(i, 'unit', e.target.value)}
                className={`w-24 ${inputBase}`}
              >
                {UNITS.map(u => <option key={u} value={u}>{u}</option>)}
              </select>
              <button
                type="button"
                onClick={() => removeIngredient(i)}
                className="p-2 rounded-lg text-stone-400 hover:text-red-500 hover:bg-red-50 transition"
                aria-label="Remove ingredient"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>

        <button type="button" onClick={addIngredient} className="inline-flex items-center gap-1.5 text-sm font-medium text-orange-600 hover:text-orange-700 transition">
          <Plus className="w-4 h-4" /> Add ingredient
        </button>
      </section>

      {/* ---- Instructions ---- */}
      <section className="bg-white rounded-2xl border border-stone-100 shadow-sm shadow-orange-50/60 p-6 space-y-4">
        <h2 className="font-display text-xl font-semibold text-stone-800">Instructions</h2>

        <div className="space-y-3">
          {instructions.map((step, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className="w-7 h-7 rounded-full bg-orange-100 text-orange-700 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-2">
                {i + 1}
              </span>
              <textarea
                value={step}
                onChange={e => updateInstruction(i, e.target.value)}
                rows={2}
                placeholder={`Step ${i + 1}...`}
                className={`flex-1 ${inputBase} resize-none`}
              />
              <button
                type="button"
                onClick={() => removeInstruction(i)}
                className="p-2 rounded-lg text-stone-400 hover:text-red-500 hover:bg-red-50 transition mt-1"
                aria-label="Remove step"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>

        <button type="button" onClick={addInstruction} className="inline-flex items-center gap-1.5 text-sm font-medium text-orange-600 hover:text-orange-700 transition">
          <Plus className="w-4 h-4" /> Add step
        </button>
      </section>

      {/* ---- Submit ---- */}
      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={submitting}
          className="px-8 py-3 rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 text-white font-semibold text-sm
                     hover:from-orange-600 hover:to-orange-700
                     disabled:opacity-50 disabled:cursor-not-allowed
                     shadow-md shadow-orange-200/60
                     transition-all duration-200"
        >
          {submitting ? (
            <span className="inline-flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /> Saving...</span>
          ) : (
            isEdit ? 'Update Recipe' : 'Create Recipe'
          )}
        </button>
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="px-6 py-3 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium hover:bg-stone-50 transition"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
