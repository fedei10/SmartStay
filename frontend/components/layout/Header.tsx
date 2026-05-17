'use client';

import { Moon, Sun, Menu, X, MessageSquare, BookOpen } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useState, useEffect } from 'react';
import { UserButton, SignedIn, SignedOut } from '@clerk/nextjs';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';

const navLinks = [
  { href: '/chat', label: 'Chat', icon: MessageSquare },
  { href: '/bookings', label: 'Bookings', icon: BookOpen },
];

export function Header() {
  const { theme, setTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/70 bg-background/85 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between gap-4">

          {/* Logo */}
          <Link href="/chat" className="flex items-center gap-2.5 flex-shrink-0 group">
            <div className="relative w-7 h-7 flex items-center justify-center">
              <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-primary to-teal-600 shadow-sm group-hover:shadow-primary/30 transition-all duration-300" />
              <svg className="relative h-3.5 w-3.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                <line x1="2" y1="12" x2="22" y2="12" />
              </svg>
            </div>
            <span className="font-bold text-base text-foreground tracking-tight hidden sm:inline">ttrip</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden sm:flex items-center gap-1 flex-1">
            {navLinks.map(({ href, label, icon: Icon }) => {
              const active = pathname === href || pathname.startsWith(href + '/');
              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                    active
                      ? 'bg-primary/10 text-primary'
                      : 'text-muted-foreground hover:text-foreground hover:bg-secondary/60'
                  }`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  {label}
                </Link>
              );
            })}
          </nav>

          {/* Right actions */}
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="h-8 w-8 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary/60"
            >
              {!mounted ? (
                <div className="h-4 w-4" />
              ) : theme === 'dark' ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>

            <SignedOut>
              <Link href="/sign-in" className="hidden sm:flex">
                <Button size="sm" className="rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 h-8 px-4 text-xs font-semibold">
                  Sign in
                </Button>
              </Link>
            </SignedOut>

            <SignedIn>
              <UserButton />
            </SignedIn>

            <Button
              variant="ghost"
              size="icon"
              onClick={() => setMenuOpen(!menuOpen)}
              className="sm:hidden h-8 w-8 rounded-lg"
            >
              {menuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </Button>
          </div>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="border-t border-border py-3 sm:hidden space-y-1 animate-fade-in">
            {navLinks.map(({ href, label, icon: Icon }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setMenuOpen(false)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    active ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:text-foreground hover:bg-secondary/60'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </Link>
              );
            })}
            <SignedOut>
              <Link href="/sign-in" onClick={() => setMenuOpen(false)}>
                <Button className="w-full mt-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 h-9 text-sm">
                  Sign in
                </Button>
              </Link>
            </SignedOut>
          </div>
        )}
      </div>
    </header>
  );
}
