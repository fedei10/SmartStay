'use client';

import { FlightOffer } from '@/lib/types';
import { FlightCard } from './FlightCard';

interface FlightSelectionListProps {
  flights?: FlightOffer[];
  onSelectFlight?: (index: number) => void;
  isLoading?: boolean;
}

export function FlightSelectionList({ flights, onSelectFlight, isLoading }: FlightSelectionListProps) {
  if (!Array.isArray(flights) || flights.length === 0) return null;

  const valid = flights.filter((f) => f && (f.offer_id || f.offerId || f.departure_time));
  if (valid.length === 0) return null;

  return (
    <div className="mt-4 space-y-3">
      {valid.map((flight, i) => (
        <FlightCard
          key={flight.offer_id || flight.offerId || i}
          flight={flight}
          index={i + 1}
          onSelect={onSelectFlight ? () => onSelectFlight(i + 1) : undefined}
          isDisabled={isLoading}
        />
      ))}
    </div>
  );
}
