'use client';

import Link from 'next/link';
import { Calendar, MapPin, Search, Sparkles, Users, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useState } from 'react';

const heroStats = [
  { value: '50K+', label: 'Happy travelers' },
  { value: '180+', label: 'Countries' },
  { value: '4.9★', label: 'Avg. rating' },
];

const previewHotels = [
  {
    name: 'Canal House Stay',
    place: 'Amsterdam',
    price: '$182',
    tag: 'Trending',
    image: 'https://images.unsplash.com/photo-1519821172141-b5d8b9a5c9c9?auto=format&fit=crop&w=900&q=80',
  },
  {
    name: 'Riad Courtyard',
    place: 'Marrakesh',
    price: '$96',
    tag: 'Best value',
    image: 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=900&q=80',
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
    <section className="relative w-full min-h-[95vh] flex items-center pt-16 overflow-hidden">
      {/* Background */}
      <img
        src="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=2400&q=85"
        alt="Travel landscape"
        className="absolute inset-0 h-full w-full object-cover"
      />
      <div className="absolute inset-0 bg-gradient-to-br from-black/70 via-black/40 to-black/55" />
      <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent" />
      {/* Grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.035]"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.6) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.6) 1px,transparent 1px)',
          backgroundSize: '64px 64px',
        }}
      />

      <div className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">

          {/* Left */}
          <div className="space-y-8 text-white animate-fade-up">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/10 backdrop-blur-md px-4 py-2 text-xs font-semibold">
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              AI-powered travel planning &amp; booking
            </div>

            <div className="space-y-4">
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold leading-none tracking-tight">
                <span className="block">Plan any</span>
                <span className="block bg-gradient-to-r from-primary via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                  trip in chat
                </span>
              </h1>
              <p className="max-w-lg text-base sm:text-lg text-white/75 leading-relaxed">
                Describe where you want to go. The AI finds hotels, flights, and deals — then books them securely.
              </p>
            </div>

            {/* Search card */}
            <div className="rounded-2xl border border-white/20 bg-background/96 backdrop-blur-xl p-5 text-foreground shadow-2xl">
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <label className="space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Destination</span>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-primary" />
                    <Input
                      type="text"
                      placeholder="Lisbon, Kyoto..."
                      value={destination}
                      onChange={(e) => setDestination(e.target.value)}
                      className="h-11 rounded-xl bg-secondary/60 pl-9 border-transparent focus-visible:border-primary focus-visible:ring-1 focus-visible:ring-primary"
                    />
                  </div>
                </label>

                <label className="space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Check in</span>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-primary" />
                    <Input
                      type="date"
                      value={checkIn}
                      onChange={(e) => setCheckIn(e.target.value)}
                      className="h-11 rounded-xl bg-secondary/60 pl-9 border-transparent focus-visible:border-primary focus-visible:ring-1 focus-visible:ring-primary"
                    />
                  </div>
                </label>

                <label className="space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Check out</span>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-primary" />
                    <Input
                      type="date"
                      value={checkOut}
                      onChange={(e) => setCheckOut(e.target.value)}
                      className="h-11 rounded-xl bg-secondary/60 pl-9 border-transparent focus-visible:border-primary focus-visible:ring-1 focus-visible:ring-primary"
                    />
                  </div>
                </label>

                <label className="space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Travelers</span>
                  <div className="relative">
                    <Users className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-primary" />
                    <select
                      value={guests}
                      onChange={(e) => setGuests(e.target.value)}
                      className="h-11 w-full rounded-xl border border-border/50 bg-secondary/60 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-primary transition-shadow"
                    >
                      <option value="">Select</option>
                      <option>1 traveler</option>
                      <option>2 travelers</option>
                      <option>3 travelers</option>
                      <option>4 travelers</option>
                      <option>5+ travelers</option>
                    </select>
                  </div>
                </label>
              </div>

              <Button
                asChild
                className="mt-4 h-12 w-full rounded-xl bg-primary text-primary-foreground text-sm font-bold shadow-lg hover:shadow-primary/40 hover:bg-primary/90 transition-all duration-300 gap-2"
              >
                <Link href={chatHref}>
                  <Search className="h-4 w-4" />
                  Start planning with AI
                  <ArrowRight className="h-4 w-4 ml-auto" />
                </Link>
              </Button>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-8 pt-1">
              {heroStats.map((s) => (
                <div key={s.label}>
                  <p className="text-xl font-bold text-white">{s.value}</p>
                  <p className="text-xs text-white/50">{s.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Right — preview cards */}
          <div className="hidden lg:flex flex-col gap-4 animate-fade-in" style={{ animationDelay: '0.2s' }}>
            {previewHotels.map((hotel, i) => (
              <div
                key={hotel.name}
                className="group overflow-hidden rounded-2xl border border-white/15 bg-white/10 backdrop-blur-xl shadow-2xl hover:-translate-y-1 transition-all duration-300"
                style={{ animationDelay: `${0.3 + i * 0.15}s` }}
              >
                <div className="relative h-44 overflow-hidden">
                  <img
                    src={hotel.image}
                    alt={hotel.name}
                    className="absolute inset-0 h-full w-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
                  <div className="absolute top-3 left-3 rounded-full bg-primary px-3 py-1 text-xs font-bold text-primary-foreground">
                    {hotel.tag}
                  </div>
                  <div className="absolute top-3 right-3 rounded-xl bg-black/50 backdrop-blur-sm px-3 py-1 text-sm font-bold text-white">
                    {hotel.price}
                    <span className="text-xs font-normal text-white/60">/night</span>
                  </div>
                </div>
                <div className="p-4 flex items-center justify-between">
                  <div>
                    <p className="font-bold text-white text-sm">{hotel.name}</p>
                    <p className="text-xs text-white/55 mt-0.5 flex items-center gap-1">
                      <MapPin className="h-3 w-3" />{hotel.place}
                    </p>
                  </div>
                  <div className="flex gap-0.5">
                    {[...Array(5)].map((_, j) => (
                      <svg key={j} className="h-3 w-3 fill-yellow-400 text-yellow-400" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                </div>
              </div>
            ))}

            <div className="rounded-2xl border border-white/15 bg-white/10 backdrop-blur-xl p-4 flex items-center gap-3">
              <div className="h-9 w-9 rounded-xl bg-primary/20 flex items-center justify-center flex-shrink-0">
                <Sparkles className="h-4 w-4 text-primary" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">"Find me a riad in Marrakesh for 2"</p>
                <p className="text-xs text-white/45 mt-0.5">AI searching hotels, comparing rates...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
