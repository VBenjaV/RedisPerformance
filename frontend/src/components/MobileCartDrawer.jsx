import { useEffect } from 'react'
import ActivityFeed from './ActivityFeed'
import CartPanel from './CartPanel'

export default function MobileCartDrawer({ open, onClose, cartProps, events }) {
  useEffect(() => {
    if (!open) return
    const onKey = (e) => e.key === 'Escape' && onClose()
    document.body.style.overflow = 'hidden'
    document.addEventListener('keydown', onKey)
    return () => {
      document.body.style.overflow = ''
      document.removeEventListener('keydown', onKey)
    }
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="drawer-overlay" onClick={onClose} role="presentation">
      <aside
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Carrito y actividad"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="drawer-header">
          <h2>Tu compra</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Cerrar">
            ×
          </button>
        </div>
        <div className="drawer-body">
          <CartPanel {...cartProps} idPrefix="drawer-" />
          <ActivityFeed events={events} />
        </div>
      </aside>
    </div>
  )
}
