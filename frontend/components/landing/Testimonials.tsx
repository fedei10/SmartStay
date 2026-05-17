'use client';

import { Star, Quote } from 'lucide-react';

const testimonials = [
  {
    name: 'Fatima Al-Mutairi',
    location: 'Kuwait City',
    rating: 5,
    text: 'The best travel app I have ever used. The interface is intuitive and the prices are amazing!',
    initials: 'FA',
    color: 'from-teal-500 to-cyan-500',
  },
  {
    name: 'Mohammed Al-Huwail',
    location: 'Riyadh, KSA',
    rating: 5,
    text: 'Excellent support and smart recommendations helped me find a great hotel at the right price.',
    initials: 'MH',
    color: 'from-violet-500 to-purple-500',
  },
  {
    name: 'Nour Al-Din',
    location: 'Dubai, UAE',
    rating: 5,
    text: "I've tried many travel apps but ttrip is the best in terms of price and service quality.",
    initials: 'ND',
    color: 'from-blue-500 to-indigo-500',
  },
  {
    name: 'Layla Al-Sharqawi',
    location: 'Doha, Qatar',
    rating: 5,
    text: 'Booking through ttrip is incredibly easy and secure. I recommend it to anyone looking to book.',
    initials: 'LS',
    color: 'from-pink-500 to-rose-500',
  },
];

const stats = [
  { value: '4.9★', label: 'Avg. rating' },
  { value: '50K+', label: 'Happy guests' },
  { value: '98%', label: 'Satisfaction' },
];

export function Testimonials() {
  return (
    <section id="testimonials" className="py-24 sm:py-32 px-4 sm:px-6 lg:px-8 bg-secondary/30">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16 space-y-4 animate-fade-up">
          <span className="inline-flex items-center rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary uppercase tracking-widest">
            Reviews
          </span>
          <h2 className="text-4xl sm:text-5xl font-extrabold text-foreground leading-tight tracking-tight">
            Trusted by thousands
          </h2>
          <p className="text-lg text-muted-foreground max-w-xl mx-auto">
            Real travelers, real experiences. See what people say about ttrip.
          </p>
        </div>

        {/* Stats bar */}
        <div className="grid grid-cols-3 gap-4 mb-14 max-w-lg mx-auto">
          {stats.map((s) => (
            <div key={s.label} className="text-center rounded-2xl bg-card border border-border p-4 shadow-sm">
              <p className="text-2xl font-extrabold text-primary">{s.value}</p>
              <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        {/* Cards grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {testimonials.map((t, idx) => (
            <div
              key={idx}
              className="group relative bg-card border border-border rounded-2xl p-6 hover:shadow-xl hover:border-primary/30 hover:-translate-y-0.5 transition-all duration-300 overflow-hidden animate-slide-up"
              style={{ animationDelay: `${idx * 0.1}s` }}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-primary/3 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

              <Quote className="absolute top-5 right-5 h-8 w-8 text-primary/10 group-hover:text-primary/20 transition-colors" />

              <div className="relative space-y-4">
                <div className="flex gap-1">
                  {[...Array(t.rating)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>

                <p className="text-foreground leading-relaxed text-[15px]">
                  &ldquo;{t.text}&rdquo;
                </p>

                <div className="flex items-center gap-3 pt-3 border-t border-border">
                  <div className={`h-10 w-10 rounded-full bg-gradient-to-br ${t.color} flex items-center justify-center text-white text-sm font-bold flex-shrink-0`}>
                    {t.initials}
                  </div>
                  <div>
                    <p className="font-semibold text-foreground text-sm">{t.name}</p>
                    <p className="text-xs text-muted-foreground">{t.location}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
