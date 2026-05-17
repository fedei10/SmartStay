'use client';

import { Check, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: '/month',
    description: 'For casual travelers',
    features: ['Hotel search', 'Price comparison', 'Direct bookings', 'Limited support'],
    cta: 'Get started',
    highlighted: false,
  },
  {
    name: 'Premium',
    price: '$9',
    period: '/month',
    description: 'For frequent travelers',
    features: [
      'Everything in Free',
      'AI-powered recommendations',
      'Custom price alerts',
      'Priority support 24/7',
      'Up to 20% exclusive discounts',
    ],
    cta: 'Start Premium',
    highlighted: true,
    badge: 'Most popular',
  },
  {
    name: 'Luxury',
    price: '$29',
    period: '/month',
    description: 'For luxury travelers',
    features: [
      'Everything in Premium',
      'Personal hotel concierge',
      'Priority reservations',
      'Free travel insurance',
      'Up to 40% discounts',
      'Dedicated booking agent',
    ],
    cta: 'Go Luxury',
    highlighted: false,
  },
];

export function Pricing() {
  return (
    <section id="pricing" className="py-24 sm:py-32 px-4 sm:px-6 lg:px-8 bg-background">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16 space-y-4 animate-fade-up">
          <span className="inline-flex items-center rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary uppercase tracking-widest">
            Pricing
          </span>
          <h2 className="text-4xl sm:text-5xl font-extrabold text-foreground leading-tight tracking-tight">
            Choose your plan
          </h2>
          <p className="text-lg text-muted-foreground max-w-xl mx-auto">
            All plans include best-price guarantee and secure booking.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto items-start">
          {plans.map((plan, idx) => (
            <div
              key={idx}
              className={`relative rounded-2xl overflow-hidden transition-all duration-300 animate-slide-up ${
                plan.highlighted
                  ? 'md:-mt-4 ring-2 ring-primary shadow-2xl shadow-primary/20 bg-gradient-to-br from-primary to-teal-600'
                  : 'border border-border bg-card hover:border-primary/40 hover:shadow-xl hover:-translate-y-0.5'
              }`}
              style={{ animationDelay: `${idx * 0.1}s` }}
            >
              {plan.badge && (
                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-0 flex items-center gap-1 bg-white text-primary rounded-full px-3 py-1 text-xs font-bold shadow-md">
                  <Zap className="h-3 w-3" />
                  {plan.badge}
                </div>
              )}

              <div className={`p-7 space-y-6 ${plan.badge ? 'pt-10' : ''}`}>
                <div>
                  <h3 className={`text-xl font-bold ${plan.highlighted ? 'text-white' : 'text-foreground'}`}>
                    {plan.name}
                  </h3>
                  <p className={`text-sm mt-1 ${plan.highlighted ? 'text-white/70' : 'text-muted-foreground'}`}>
                    {plan.description}
                  </p>
                </div>

                <div className="flex items-baseline gap-1">
                  <span className={`text-4xl font-extrabold ${plan.highlighted ? 'text-white' : 'text-foreground'}`}>
                    {plan.price}
                  </span>
                  <span className={`text-sm ${plan.highlighted ? 'text-white/65' : 'text-muted-foreground'}`}>
                    {plan.period}
                  </span>
                </div>

                <Button
                  asChild
                  className={`w-full h-11 rounded-xl font-bold transition-all duration-300 ${
                    plan.highlighted
                      ? 'bg-white text-primary hover:bg-white/90 shadow-lg'
                      : 'bg-primary text-primary-foreground hover:bg-primary/90'
                  }`}
                >
                  <Link href="/sign-up?redirect_url=/chat">{plan.cta}</Link>
                </Button>

                <div className={`space-y-3 pt-4 border-t ${plan.highlighted ? 'border-white/20' : 'border-border'}`}>
                  {plan.features.map((feature, fi) => (
                    <div key={fi} className="flex items-start gap-3">
                      <div className={`mt-0.5 h-5 w-5 rounded-full flex items-center justify-center flex-shrink-0 ${
                        plan.highlighted ? 'bg-white/20' : 'bg-primary/10'
                      }`}>
                        <Check className={`h-3 w-3 ${plan.highlighted ? 'text-white' : 'text-primary'}`} />
                      </div>
                      <span className={`text-sm ${plan.highlighted ? 'text-white/85' : 'text-foreground/75'}`}>
                        {feature}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-14 text-center">
          <p className="text-muted-foreground text-sm">
            Questions about pricing?{' '}
            <button className="text-primary font-semibold hover:underline transition-colors">
              Contact sales
            </button>
          </p>
        </div>
      </div>
    </section>
  );
}
