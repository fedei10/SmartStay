'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Compass, Menu, X, Moon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';

export function LandingHeader() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { theme, setTheme } = useTheme();

  return (
    <header className="fixed top-0 w-full z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Compass className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="font-bold text-lg text-foreground hidden sm:inline">ttrip</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <Link href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Features
            </Link>
            <Link href="#pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Plans
            </Link>
            <Link href="#testimonials" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Reviews
            </Link>
          </nav>

          {/* Right Side Actions */}
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="h-10 w-10 rounded-lg"
            >
              {theme === 'dark' ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>

            <div className="hidden sm:flex items-center gap-2">
              <Link href="/sign-in?redirect_url=/chat">
                <Button variant="outline" className="rounded-lg px-5 h-10">
                  Sign in
                </Button>
              </Link>
              <Link href="/sign-up?redirect_url=/chat">
                <Button className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg px-5 h-10">
                  Start
                </Button>
              </Link>
            </div>

            <Button
              variant="ghost"
              size="icon"
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden h-10 w-10 rounded-lg"
            >
              {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden border-t border-border py-4 space-y-3">
            <Link href="#features" className="block text-sm text-muted-foreground hover:text-foreground py-2">
              Features
            </Link>
            <Link href="#pricing" className="block text-sm text-muted-foreground hover:text-foreground py-2">
              Plans
            </Link>
            <Link href="#testimonials" className="block text-sm text-muted-foreground hover:text-foreground py-2">
              Reviews
            </Link>
            <Link href="/sign-in?redirect_url=/chat">
              <Button variant="outline" className="w-full rounded-lg">
                Sign in
              </Button>
            </Link>
            <Link href="/sign-up?redirect_url=/chat">
              <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg">
                Start
              </Button>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}
