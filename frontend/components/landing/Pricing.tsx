'use client';

import { Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

const plans = [
  {
    name: 'أساسي',
    price: 'مجاني',
    description: 'للمسافرين الكاجوالين',
    features: [
      'البحث عن الفنادق',
      'المقارنة بين الأسعار',
      'الحجوزات المباشرة',
      'دعم العملاء المحدود',
    ],
    cta: 'ابدأ الآن',
    highlighted: false,
  },
  {
    name: 'بريميوم',
    price: 'ر.س 99',
    period: '/شهر',
    description: 'للمسافرين المتكررين',
    features: [
      'كل ما في الأساسي',
      'توصيات ذكية بالذكاء الاصطناعي',
      'تنبيهات الأسعار المخصصة',
      'دعم الأولوية 24/7',
      'خصومات حصرية تصل إلى 20%',
    ],
    cta: 'اشترك الآن',
    highlighted: true,
  },
  {
    name: 'فاخر',
    price: 'ر.س 299',
    period: '/شهر',
    description: 'للمسافرين الفاخرين',
    features: [
      'كل ما في البريميوم',
      'بيت قائم بالفندق الشخصي',
      'حجوزات أولويتية',
      'تأمين السفر المجاني',
      'خصومات تصل إلى 40%',
      'وسيط حجز خاص',
    ],
    cta: 'اشترك الآن',
    highlighted: false,
  },
];

export function Pricing() {
  return (
    <section className="py-20 sm:py-28 px-4 sm:px-6 lg:px-8 bg-background border-t border-border/50">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16 sm:mb-20 space-y-4 animate-fade-in">
          <p className="text-xs font-bold text-primary uppercase tracking-widest">الخطط والأسعار</p>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground leading-tight text-balance">
            اختر الخطة المناسبة لك
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            كل الخطط تتضمن ضمان أفضل سعر وحجز آمن موثوق
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8 max-w-5xl mx-auto">
          {plans.map((plan, idx) => (
            <div
              key={idx}
              className={`relative rounded-xl transition-all duration-300 overflow-hidden animate-slide-up group ${
                plan.highlighted
                  ? 'md:scale-105 bg-primary text-primary-foreground border-2 border-primary shadow-2xl'
                  : 'bg-card border border-border/50 hover:shadow-xl hover:border-primary/50'
              }`}
              style={{ animationDelay: `${idx * 0.1}s` }}
            >
              {/* Gradient overlay for highlighted card */}
              {plan.highlighted && (
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-transparent -z-10" />
              )}

              {/* Badge for highlighted */}
              {plan.highlighted && (
                <div className="absolute top-0 right-0 bg-white/20 text-primary-foreground px-4 py-1 text-xs font-bold uppercase tracking-wider rounded-bl-lg">
                  الأشهر
                </div>
              )}

              <div className="relative z-10 p-8 space-y-6">
                {/* Plan Title & Description */}
                <div>
                  <h3 className={`text-2xl font-bold mb-2 ${plan.highlighted ? 'text-primary-foreground' : 'text-foreground'}`}>
                    {plan.name}
                  </h3>
                  <p className={`text-sm ${plan.highlighted ? 'text-primary-foreground/80' : 'text-muted-foreground'}`}>
                    {plan.description}
                  </p>
                </div>

                {/* Pricing */}
                <div className="space-y-2">
                  <div className="flex items-baseline gap-2">
                    <span className={`text-4xl font-bold ${plan.highlighted ? 'text-primary-foreground' : 'text-foreground'}`}>
                      {plan.price}
                    </span>
                    {plan.period && (
                      <span className={`text-sm ${plan.highlighted ? 'text-primary-foreground/80' : 'text-muted-foreground'}`}>
                        {plan.period}
                      </span>
                    )}
                  </div>
                </div>

                {/* CTA Button */}
                <Button
                  className={`w-full py-3 font-bold rounded-lg transition-all ${
                    plan.highlighted
                      ? 'bg-white text-primary hover:bg-white/90 shadow-lg'
                      : 'bg-primary text-primary-foreground hover:bg-primary/90'
                  }`}
                  asChild
                >
                  <Link href="/sign-in?redirect_url=/chat">
                    {plan.cta}
                  </Link>
                </Button>

                {/* Features List */}
                <div className="space-y-3 pt-4 border-t border-current border-opacity-20">
                  {plan.features.map((feature, fidx) => (
                    <div key={fidx} className="flex items-start gap-3">
                      <Check className={`h-5 w-5 flex-shrink-0 mt-0.5 ${plan.highlighted ? 'text-primary-foreground' : 'text-primary'}`} />
                      <span className={`text-sm ${plan.highlighted ? 'text-primary-foreground/90' : 'text-foreground/75'}`}>
                        {feature}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* FAQ/Additional Info */}
        <div className="mt-16 sm:mt-20 text-center">
          <p className="text-muted-foreground mb-4">
            هل لديك أسئلة حول الخطط؟
          </p>
          <button className="text-primary font-medium hover:text-primary/80 transition-colors inline-flex items-center gap-2">
            تواصل مع فريق المبيعات
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </section>
  );
}
