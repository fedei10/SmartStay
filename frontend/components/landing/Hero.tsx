'use client';

import Link from 'next/link';
import { Calendar, MapPin, Search, Sparkles, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useState } from 'react';

const previewHotels = [
  {
    name: 'Canal House Stay',
    place: 'Amsterdam',
    price: '$182',
    image:
      'https://images.unsplash.com/photo-1519821172141-b5d8b9a5c9c9?auto=format&fit=crop&w=900&q=80',
  },
  {
    name: 'Riad Courtyard',
    place: 'Marrakesh',
    price: '$96',
    image:
      'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=900&q=80',
  },
];

export function Hero() {
  const [destination, setDestination] = useState('');
  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');
  const [guests, setGuests] = useState('');

  const chatHref = destination.trim()
    ? `/chat?initial=${encodeURIComponent(`Find stays in ${destination.trim()}`)}`
    : '/chat';

  return (
    <section className="relative w-full min-h-[92vh] flex items-center pt-20 overflow-hidden bg-background">
      <img
        src="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=2400&q=85"
        alt="Mountain road trip landscape"
        className="absolute inset-0 h-full w-full object-cover"
      />
      <div className="absolute inset-0 bg-black/45" />
      <div className="absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-background to-transparent" />

      <div className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid gap-8 lg:grid-cols-[1.05fr_0.95fr] lg:items-end">
          <div className="max-w-3xl space-y-7 text-white animate-fade-in">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/15 px-4 py-2 text-xs font-semibold backdrop-blur-md">
              <Sparkles className="h-4 w-4 text-primary" />
              AI travel planning connected to your booking backend
            </div>

            <div className="space-y-4">
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold leading-tight text-balance">
                ttrip
              </h1>
              <p className="max-w-2xl text-lg sm:text-xl leading-relaxed text-white/85">
                Build a trip from a conversation, compare stays in visual cards, and keep the next step close.
              </p>
            </div>

            <div className="grid max-w-3xl grid-cols-1 gap-3 rounded-lg border border-white/20 bg-background/95 p-4 text-foreground shadow-2xl sm:grid-cols-2 lg:grid-cols-4">
              <label className="space-y-2">
                <span className="text-xs font-bold uppercase text-muted-foreground">Destination</span>
                <span className="relative block">
                  <MapPin className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-primary" />
                  <Input
                    type="text"
                    placeholder="Lisbon, Kyoto..."
                    value={destination}
                    onChange={(event) => setDestination(event.target.value)}
                    className="h-11 rounded-md bg-secondary/70 pl-9"
                  />
                </span>
              </label>

              <label className="space-y-2">
                <span className="text-xs font-bold uppercase text-muted-foreground">Check in</span>
                <span className="relative block">
                  <Calendar className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-primary" />
                  <Input
                    type="date"
                    value={checkIn}
                    onChange={(event) => setCheckIn(event.target.value)}
                    className="h-11 rounded-md bg-secondary/70 pl-9"
                  />
                </span>
              </label>

              <label className="space-y-2">
                <span className="text-xs font-bold uppercase text-muted-foreground">Check out</span>
                <span className="relative block">
                  <Calendar className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-primary" />
                  <Input
                    type="date"
                    value={checkOut}
                    onChange={(event) => setCheckOut(event.target.value)}
                    className="h-11 rounded-md bg-secondary/70 pl-9"
                  />
                </span>
              </label>

              <label className="space-y-2">
                <span className="text-xs font-bold uppercase text-muted-foreground">Travelers</span>
                <span className="relative block">
                  <Users className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-primary" />
                  <select
                    value={guests}
                    onChange={(event) => setGuests(event.target.value)}
                    className="h-11 w-full rounded-md border border-input bg-secondary/70 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="">Select</option>
                    <option value="1">1 traveler</option>
                    <option value="2">2 travelers</option>
                    <option value="3">3 travelers</option>
                    <option value="4">4 travelers</option>
                    <option value="5+">5+ travelers</option>
                  </select>
                </span>
              </label>

              <Button asChild className="h-11 rounded-md sm:col-span-2 lg:col-span-4">
                <Link href={chatHref}>
                  <Search className="h-4 w-4" />
                  Start planning
                </Link>
              </Button>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
            {previewHotels.map((hotel) => (
              <div key={hotel.name} className="overflow-hidden rounded-lg border border-white/20 bg-background/95 shadow-2xl">
                <div className="relative h-44">
                  <img src={hotel.image} alt={hotel.name} className="absolute inset-0 h-full w-full object-cover" />
                  <div className="absolute right-3 top-3 rounded-md bg-primary px-3 py-1 text-sm font-bold text-primary-foreground">
                    {hotel.price}
                  </div>
                </div>
                <div className="space-y-1 p-4">
                  <p className="text-sm font-bold text-foreground">{hotel.name}</p>
                  <p className="text-sm text-muted-foreground">{hotel.place}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
