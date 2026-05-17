'use client';

import { Bot, CreditCard, Map, MessageSquare, Plane, WalletCards } from 'lucide-react';

const features = [
  {
    icon: MessageSquare,
    title: 'Chat-first planning',
    description: 'Ask for hotels, flights, or a combined plan and let the backend route the request.',
  },
  {
    icon: Map,
    title: 'Visual stay cards',
    description: 'Hotel results keep images, location, rating, and rate details ready for fast comparison.',
  },
  {
    icon: Plane,
    title: 'Flight connectors',
    description: 'Frontend routes now proxy to the current FastAPI flight search, verify, prebook, and booking endpoints.',
  },
  {
    icon: CreditCard,
    title: 'LiteAPI booking flow',
    description: 'Hotel prebook and book endpoints stay server-side so provider keys never move into the browser.',
  },
  {
    icon: WalletCards,
    title: 'Travel workspace',
    description: 'The interface is organized around trip planning instead of the old hotel-only frontend.',
  },
  {
    icon: Bot,
    title: 'Agent-ready backend',
    description: 'The UI consumes the backend response envelope and metadata shape used by the new travel agents.',
  },
];

export function Features() {
  return (
    <section className="py-20 sm:py-28 px-4 sm:px-6 lg:px-8 bg-background border-t border-border/50">
      <div className="max-w-6xl mx-auto">
        <div className="mb-14 max-w-3xl space-y-4 animate-fade-in">
          <p className="text-xs font-bold text-primary uppercase tracking-widest">What changed</p>
          <h2 className="text-4xl sm:text-5xl font-bold text-foreground leading-tight text-balance">
            A travel planner wired to the new backend
          </h2>
          <p className="text-lg text-muted-foreground">
            Inspired by TREK-style trip tooling: practical planning surfaces, image-rich results, and backend-driven flows.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="group relative bg-card border border-border rounded-lg p-6 hover:shadow-lg hover:border-primary/50 transition-all duration-300 animate-slide-up"
                style={{ animationDelay: `${idx * 0.08}s` }}
              >
                <div className="mb-5 bg-primary/10 group-hover:bg-primary/15 rounded-md p-3 w-fit transition-all">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-bold text-foreground group-hover:text-primary transition-colors">
                  {feature.title}
                </h3>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
