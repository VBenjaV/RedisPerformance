import { useMemo } from 'react'

export function useFilteredProducts(products, { search, sort }) {
  return useMemo(() => {
    let list = [...products]

    if (search.trim()) {
      const q = search.trim().toLowerCase()
      list = list.filter(
        (p) =>
          p.name.toLowerCase().includes(q) ||
          p.description?.toLowerCase().includes(q) ||
          p.category_name?.toLowerCase().includes(q),
      )
    }

    switch (sort) {
      case 'price-asc':
        list.sort((a, b) => a.price - b.price)
        break
      case 'price-desc':
        list.sort((a, b) => b.price - a.price)
        break
      case 'stock':
        list.sort((a, b) => b.stock - a.stock)
        break
      default:
        list.sort((a, b) => Number(b.is_popular) - Number(a.is_popular) || a.name.localeCompare(b.name))
    }

    return list
  }, [products, search, sort])
}
