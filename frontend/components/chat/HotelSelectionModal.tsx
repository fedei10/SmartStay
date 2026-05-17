'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Hotel } from '@/lib/types';
import { Star, MapPin, ChevronLeft, ChevronRight } from 'lucide-react';

interface HotelSelectionModalProps {
  open: boolean;
  hotels: Hotel[];
  onSelectHotel: (index: number) => void;
  onOpenChange: (open: boolean) => void;
  isLoading?: boolean;
}

export function HotelSelectionModal({
  open,
  hotels,
  onSelectHotel,
  onOpenChange,
  isLoading,
}: HotelSelectionModalProps) {
  const validHotels = hotels.filter((hotel) => hotel && hotel.hotel_id);
  const [imageIndexByHotel, setImageIndexByHotel] = useState<Record<string, number>>({});
  const [showAllImagesByHotel, setShowAllImagesByHotel] = useState<Record<string, boolean>>({});
  const placeholderImage =
    'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22200%22%3E%3Crect fill=%22%2313272d%22 width=%22400%22 height=%22200%22/%3E%3Cpath d=%22M0 150 C90 100 130 165 215 120 C290 82 320 120 400 80 L400 200 L0 200 Z%22 fill=%22%231aa39a%22 opacity=%220.85%22/%3E%3Ccircle cx=%22328%22 cy=%2252%22 r=%2227%22 fill=%22%23ff7a59%22/%3E%3C/svg%3E';

  const cleanDescription = (value?: string) =>
    (value || '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();

  const normalizeImageKey = (value: string): string => {
    const raw = (value || '').trim();
    if (!raw) return '';
    if (raw.startsWith('data:')) return raw;
    try {
      const parsed = new URL(raw);
      return `${parsed.origin}${parsed.pathname}`;
    } catch {
      return raw.split('#')[0].split('?')[0];
    }
  };

  const dedupeImageUrls = (values: string[]): string[] => {
    const seen = new Set<string>();
    const unique: string[] = [];
    for (const value of values) {
      const clean = (value || '').trim();
      if (!clean) continue;
      const key = normalizeImageKey(clean);
      if (!key || seen.has(key)) continue;
      seen.add(key);
      unique.push(clean);
    }
    return unique;
  };

  if (validHotels.length === 0) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-[95vw] max-w-6xl max-h-[92vh] p-6 sm:p-8">
        <DialogHeader>
          <DialogTitle className="text-2xl sm:text-3xl">Available stays</DialogTitle>
          <DialogDescription className="text-sm sm:text-base">
            Compare {validHotels.length} backend results with images, ratings, and rate details.
          </DialogDescription>
        </DialogHeader>

        <Separator />

        <ScrollArea className="h-[72vh] pr-4">
          <div className="space-y-4">
            {validHotels.map((hotel, index) => {
              const minPrice = hotel.rates?.[0]?.price;
              const rateCurrency = hotel.rates?.[0]?.currency || '';
              const roomType = hotel.rates?.[0]?.room_type || 'غرفة قياسية';
              const boardType = hotel.rates?.[0]?.board_type || 'إقامة فقط';
              const location = hotel.address || hotel.city || 'الموقع غير متوفر';
              const rating = hotel.rating ? Math.round(hotel.rating * 10) / 10 : null;
              const imageUrls = dedupeImageUrls([
                ...(hotel.image_urls || []),
                hotel.image_url || '',
              ]);
              const activeImageIndex = Math.min(
                imageIndexByHotel[hotel.hotel_id] || 0,
                Math.max(imageUrls.length - 1, 0)
              );
              const activeImage = imageUrls[activeImageIndex] || placeholderImage;

              return (
                <div key={hotel.hotel_id} className="group">
                  <div className="rounded-lg overflow-hidden bg-card border border-border hover:border-primary transition-all duration-300 md:grid md:grid-cols-[1.6fr_1fr]">
                    {/* Image and Price Section */}
                    <div className="relative h-64 sm:h-72 md:h-full md:min-h-[330px] bg-secondary overflow-hidden">
                      <img
                        src={activeImage}
                        alt={hotel.name}
                        className="absolute inset-0 h-full w-full object-cover group-hover:scale-110 transition-transform duration-500"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.src = placeholderImage;
                        }}
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />

                      {/* Badge - Number and Price */}
                      <div className="absolute inset-0 flex items-start justify-between p-4">
                        <Badge className="bg-white/90 text-foreground text-lg font-bold px-3 py-1">
                          #{index + 1}
                        </Badge>
                        {typeof minPrice === 'number' && (
                          <Badge className="bg-primary text-primary-foreground text-lg font-bold px-3 py-1">
                            {rateCurrency ? `${rateCurrency} ${minPrice}` : `$${minPrice}`}/night
                          </Badge>
                        )}
                      </div>

                      {imageUrls.length > 1 && (
                        <>
                          <button
                            type="button"
                            onClick={() =>
                              setImageIndexByHotel((prev) => ({
                                ...prev,
                                [hotel.hotel_id]:
                                  activeImageIndex === 0 ? imageUrls.length - 1 : activeImageIndex - 1,
                              }))
                            }
                            className="absolute left-3 top-1/2 -translate-y-1/2 rounded-full bg-black/55 text-white p-2 hover:bg-black/70"
                            aria-label="Previous image"
                          >
                            <ChevronLeft className="h-4 w-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() =>
                              setImageIndexByHotel((prev) => ({
                                ...prev,
                                [hotel.hotel_id]:
                                  activeImageIndex === imageUrls.length - 1 ? 0 : activeImageIndex + 1,
                              }))
                            }
                            className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full bg-black/55 text-white p-2 hover:bg-black/70"
                            aria-label="Next image"
                          >
                            <ChevronRight className="h-4 w-4" />
                          </button>
                          <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex items-center gap-1">
                            {imageUrls.map((_, imgIndex) => (
                              <span
                                key={`${hotel.hotel_id}-img-dot-${imgIndex}`}
                                className={`h-1.5 w-1.5 rounded-full ${
                                  imgIndex === activeImageIndex ? 'bg-white' : 'bg-white/55'
                                }`}
                              />
                            ))}
                          </div>
                        </>
                      )}
                    </div>

                    {/* Content Section */}
                    <div className="flex flex-col p-5 sm:p-6 space-y-4">
                      {/* Name and Location */}
                      <div>
                        <h3 className="font-bold text-lg text-foreground mb-2 line-clamp-2">
                          {hotel.name}
                        </h3>
                        <div className="flex items-center gap-2 text-muted-foreground text-sm">
                          <MapPin className="h-4 w-4 flex-shrink-0 text-primary" />
                          <span className="line-clamp-1">{location}</span>
                        </div>
                      </div>

                      {/* Rating */}
                      {rating && (
                        <div className="flex items-center gap-3">
                          <div className="flex gap-0.5">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                className={`h-4 w-4 ${
                                  i < Math.floor(rating)
                                    ? 'fill-yellow-400 text-yellow-400'
                                    : 'text-border'
                                }`}
                              />
                            ))}
                          </div>
                          <span className="text-sm font-semibold text-foreground">
                            {rating}/5
                          </span>
                        </div>
                      )}

                      {/* Description */}
                      {cleanDescription(hotel.description) && (
                        <p className="text-sm text-foreground/70 line-clamp-2">
                          {cleanDescription(hotel.description)}
                        </p>
                      )}

                      {/* View all images */}
                      {imageUrls.length > 1 && (
                        <div className="pt-1">
                          <button
                            type="button"
                            className="text-xs font-semibold text-primary hover:underline"
                            onClick={() =>
                              setShowAllImagesByHotel((prev) => ({
                                ...prev,
                                [hotel.hotel_id]: !prev[hotel.hotel_id],
                              }))
                            }
                          >
                            {showAllImagesByHotel[hotel.hotel_id]
                              ? 'Hide images'
                              : `View all images (${imageUrls.length})`}
                          </button>
                          {showAllImagesByHotel[hotel.hotel_id] && (
                            <div className="mt-2 grid grid-cols-4 md:grid-cols-5 gap-2">
                              {imageUrls.map((img, imgIndex) => (
                                <button
                                  key={`${hotel.hotel_id}-thumb-${imgIndex}`}
                                  type="button"
                                  onClick={() =>
                                    setImageIndexByHotel((prev) => ({
                                      ...prev,
                                      [hotel.hotel_id]: imgIndex,
                                    }))
                                  }
                                  className={`relative h-16 overflow-hidden rounded-md border ${
                                    imgIndex === activeImageIndex ? 'border-primary' : 'border-border'
                                  }`}
                                  aria-label={`Image ${imgIndex + 1}`}
                                >
                                  <img
                                    src={img}
                                    alt={`${hotel.name}-${imgIndex + 1}`}
                                    className="absolute inset-0 h-full w-full object-cover"
                                    onError={(e) => {
                                      const target = e.target as HTMLImageElement;
                                      target.src = placeholderImage;
                                    }}
                                  />
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Rate details */}
                      <div className="text-sm text-foreground/80 space-y-1">
                        <p className="line-clamp-1">
                          <span className="font-semibold">Room:</span> {roomType}
                        </p>
                        <p className="line-clamp-1">
                          <span className="font-semibold">Board:</span> {boardType}
                        </p>
                      </div>

                      {/* Select Button */}
                      <Button
                        onClick={() => onSelectHotel(index + 1)}
                        disabled={isLoading}
                        className="w-full mt-4 md:mt-auto h-10 font-semibold rounded-lg"
                      >
                        {isLoading ? 'Working...' : `Select hotel ${index + 1}`}
                      </Button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
