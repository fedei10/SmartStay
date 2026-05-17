'use client';

import { Hotel } from '@/lib/types';
import { Star, MapPin, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface HotelCardProps {
  hotel: Hotel;
  index?: number;
  onSelect?: () => void;
  isDisabled?: boolean;
}

const PLACEHOLDER =
  'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22220%22%3E%3Crect fill=%22%231a2942%22 width=%22400%22 height=%22220%22/%3E%3Cpath d=%22M0 160 C90 110 140 175 215 130 C290 90 325 130 400 90 L400 220 L0 220 Z%22 fill=%22%231aa39a%22 opacity=%220.7%22/%3E%3Ccircle cx=%22330%22 cy=%2258%22 r=%2230%22 fill=%22%23ff7a59%22 opacity=%220.85%22/%3E%3C/svg%3E';

export function HotelCard({ hotel, index, onSelect, isDisabled }: HotelCardProps) {
  const minPrice = hotel.rates?.[0]?.price;
  const currency = hotel.rates?.[0]?.currency || 'USD';
  const location = hotel.address || hotel.city || 'Location not specified';
  const rating = hotel.rating ? Math.round(hotel.rating * 10) / 10 : null;
  const stars = hotel.stars ? Math.min(5, Math.round(hotel.stars)) : null;
  const imageUrl = hotel.image_url || hotel.image_urls?.[0] || PLACEHOLDER;
  const cleanDescription = (v?: string) =>
    (v || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();

  return (
    <div className="group rounded-2xl overflow-hidden border border-border bg-card hover:border-primary/40 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 animate-slide-up">
      {/* Image */}
      <div className="relative h-44 w-full overflow-hidden bg-secondary">
        <img
          src={imageUrl}
          alt={hotel.name}
          className="absolute inset-0 h-full w-full object-cover group-hover:scale-105 transition-transform duration-500"
          onError={(e) => { (e.target as HTMLImageElement).src = PLACEHOLDER; }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />

        {/* Price badge */}
        {typeof minPrice === 'number' && (
          <div className="absolute top-3 right-3 bg-primary text-primary-foreground rounded-xl px-3 py-1.5 shadow-lg font-bold text-sm backdrop-blur-sm">
            {currency} {minPrice}
            <span className="text-xs font-normal opacity-80 ml-1">/night</span>
          </div>
        )}

        {/* Number badge */}
        {index && (
          <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm text-foreground rounded-full w-7 h-7 flex items-center justify-center font-bold text-xs shadow-md">
            {index}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        <div>
          <h3 className="font-bold text-sm text-foreground line-clamp-1 group-hover:text-primary transition-colors">
            {hotel.name}
          </h3>
          <div className="flex items-center gap-1.5 mt-1 text-muted-foreground text-xs">
            <MapPin className="h-3 w-3 flex-shrink-0 text-primary" />
            <span className="line-clamp-1">{location}</span>
          </div>
        </div>

        {/* Stars + rating row */}
        {(stars || rating) && (
          <div className="flex items-center gap-2">
            {stars && (
              <div className="flex gap-0.5">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`h-3 w-3 ${i < stars ? 'fill-yellow-400 text-yellow-400' : 'text-border'}`}
                  />
                ))}
              </div>
            )}
            {rating && (
              <span className="text-xs font-semibold text-foreground bg-secondary px-1.5 py-0.5 rounded-md">
                {rating}
              </span>
            )}
          </div>
        )}

        {cleanDescription(hotel.description) && (
          <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
            {cleanDescription(hotel.description)}
          </p>
        )}

        <Button
          className="w-full rounded-xl bg-primary text-primary-foreground font-semibold h-9 text-xs gap-1.5 hover:bg-primary/90 hover:shadow-md hover:shadow-primary/20 active:scale-95 transition-all duration-300"
          onClick={onSelect}
          disabled={!onSelect || isDisabled}
        >
          {isDisabled ? 'Working...' : (
            <>
              Select{index ? ` #${index}` : ''}
              <ArrowRight className="h-3.5 w-3.5" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
