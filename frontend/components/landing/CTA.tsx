'use client';

import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

export function CTA() {
  return (
    <section className="py-20 sm:py-28 px-4 sm:px-6 lg:px-8 bg-background border-t border-border/50">
      <div className="max-w-4xl mx-auto text-center space-y-8 animate-fade-in">
        {/* Headline */}
        <div className="space-y-4">
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground leading-tight text-balance">
            جاهز لحجز فندقك الآن؟
          </h2>
          <p className="text-lg sm:text-xl text-muted-foreground">
            ابدأ البحث اليوم واستمتع بأفضل الأسعار المضمونة
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link href="/sign-in?redirect_url=/chat">
            <Button className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg px-8 h-12 text-base font-semibold shadow-lg hover:shadow-xl hover:shadow-primary/40 transition-all w-full sm:w-auto">
              ابدأ البحث الآن
            </Button>
          </Link>
          <Link href="#features">
            <Button variant="outline" className="border-border hover:bg-secondary rounded-lg px-8 h-12 text-base font-semibold w-full sm:w-auto flex items-center justify-center gap-2">
              تعرف على المزيد
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>

        {/* Trust Badges */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-sm text-muted-foreground flex-wrap pt-4">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            بدون رسوم مخفية
          </span>
          <span className="hidden sm:inline text-border">•</span>
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            ضمان أفضل سعر
          </span>
          <span className="hidden sm:inline text-border">•</span>
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            إلغاء مجاني
          </span>
        </div>
      </div>
    </section>
  );
}
