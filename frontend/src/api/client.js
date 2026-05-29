const API_BASE = import.meta.env.VITE_API_URL || ''

async function parseError(res) {
  const text = await res.text()
  try {
    const json = JSON.parse(text)
    if (typeof json.detail === 'string') return json.detail
    if (Array.isArray(json.detail)) return json.detail.map((d) => d.msg).join(', ')
    return JSON.stringify(json.detail)
  } catch {
    if (text.includes('Internal Server Error')) {
      return 'No se pudo conectar con la API. ¿Está corriendo? Ejecuta: docker compose up --build'
    }
    return text || res.statusText || 'Error en la API'
  }
}

async function request(path, options = {}) {
  let res
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    })
  } catch {
    throw new Error(
      'Sin conexión al backend. Verifica que la API esté activa (docker compose ps → api Up).',
    )
  }

  if (!res.ok) {
    throw new Error(await parseError(res))
  }

  const cache = res.headers.get('X-Cache')
  const data = await res.json()
  return { data, cache }
}

export const api = {
  getCategories: () => request('/api/categories'),
  getProducts: (params = {}) => {
    const q = new URLSearchParams()
    if (params.categoryId) q.set('category_id', params.categoryId)
    if (params.popular) q.set('popular', 'true')
    const suffix = q.toString() ? `?${q}` : ''
    return request(`/api/products${suffix}`)
  },
  getOffers: () => request('/api/offers'),
  createOrder: (body) =>
    request('/api/orders', { method: 'POST', body: JSON.stringify(body) }),
  getEvents: () => request('/api/system/events'),
}
