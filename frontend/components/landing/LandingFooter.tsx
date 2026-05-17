'use client';

import Link from 'next/link';
import { Heart } from 'lucide-react';

export function LandingFooter() {
  return (
    <footer className="bg-foreground/5 border-t border-border px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          <div className="space-y-4">
            <h3 className="text-2xl font-bold text-foreground">ttrip</h3>
            <p className="text-muted-foreground">
              منصة حجز الفنادق الذكية برعاية الذكاء الاصطناعي.
            </p>
          </div>

          <div className="space-y-4">
            <h4 className="font-bold text-foreground">الشركة</h4>
            <ul className="space-y-2">
              <li><Link href="#" className="text-muted-foreground hover:text-primary transition-colors">عن ttrip</Link></li>
              <li><Link href="#" className="text-muted-foreground hover:text-primary transition-colors">الوظائف</Link></li>
              <li><Link href="#" className="text-muted-foreground hover:text-primary transition-colors">المدونة</Link></li>
              <li><Link href="#" className="text-muted-foreground hover:text-primary transition-colors">الإعلام</Link></li>
            </ul>
          </div>

          <div className="space-y-4">
            <h4 className="font-bold text-foreground">المساعدة</h4>
            <ul className="space-y-2">
              <li><Link href="#" className="text-muted-foreground hover:text-primary transition-colors">مركز المساعدة</Link></li>
              <li><Link href="#" className="text-muted-foreground hover:text-primary transition-colors">اتصل بنا</Link></li>
              <li><Link href="#" className="text-muted-foreground hover:text-primary transition-colors">الأسئلة الشائعة</Link></li>
              <li><Link href="#" className="text-muted-foreground hover:text-primary transition-colors">حالة النظام</Link></li>
            </ul>
          </div>

          <div className="space-y-4">
            <h4 className="font-bold text-foreground">القانوني</h4>
            <ul className="space-y-2">
              <li><Link href="#" className="text-muted-foreground hover:text-primary transition-colors">سياسة الخصوصية</Link></li>
              <li><Link href="#" className="text-muted-foreground hover:text-primary transition-colors">شروط الخدمة</Link></li>
              <li><Link href="#" className="text-muted-foreground hover:text-primary transition-colors">ملفات تعريف الارتباط</Link></li>
              <li><Link href="#" className="text-muted-foreground hover:text-primary transition-colors">الامتثال</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-border pt-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-muted-foreground flex items-center gap-2">
              صُنع بـ <Heart className="h-4 w-4 fill-primary text-primary" /> لك
            </p>
            <p className="text-muted-foreground">
              © 2024 ttrip. جميع الحقوق محفوظة.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
