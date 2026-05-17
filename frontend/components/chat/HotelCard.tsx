'use client';

import { Hotel } from '@/lib/types';
import { Star, MapPin, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface HotelCardProps {
  hotel: Hotel;
  index?: number;
  onSelect?: () => void;
  isDisabled?: boolean;
}

export function HotelCard({ hotel, index, onSelect, isDisabled }: HotelCardProps) {
  const minPrice = hotel.rates?.[0]?.price;
  const currency = hotel.rates?.[0]?.currency || 'USD';
  const location = hotel.address || hotel.city || 'الموقع غير متوفر';
  const rating = hotel.rating ? Math.round(hotel.rating * 10) / 10 : null;
  const placeholderImage =
    'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22200%22%3E%3Crect fill=%22%2313272d%22 width=%22400%22 height=%22200%22/%3E%3Cpath d=%22M0 150 C90 100 130 165 215 120 C290 82 320 120 400 80 L400 200 L0 200 Z%22 fill=%22%231aa39a%22 opacity=%220.85%22/%3E%3Ccircle cx=%22328%22 cy=%2252%22 r=%2227%22 fill=%22%23ff7a59%22/%3E%3C/svg%3E';
  const imageUrl = hotel.image_url || hotel.image_urls?.[0] || placeholderImage;
  const cleanDescription = (value?: string) =>
    (value || '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();

  return (
    <div className="rounded-lg overflow-hidden transition-all duration-300 bg-card border border-border hover:border-primary/50 hover:shadow-lg animate-slide-up">
      {/* Image Container */}
      <div className="relative h-40 w-full bg-secondary overflow-hidden group">
        <img
          src={imageUrl}
          alt={hotel.name}
          className="absolute inset-0 h-full w-full object-cover group-hover:scale-110 transition-transform duration-500"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = placeholderImage;
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
        
        {/* Price Badge */}
        {typeof minPrice === 'number' && (
          <div className="absolute top-3 right-3 bg-primary text-primary-foreground rounded-lg px-3 py-1.5 shadow-md font-semibold text-sm">
            {currency} {minPrice}
            <span className="text-xs font-normal ml-1">/night</span>
          </div>
        )}

        {/* Number Badge */}
        {index && (
          <div className="absolute top-3 left-3 bg-white/90 text-foreground rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm shadow-md">
            {index}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        <div>
          <h3 className="font-bold text-base text-foreground mb-2 line-clamp-2 leading-tight">
            {hotel.name}
          </h3>
          <div className="flex items-center gap-2 text-muted-foreground text-sm">
            <MapPin className="h-4 w-4 flex-shrink-0 text-primary" />
            <span className="line-clamp-1">{location}</span>
          </div>
        </div>

        {/* Rating and Reviews */}
        {rating && (
          <div className="flex items-center gap-2 py-2 border-y border-border">
            <div className="flex gap-0.5">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`h-3.5 w-3.5 ${i < Math.floor(rating)
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-border'
                    }`}
                />
              ))}
            </div>
            <span className="text-xs font-semibold text-foreground ml-1">
              {rating}/5
            </span>
          </div>
        )}

        {/* Description */}
        {cleanDescription(hotel.description) && (
          <p className="text-xs text-foreground/70 line-clamp-2 leading-relaxed">
            {cleanDescription(hotel.description)}
          </p>
        )}

        {/* Amenities hint */}
        <div className="flex items-center gap-1 text-xs text-primary">
          <Check className="h-3 w-3" />
          <span>{typeof minPrice === 'number' ? 'Rate available' : 'Backend hotel result'}</span>
        </div>

        {/* Select Button */}
        <Button
          className="w-full rounded-lg bg-primary text-primary-foreground font-semibold transition-all duration-300 hover:bg-primary/90 hover:shadow-md active:scale-95 h-9 text-sm"
          onClick={onSelect}
          disabled={!onSelect || isDisabled}
        >
          {isDisabled ? 'Working...' : `Select hotel ${index ? `#${index}` : ''}`}
        </Button>
      </div>
    </div>
  );
}
