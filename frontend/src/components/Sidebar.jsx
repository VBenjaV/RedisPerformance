import ActivityFeed from './ActivityFeed'
import CartPanel from './CartPanel'

export default function Sidebar(props) {
  return (
    <aside className="sidebar" aria-label="Carrito y actividad del sistema">
      <CartPanel {...props} idPrefix="sidebar-" />
      <ActivityFeed events={props.events} />
    </aside>
  )
}
