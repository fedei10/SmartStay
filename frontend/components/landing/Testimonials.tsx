'use client';

import { Star } from 'lucide-react';

const testimonials = [
  {
    name: 'فاطمة المطيري',
    location: 'الكويت',
    rating: 5,
    text: 'أفضل تطبيق استخدمته لحجز الفنادق. الواجهة سهلة والأسعار رائعة!',
    image: '👩‍💼',
  },
  {
    name: 'محمد الهويل',
    location: 'السعودية',
    rating: 5,
    text: 'الدعم ممتاز والتوصيات الذكية ساعدتني في إيجاد فندق رائع بسعر مناسب.',
    image: '👨‍💼',
  },
  {
    name: 'نور الدين',
    location: 'الإمارات',
    rating: 5,
    text: 'جربت عدة تطبيقات لكن ttrip الأفضل من ناحية السعر والخدمة.',
    image: '👨‍💻',
  },
  {
    name: 'ليلى الشرقاوي',
    location: 'قطر',
    rating: 5,
    text: 'الحجز من خلال ttrip سهل جداً وآمن. أنصح به لأي شخص يريد حجز فندق.',
    image: '👩‍🦰',
  },
];

export function Testimonials() {
  return (
    <section className="py-20 sm:py-28 px-4 sm:px-6 lg:px-8 bg-background border-t border-border/50">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16 sm:mb-20 space-y-4 animate-fade-in">
          <p className="text-xs font-bold text-primary uppercase tracking-widest">التقييمات</p>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground leading-tight text-balance">
            يثق بنا الملايين حول العالم
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            اقرأ تقييمات عملائنا الراضين عن خدماتنا
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8">
          {testimonials.map((testimonial, idx) => (
            <div
              key={idx}
              className="group relative bg-card border border-border/50 rounded-xl p-7 hover:shadow-xl hover:border-primary/50 transition-all duration-300 overflow-hidden animate-slide-up"
              style={{ animationDelay: `${idx * 0.1}s` }}
            >
              {/* Gradient overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10" />

              <div className="relative z-10 space-y-4">
                {/* Stars */}
                <div className="flex gap-1">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-primary text-primary" />
                  ))}
                </div>

                {/* Quote */}
                <p className="text-foreground leading-relaxed text-base">
                  "{testimonial.text}"
                </p>

                {/* Author */}
                <div className="flex items-center gap-3 pt-2 border-t border-border">
                  <div className="text-3xl">{testimonial.image}</div>
                  <div>
                    <p className="font-semibold text-foreground text-sm">{testimonial.name}</p>
                    <p className="text-xs text-muted-foreground">{testimonial.location}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Social Proof Stats */}
        <div className="mt-16 sm:mt-20 grid grid-cols-3 gap-4 sm:gap-8">
          <div className="text-center p-6 rounded-lg bg-secondary/30 border border-border/30">
            <p className="text-3xl sm:text-4xl font-bold text-primary">4.9★</p>
            <p className="text-xs text-muted-foreground mt-2">متوسط التقييم</p>
          </div>
          <div className="text-center p-6 rounded-lg bg-secondary/30 border border-border/30">
            <p className="text-3xl sm:text-4xl font-bold text-primary">50K+</p>
            <p className="text-xs text-muted-foreground mt-2">عميل سعيد</p>
          </div>
          <div className="text-center p-6 rounded-lg bg-secondary/30 border border-border/30">
            <p className="text-3xl sm:text-4xl font-bold text-primary">98%</p>
            <p className="text-xs text-muted-foreground mt-2">رضا العملاء</p>
          </div>
        </div>
      </div>
    </section>
  );
}
