'use client';

import Link from 'next/link';
import { useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import { useUser } from '@clerk/nextjs';

const DEFAULT_REDIRECT = '/chat';

export default function CompleteProfilePage() {
  const searchParams = useSearchParams();
  const { isLoaded, isSignedIn } = useUser();

  const redirectUrl = useMemo(() => {
    const requested = searchParams.get('redirect_url');
    if (requested && requested.startsWith('/')) {
      return requested;
    }
    return DEFAULT_REDIRECT;
  }, [searchParams]);

  if (!isLoaded) {
    return <div className="min-h-screen bg-background" />;
  }

  if (!isSignedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background px-4">
        <Link
          href={`/sign-in?redirect_url=${encodeURIComponent(redirectUrl)}`}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
        >
          Sign in to continue
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto w-full max-w-2xl rounded-xl border border-border bg-card p-6">
        <h1 className="text-xl font-semibold text-foreground">Complete profile in chat</h1>
        <p className="mt-3 text-sm text-muted-foreground">
          Phone capture through Clerk can require premium features. ttrip now collects booking details
          directly in chat with guided components for dates, guests, and phone number.
        </p>
        <div className="mt-6">
          <Link
            href={redirectUrl}
            className="inline-flex rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
          >
            Continue to chat
          </Link>
        </div>
      </div>
    </div>
  );
}
