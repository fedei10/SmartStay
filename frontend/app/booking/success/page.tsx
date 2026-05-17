import Link from 'next/link';
import { CheckCircle2, CreditCard } from 'lucide-react';
import { Suspense } from 'react';
import { connection } from 'next/server';

interface SuccessPageProps {
  searchParams?: Promise<{
    session_id?: string;
  }>;
}

async function BookingSuccessContent({ searchParams }: SuccessPageProps) {
  await connection();
  const resolvedSearchParams = await searchParams;
  const sessionId = resolvedSearchParams?.session_id;

  return (
    <main className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-xl rounded-2xl border border-border bg-card p-6 sm:p-8 shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <CheckCircle2 className="h-7 w-7 text-green-500" />
          <h1 className="text-2xl font-bold text-foreground">Payment successful</h1>
        </div>

        <p className="text-muted-foreground mb-5">
          Your Stripe checkout was completed. Your booking confirmation is being processed.
        </p>

        <div className="rounded-lg border border-border bg-background/60 p-4 mb-6">
          <div className="flex items-center gap-2 text-sm text-foreground/80 mb-1">
            <CreditCard className="h-4 w-4" />
            Session ID
          </div>
          <p className="text-xs break-all text-muted-foreground">
            {sessionId || 'No session ID provided in URL.'}
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <Link
            href="/bookings"
            className="inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2.5 text-primary-foreground font-semibold"
          >
            View my bookings
          </Link>
          <Link
            href={sessionId ? `/chat?payment_success=1&session_id=${encodeURIComponent(sessionId)}` : '/chat'}
            className="inline-flex items-center justify-center rounded-lg border border-border px-4 py-2.5 text-foreground font-semibold"
          >
            Back to chat
          </Link>
        </div>
      </div>
    </main>
  );
}

export default function BookingSuccessPage({ searchParams }: SuccessPageProps) {
  return (
    <Suspense fallback={<main className="min-h-screen bg-background" />}>
      <BookingSuccessContent searchParams={searchParams} />
    </Suspense>
  );
}
