import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// ----------------------------------------------------------------
// Recipes
// ----------------------------------------------------------------

export async function getRecipes() {
  const { data } = await api.get('/recipes')
  return data.recipes || []
}

export async function getRecipe(id) {
  const { data } = await api.get(`/recipes/${id}`)
  return data.recipe
}

export async function createRecipe(recipeData) {
  const { data } = await api.post('/recipes', recipeData)
  return data.recipe
}

export async function updateRecipe(id, recipeData) {
  const { data } = await api.put(`/recipes/${id}`, recipeData)
  return data.recipe
}

export async function deleteRecipe(id) {
  const { data } = await api.delete(`/recipes/${id}`)
  return data
}

// ----------------------------------------------------------------
// Translation
// ----------------------------------------------------------------

export async function translateRecipe(id, targetLanguage) {
  const { data } = await api.post(`/recipes/${id}/translate`, { targetLanguage })
  return data.translated
}

// ----------------------------------------------------------------
// Image analysis (Rekognition)
// ----------------------------------------------------------------

export async function analyzeImage(base64Image) {
  const { data } = await api.post('/recipes/analyze-image', { image: base64Image })
  return data
}

export default api
