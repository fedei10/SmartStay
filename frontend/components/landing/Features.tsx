'use client';

import { Bot, CreditCard, Map, MessageSquare, Plane, WalletCards } from 'lucide-react';

const features = [
  {
    icon: MessageSquare,
    title: 'Chat-first planning',
    description: 'Ask for hotels, flights, or a combined plan and let the AI route the request instantly.',
    color: 'from-teal-500/20 to-teal-500/5',
    iconColor: 'text-teal-500',
  },
  {
    icon: Map,
    title: 'Visual stay cards',
    description: 'Hotel results include images, location, rating, and live rates — ready for fast comparison.',
    color: 'from-blue-500/20 to-blue-500/5',
    iconColor: 'text-blue-500',
  },
  {
    icon: Plane,
    title: 'Flight connectors',
    description: 'Search, verify, prebook and book flights end-to-end through the same conversational interface.',
    color: 'from-indigo-500/20 to-indigo-500/5',
    iconColor: 'text-indigo-500',
  },
  {
    icon: CreditCard,
    title: 'Secure booking flow',
    description: 'Hotel prebook and book endpoints stay server-side. Provider keys never reach the browser.',
    color: 'from-violet-500/20 to-violet-500/5',
    iconColor: 'text-violet-500',
  },
  {
    icon: WalletCards,
    title: 'Travel workspace',
    description: 'Organized around trip planning — manage conversations, view booking history, track status.',
    color: 'from-pink-500/20 to-pink-500/5',
    iconColor: 'text-pink-500',
  },
  {
    icon: Bot,
    title: 'Agent-ready backend',
    description: 'Multi-agent LangGraph backend handles orchestration, slot-filling, and LiteAPI calls.',
    color: 'from-orange-500/20 to-orange-500/5',
    iconColor: 'text-orange-500',
  },
];

export function Features() {
  return (
    <section id="features" className="py-24 sm:py-32 px-4 sm:px-6 lg:px-8 bg-background">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-16 max-w-2xl space-y-4 animate-fade-up">
          <span className="inline-flex items-center rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary uppercase tracking-widest">
            Platform
          </span>
          <h2 className="text-4xl sm:text-5xl font-extrabold text-foreground leading-tight tracking-tight text-balance">
            Everything in one conversation
          </h2>
          <p className="text-lg text-muted-foreground leading-relaxed">
            A travel AI connected to real booking infrastructure — hotels, flights, payments, all from chat.
          </p>
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="group relative rounded-2xl border border-border bg-card p-6 overflow-hidden hover:border-primary/40 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 animate-slide-up"
                style={{ animationDelay: `${idx * 0.07}s` }}
              >
                {/* Gradient bg on hover */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />

                <div className="relative">
                  <div className={`mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${feature.color} border border-current/10`}>
                    <Icon className={`h-5 w-5 ${feature.iconColor}`} />
                  </div>
                  <h3 className="text-base font-bold text-foreground group-hover:text-primary transition-colors mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
