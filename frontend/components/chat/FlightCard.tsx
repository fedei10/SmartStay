'use client';

import { FlightOffer } from '@/lib/types';
import { Plane, Clock, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FlightCardProps {
  flight: FlightOffer;
  index?: number;
  onSelect?: () => void;
  isDisabled?: boolean;
}

function parseDuration(iso: string | undefined): string {
  if (!iso) return '';
  const m = iso.match(/PT(?:(\d+)H)?(?:(\d+)M)?/);
  if (!m) return iso;
  return [m[1] ? `${m[1]}h` : '', m[2] ? `${m[2]}m` : ''].filter(Boolean).join(' ');
}

function fmt(dt: string | undefined, part: 'time' | 'date'): string {
  if (!dt || dt.length < 10) return '';
  return part === 'time' ? dt.slice(11, 16) : dt.slice(0, 10);
}

export function FlightCard({ flight, index, onSelect, isDisabled }: FlightCardProps) {
  const price = flight.price;
  const currency = flight.currency || 'USD';
  const airline = flight.airline || flight.segments?.[0]?.carrier || 'Airline';
  const stops = flight.stops ?? Math.max(0, (flight.segments?.length ?? 1) - 1);
  const stopsLabel = stops === 0 ? 'Direct' : `${stops} stop${stops > 1 ? 's' : ''}`;
  const depTime = fmt(flight.departure_time, 'time');
  const arrTime = fmt(flight.arrival_time, 'time');
  const depDate = fmt(flight.departure_time, 'date');
  const duration = parseDuration(flight.duration);
  const origin = flight.segments?.[0]?.from;
  const dest = flight.segments?.[flight.segments.length - 1]?.to;

  return (
    <div className="group rounded-2xl overflow-hidden border border-border bg-card hover:border-primary/40 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 animate-slide-up">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-secondary/40 border-b border-border/60">
        <div className="flex items-center gap-2">
          {index && (
            <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold flex-shrink-0">
              {index}
            </span>
          )}
          <div className="h-7 w-7 rounded-lg bg-primary/10 flex items-center justify-center">
            <Plane className="h-3.5 w-3.5 text-primary" />
          </div>
          <span className="font-semibold text-sm text-foreground group-hover:text-primary transition-colors">{airline}</span>
        </div>
        {price != null && (
          <div className="text-right">
            <span className="text-lg font-extrabold text-primary">{currency} {Math.round(price)}</span>
            <span className="text-[10px] text-muted-foreground ml-1">/ person</span>
          </div>
        )}
      </div>

      {/* Route */}
      <div className="px-4 py-4">
        <div className="flex items-center justify-between gap-3">
          <div className="text-center min-w-[48px]">
            <p className="text-2xl font-extrabold text-foreground tabular-nums">{depTime || '--:--'}</p>
            <p className="text-[11px] font-semibold text-muted-foreground mt-0.5">{origin || '---'}</p>
          </div>

          <div className="flex-1 flex flex-col items-center gap-1">
            <span className="text-[10px] font-medium text-muted-foreground">{duration}</span>
            <div className="flex items-center w-full gap-1">
              <div className="flex-1 h-px bg-border" />
              <div className="h-5 w-5 rounded-full bg-primary/10 flex items-center justify-center">
                <Plane className="h-2.5 w-2.5 text-primary" />
              </div>
              <div className="flex-1 h-px bg-border" />
            </div>
            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
              stops === 0 ? 'bg-green-500/10 text-green-600' : 'bg-amber-500/10 text-amber-600'
            }`}>
              {stopsLabel}
            </span>
          </div>

          <div className="text-center min-w-[48px]">
            <p className="text-2xl font-extrabold text-foreground tabular-nums">{arrTime || '--:--'}</p>
            <p className="text-[11px] font-semibold text-muted-foreground mt-0.5">{dest || '---'}</p>
          </div>
        </div>

        {depDate && (
          <div className="flex items-center gap-1 mt-2.5 text-[10px] text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>{depDate}</span>
          </div>
        )}
      </div>

      {/* Select button */}
      <div className="px-4 pb-4">
        <Button
          className="w-full rounded-xl bg-primary text-primary-foreground font-semibold h-9 text-xs gap-1.5 hover:bg-primary/90 hover:shadow-md hover:shadow-primary/20 active:scale-95 transition-all duration-300"
          onClick={onSelect}
          disabled={!onSelect || isDisabled}
        >
          {isDisabled ? 'Working...' : (
            <>
              Select flight{index ? ` #${index}` : ''}
              <ArrowRight className="h-3.5 w-3.5" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
