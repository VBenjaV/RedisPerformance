import { priceFmt } from '../utils/format'

export default function OffersStrip({ offers, cacheStatus, onSelectProduct }) {
  if (!offers.length) return null

  return (
    <section className="offers-section" aria-label="Ofertas activas">
      <div className="section-title">
        <div>
          <h2 className="section-heading">Ofertas del día</h2>
          <p className="section-sub">Endpoint cacheado: GET /api/offers</p>
        </div>
        {cacheStatus && (
          <span className={`cache-tag ${cacheStatus === 'HIT' ? 'hit' : 'miss'}`}>
            Redis {cacheStatus}
          </span>
        )}
      </div>
      <div className="offers-strip">
        {offers.map((offer) => (
          <article key={offer.id} className="offer-card">
            <div className="offer-card__top">
              <span className="offer-discount">-{offer.discount_percent}%</span>
              <span className="offer-flash">Flash</span>
            </div>
            <h3>{offer.title}</h3>
            <p className="offer-product">{offer.product_name}</p>
            <p className="offer-price">
              {priceFmt.format(offer.product_price * (1 - offer.discount_percent / 100))}
              <span className="offer-price__old">{priceFmt.format(offer.product_price)}</span>
            </p>
            {onSelectProduct && (
              <button
                type="button"
                className="offer-cta"
                onClick={() => onSelectProduct(offer.product_id)}
              >
                Ver producto
              </button>
            )}
          </article>
        ))}
      </div>
    </section>
  )
}
