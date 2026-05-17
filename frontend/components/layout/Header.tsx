'use client';

import { Compass, Moon, Sun, Menu, X } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useState, useEffect } from 'react';
import { UserButton, SignedIn, SignedOut } from '@clerk/nextjs';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export function Header() {
  const { theme, setTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
              <Compass className="h-4 w-4 text-primary-foreground" />
            </div>
            <div className="text-2xl font-bold text-foreground tracking-tight">ttrip</div>
            <span className="hidden sm:inline text-xs text-muted-foreground font-medium tracking-wide uppercase">travel workspace</span>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="rounded-lg hover:bg-secondary transition-colors"
            >
              {!mounted ? (
                <div className="h-5 w-5" />
              ) : theme === 'dark' ? (
                <Sun className="h-5 w-5 text-primary" />
              ) : (
                <Moon className="h-5 w-5 text-primary" />
              )}
            </Button>

            <SignedOut>
              <Link href="/sign-in" className="hidden sm:flex">
                <Button variant="default" className="rounded-lg bg-primary text-primary-foreground hover:bg-primary/90">
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
              className="sm:hidden hover:bg-secondary"
            >
              {menuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>

        {menuOpen && (
          <div className="border-t border-border py-4 sm:hidden space-y-2">
            <SignedIn>
              <div className="px-3 py-2 text-sm text-muted-foreground">Plan and book from chat.</div>
            </SignedIn>
            <SignedOut>
              <Link href="/sign-in">
                <Button variant="default" className="w-full rounded-lg bg-primary text-primary-foreground hover:bg-primary/90">
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
