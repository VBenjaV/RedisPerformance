export const priceFmt = new Intl.NumberFormat('es-CL', {
  style: 'currency',
  currency: 'USD',
})

export function formatTime(iso) {
  if (!iso) return ''
  return new Intl.DateTimeFormat('es-CL', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(new Date(iso))
}

export const SOURCE_LABELS = {
  'api-publisher': { label: 'API', color: 'blue' },
  'inventory-subscriber': { label: 'Inventario', color: 'amber' },
  'email-subscriber': { label: 'Email', color: 'violet' },
  'analytics-subscriber': { label: 'Analytics', color: 'green' },
}
