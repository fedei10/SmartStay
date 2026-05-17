'use client';

import Link from 'next/link';

const links = {
  Company: ['About ttrip', 'Careers', 'Blog', 'Press'],
  Support: ['Help center', 'Contact us', 'FAQ', 'System status'],
  Legal: ['Privacy policy', 'Terms of service', 'Cookie policy', 'Compliance'],
};

export function LandingFooter() {
  return (
    <footer className="border-t border-border bg-secondary/20 px-4 sm:px-6 lg:px-8 py-14">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-2.5">
              <div className="relative w-8 h-8 flex items-center justify-center">
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-primary to-teal-600" />
                <svg className="relative h-4 w-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                  <line x1="2" y1="12" x2="22" y2="12" />
                </svg>
              </div>
              <span className="font-bold text-lg text-foreground">ttrip</span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed max-w-[200px]">
              AI-powered travel booking for the modern traveler.
            </p>
          </div>

          {/* Link columns */}
          {Object.entries(links).map(([heading, items]) => (
            <div key={heading} className="space-y-4">
              <h4 className="font-bold text-sm text-foreground">{heading}</h4>
              <ul className="space-y-2.5">
                {items.map((item) => (
                  <li key={item}>
                    <Link
                      href="#"
                      className="text-sm text-muted-foreground hover:text-primary transition-colors"
                    >
                      {item}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t border-border pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">© 2025 ttrip. All rights reserved.</p>
          <p className="text-sm text-muted-foreground">
            Built with ❤️ for travelers worldwide
          </p>
        </div>
      </div>
    </footer>
  );
}
