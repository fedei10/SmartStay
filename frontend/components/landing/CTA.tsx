'use client';

import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowRight, Shield, Tag, RotateCcw } from 'lucide-react';

const trust = [
  { icon: Shield, label: 'No hidden fees' },
  { icon: Tag, label: 'Best price guarantee' },
  { icon: RotateCcw, label: 'Free cancellation' },
];

export function CTA() {
  return (
    <section className="relative py-24 sm:py-32 px-4 sm:px-6 lg:px-8 overflow-hidden">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary via-teal-600 to-cyan-700" />
      {/* Grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.06]"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.8) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.8) 1px,transparent 1px)',
          backgroundSize: '48px 48px',
        }}
      />
      {/* Radial glow */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,0.12)_0%,transparent_65%)]" />

      <div className="relative z-10 max-w-4xl mx-auto text-center space-y-10 animate-fade-up">
        <div className="space-y-5">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 backdrop-blur-md px-4 py-1.5 text-xs font-bold text-white uppercase tracking-widest">
            Get started free
          </div>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white leading-tight tracking-tight text-balance">
            Ready to book your<br />perfect trip?
          </h2>
          <p className="text-lg sm:text-xl text-white/75 max-w-xl mx-auto">
            Start a conversation, find the best deals, and book everything in minutes.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link href="/sign-up?redirect_url=/chat">
            <Button className="bg-white text-primary hover:bg-white/90 rounded-xl px-8 h-12 text-base font-bold shadow-xl hover:shadow-2xl transition-all duration-300 w-full sm:w-auto gap-2">
              Start for free
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/sign-in?redirect_url=/chat">
            <Button variant="ghost" className="border border-white/30 text-white hover:bg-white/10 rounded-xl px-8 h-12 text-base font-semibold w-full sm:w-auto">
              Sign in
            </Button>
          </Link>
        </div>

        {/* Trust badges */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-sm text-white/80">
          {trust.map((item, i) => (
            <span key={i} className="flex items-center gap-2">
              <item.icon className="h-4 w-4 text-white/90" />
              {item.label}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
