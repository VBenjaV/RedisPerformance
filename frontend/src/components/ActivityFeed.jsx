import { formatTime, SOURCE_LABELS } from '../utils/format'

export default function ActivityFeed({ events }) {
  return (
    <div className="panel panel--activity">
      <div className="panel-header">
        <h2>Actividad Pub/Sub</h2>
        <span className="live-dot" title="Actualización en vivo" aria-hidden="true" />
      </div>
      <ul className="activity-list" aria-live="polite">
        {events.length === 0 && (
          <li className="activity-empty">
            Esperando eventos… Crea una orden para activar los subscribers.
          </li>
        )}
        {events.map((ev, i) => {
          const meta = SOURCE_LABELS[ev.source] || { label: ev.source, color: 'gray' }
          return (
            <li key={`${ev.at}-${i}`} className={`activity-item activity-item--${meta.color}`}>
              <div className="activity-item__head">
                <span className={`activity-source activity-source--${meta.color}`}>
                  {meta.label}
                </span>
                <time dateTime={ev.at}>{formatTime(ev.at)}</time>
              </div>
              <p>{ev.message}</p>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
