'use client';

import { Hotel } from '@/lib/types';
import { HotelCard } from './HotelCard';

interface HotelSelectionListProps {
  hotels?: Hotel[];
  onSelectHotel?: (selection: number) => void;
  isLoading?: boolean;
}

export function HotelSelectionList({
  hotels,
  onSelectHotel,
  isLoading,
}: HotelSelectionListProps) {
  if (!Array.isArray(hotels) || hotels.length === 0) {
    return null;
  }

  const validHotels = hotels.filter((hotel) => hotel && hotel.hotel_id);

  if (validHotels.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 space-y-3">
      {validHotels.map((hotel, index) => (
        <HotelCard
          key={hotel.hotel_id}
          hotel={hotel}
          index={index + 1}
          onSelect={onSelectHotel ? () => onSelectHotel(index + 1) : undefined}
          isDisabled={isLoading}
        />
      ))}
    </div>
  );
}
