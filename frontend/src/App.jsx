import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api } from './api/client'
import CacheStatusBar from './components/CacheStatusBar'
import CategoryPills from './components/CategoryPills'
import Footer from './components/Footer'
import Header from './components/Header'
import Hero from './components/Hero'
import MobileCartDrawer from './components/MobileCartDrawer'
import OffersStrip from './components/OffersStrip'
import ProductDetailModal from './components/ProductDetailModal'
import ProductGrid from './components/ProductGrid'
import SearchSortBar from './components/SearchSortBar'
import Sidebar from './components/Sidebar'
import SkeletonGrid from './components/SkeletonGrid'
import Toast from './components/Toast'
import { useFilteredProducts } from './hooks/useFilteredProducts'

export default function App() {
  const catalogRef = useRef(null)
  const [categories, setCategories] = useState([])
  const [products, setProducts] = useState([])
  const [offers, setOffers] = useState([])
  const [activeCategory, setActiveCategory] = useState(null)
  const [cacheTags, setCacheTags] = useState({})
  const [cart, setCart] = useState([])
  const [email, setEmail] = useState('')
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [productsLoading, setProductsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [checkingOut, setCheckingOut] = useState(false)
  const [toast, setToast] = useState(null)
  const [toastType, setToastType] = useState('success')
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState('featured')
  const [cartOpen, setCartOpen] = useState(false)
  const [detailProduct, setDetailProduct] = useState(null)

  const showToast = (message, type = 'success') => {
    setToast(message)
    setToastType(type)
    setTimeout(() => setToast(null), 3500)
  }

  const loadCatalog = useCallback(async (categoryFilter) => {
    setProductsLoading(true)
    setError(null)
    try {
      const [catRes, offRes] = await Promise.all([
        api.getCategories(),
        api.getOffers(),
      ])
      setCategories(catRes.data)
      setOffers(offRes.data)
      setCacheTags((t) => ({
        ...t,
        categories: catRes.cache,
        offers: offRes.cache,
      }))

      const params =
        categoryFilter === 'popular'
          ? { popular: true }
          : categoryFilter
            ? { categoryId: categoryFilter }
            : {}
      const prodRes = await api.getProducts(params)
      setProducts(prodRes.data)
      setCacheTags((t) => ({ ...t, products: prodRes.cache }))
    } catch (e) {
      setError(e.message)
    } finally {
      setProductsLoading(false)
      setLoading(false)
    }
  }, [])

  const refreshEvents = useCallback(async () => {
    try {
      const { data } = await api.getEvents()
      setEvents(data)
    } catch {
      /* polling silencioso */
    }
  }, [])

  useEffect(() => {
    loadCatalog(activeCategory)
  }, [activeCategory, loadCatalog])

  useEffect(() => {
    refreshEvents()
    const id = setInterval(refreshEvents, 2500)
    return () => clearInterval(id)
  }, [refreshEvents])

  const filteredProducts = useFilteredProducts(products, { search, sort })

  const cartCount = useMemo(() => cart.reduce((n, i) => n + i.qty, 0), [cart])
  const total = useMemo(
    () => cart.reduce((sum, i) => sum + i.price * i.qty, 0),
    [cart],
  )

  const addToCart = (product) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.id === product.id)
      if (existing) {
        return prev.map((i) =>
          i.id === product.id
            ? { ...i, qty: Math.min(i.qty + 1, product.stock) }
            : i,
        )
      }
      return [
        ...prev,
        {
          id: product.id,
          name: product.name,
          price: product.price,
          qty: 1,
          stock: product.stock,
          image_url: product.image_url,
        },
      ]
    })
    showToast(`${product.name} agregado al carrito`)
  }

  const updateQty = (id, qty) => {
    if (qty < 1) {
      setCart((prev) => prev.filter((i) => i.id !== id))
      return
    }
    setCart((prev) =>
      prev.map((i) =>
        i.id === id ? { ...i, qty: Math.min(qty, i.stock) } : i,
      ),
    )
  }

  const removeFromCart = (id) => {
    setCart((prev) => prev.filter((i) => i.id !== id))
  }

  const handleCheckout = async () => {
    setCheckingOut(true)
    setError(null)
    try {
      const order = await api.createOrder({
        customer_email: email,
        items: cart.map((i) => ({ product_id: i.id, quantity: i.qty })),
      })
      setCart([])
      setCartOpen(false)
      showToast(`Orden #${order.data.order_id} creada — revisa Pub/Sub`)
      await loadCatalog(activeCategory)
      await refreshEvents()
    } catch (e) {
      setError(e.message)
      showToast(e.message, 'error')
    } finally {
      setCheckingOut(false)
    }
  }

  const scrollToCatalog = () => {
    catalogRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const openProductById = (productId) => {
    const found = products.find((p) => p.id === productId)
    if (found) setDetailProduct(found)
    else scrollToCatalog()
  }

  const cartProps = {
    cart,
    total,
    email,
    onEmailChange: setEmail,
    onCheckout: handleCheckout,
    checkingOut,
    onUpdateQty: updateQty,
    onRemove: removeFromCart,
  }

  if (loading) {
    return (
      <div className="app-loading">
        <div className="app-loading__spinner" aria-hidden="true" />
        <p>Cargando ShopNow…</p>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <Header
        cartCount={cartCount}
        onOpenCart={() => setCartOpen(true)}
        search={search}
        onSearchChange={setSearch}
      />

      <Hero
        stats={{
          products: products.length,
          categories: categories.length,
          offers: offers.length,
        }}
        onShopClick={scrollToCatalog}
      />

      <CacheStatusBar cacheTags={cacheTags} />

      {error && (
        <div className="error-banner" role="alert">
          {error}
          <button type="button" onClick={() => setError(null)} aria-label="Cerrar">
            ×
          </button>
        </div>
      )}

      <OffersStrip
        offers={offers}
        cacheStatus={cacheTags.offers}
        onSelectProduct={openProductById}
      />

      <div className="main-grid">
        <main ref={catalogRef}>
          <CategoryPills
            categories={categories}
            activeId={activeCategory}
            onSelect={setActiveCategory}
            loading={productsLoading}
          />

          <SearchSortBar
            search={search}
            onSearchChange={setSearch}
            sort={sort}
            onSortChange={setSort}
            resultCount={filteredProducts.length}
            loading={productsLoading}
          />

          <div className="catalog-section">
            <div className="section-title">
              <p className="section-sub">
                GET /api/products
                {cacheTags.products && (
                  <span className={`cache-tag ${cacheTags.products === 'HIT' ? 'hit' : 'miss'}`}>
                    {cacheTags.products}
                  </span>
                )}
              </p>
            </div>

            {productsLoading ? (
              <SkeletonGrid />
            ) : (
              <ProductGrid
                products={filteredProducts}
                onAdd={addToCart}
                onQuickView={setDetailProduct}
              />
            )}
          </div>
        </main>

        <div className="sidebar-desktop">
          <Sidebar {...cartProps} events={events} />
        </div>
      </div>

      <Footer />

      <MobileCartDrawer
        open={cartOpen}
        onClose={() => setCartOpen(false)}
        cartProps={cartProps}
        events={events}
      />

      {detailProduct && (
        <ProductDetailModal
          product={detailProduct}
          onClose={() => setDetailProduct(null)}
          onAdd={addToCart}
        />
      )}

      <Toast message={toast} type={toastType} />
    </div>
  )
}
