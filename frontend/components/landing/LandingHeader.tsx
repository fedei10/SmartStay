'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Moon, Sun, Menu, X } from 'lucide-react';
import { useTheme } from 'next-themes';

export function LandingHeader() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 w-full z-50 transition-all duration-500 ${
        scrolled
          ? 'border-b border-border/60 bg-background/90 backdrop-blur-2xl shadow-sm'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="relative w-8 h-8 flex items-center justify-center">
              <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-primary to-teal-600 shadow-md group-hover:shadow-primary/40 transition-all duration-300" />
              <svg className="relative h-4 w-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                <line x1="2" y1="12" x2="22" y2="12" />
              </svg>
            </div>
            <span className="font-bold text-lg text-foreground tracking-tight hidden sm:inline">ttrip</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            {[
              { href: '#features', label: 'Features' },
              { href: '#pricing', label: 'Pricing' },
              { href: '#testimonials', label: 'Reviews' },
            ].map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="relative px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors duration-200 rounded-lg hover:bg-secondary/60 group"
              >
                {item.label}
                <span className="absolute bottom-1 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-primary rounded-full group-hover:w-4 transition-all duration-300" />
              </Link>
            ))}
          </nav>

          {/* Right actions */}
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="h-9 w-9 rounded-xl text-muted-foreground hover:text-foreground hover:bg-secondary/60"
            >
              {!mounted ? <div className="h-4 w-4" /> : theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>

            <div className="hidden sm:flex items-center gap-2">
              <Link href="/sign-in?redirect_url=/chat">
                <Button variant="ghost" className="rounded-xl px-4 h-9 text-sm font-medium hover:bg-secondary/60">
                  Sign in
                </Button>
              </Link>
              <Link href="/sign-up?redirect_url=/chat">
                <Button className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-xl px-5 h-9 text-sm font-semibold shadow-md hover:shadow-primary/30 hover:shadow-lg transition-all duration-300">
                  Get started
                </Button>
              </Link>
            </div>

            <Button
              variant="ghost"
              size="icon"
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden h-9 w-9 rounded-xl"
            >
              {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden border-t border-border/50 py-4 space-y-1 animate-fade-in">
            {['#features', '#pricing', '#testimonials'].map((href) => (
              <Link
                key={href}
                href={href}
                onClick={() => setMenuOpen(false)}
                className="block text-sm text-muted-foreground hover:text-foreground px-3 py-2 rounded-lg hover:bg-secondary/60 transition-colors"
              >
                {href.replace('#', '').charAt(0).toUpperCase() + href.replace('#', '').slice(1)}
              </Link>
            ))}
            <div className="pt-2 grid grid-cols-2 gap-2">
              <Link href="/sign-in?redirect_url=/chat">
                <Button variant="outline" className="w-full rounded-xl h-10">Sign in</Button>
              </Link>
              <Link href="/sign-up?redirect_url=/chat">
                <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded-xl h-10">Get started</Button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
