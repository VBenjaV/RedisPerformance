export default function Toast({ message, type = 'success' }) {
  if (!message) return null
  return (
    <div className={`toast toast--${type}`} role="status" aria-live="polite">
      {type === 'success' && <span aria-hidden="true">✓</span>}
      {type === 'error' && <span aria-hidden="true">!</span>}
      <span>{message}</span>
    </div>
  )
}
