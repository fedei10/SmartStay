import Link from 'next/link';
import { CheckCircle2, CreditCard, ArrowRight, Home, Ticket } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Suspense } from 'react';
import { connection } from 'next/server';

interface SuccessPageProps {
  searchParams?: Promise<{
    session_id?: string;
  }>;
}

async function PaymentSuccessContent({ searchParams }: SuccessPageProps) {
  await connection();
  const resolvedSearchParams = await searchParams;
  const sessionId = resolvedSearchParams?.session_id;

  return (
    <main className="min-h-screen bg-gradient-to-br from-green-50 via-background to-background flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Success Card */}
        <div className="rounded-2xl border border-border bg-card p-8 sm:p-12 shadow-lg">
          {/* Header with Icon */}
          <div className="flex flex-col items-center text-center mb-8">
            <div className="mb-6 relative">
              <div className="absolute inset-0 bg-green-500/20 rounded-full blur-xl" />
              <CheckCircle2 className="h-16 w-16 text-green-500 relative" />
            </div>
            
            <h1 className="text-4xl sm:text-5xl font-bold text-foreground mb-2">
              Payment Successful!
            </h1>
            <p className="text-muted-foreground text-lg">
              Your booking has been confirmed and payment processed
            </p>
          </div>

          <Separator className="my-8" />

          {/* Details Section */}
          <div className="space-y-6 mb-8">
            {/* Status Badge */}
            <div className="flex justify-center">
              <Badge className="bg-green-500/10 text-green-700 border-green-500/30 px-4 py-2 text-sm font-semibold">
                ✓ Transaction Complete
              </Badge>
            </div>

            {/* Session ID */}
            <div className="rounded-lg border border-border/50 bg-muted/30 p-6">
              <div className="flex items-center gap-3 mb-3">
                <CreditCard className="h-5 w-5 text-primary" />
                <h3 className="font-semibold text-foreground">Transaction ID</h3>
              </div>
              <p className="text-sm break-all text-muted-foreground font-mono bg-background/50 p-3 rounded-md">
                {sessionId || 'No session ID provided'}
              </p>
            </div>

            {/* What happens next */}
            <div className="space-y-3">
              <h3 className="font-semibold text-foreground flex items-center gap-2">
                <span className="text-primarytext-xl">📧</span>
                What happens next?
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-3">
                  <span className="text-green-500 font-bold mt-0.5">1</span>
                  <span>A confirmation email has been sent to your registered email address</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-500 font-bold mt-0.5">2</span>
                  <span>Your booking details are being finalized</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-500 font-bold mt-0.5">3</span>
                  <span>You'll receive further instructions via email within 24 hours</span>
                </li>
              </ul>
            </div>
          </div>

          <Separator className="my-8" />

          {/* Action Buttons */}
          <div className="grid sm:grid-cols-2 gap-4">
            <Link href="/bookings">
              <Button className="w-full h-11 text-base font-semibold bg-primary hover:bg-primary/90 flex items-center justify-center gap-2">
                <Ticket className="h-5 w-5" />
                View my Bookings
              </Button>
            </Link>
            <Link href={sessionId ? `/chat?payment_success=1&session_id=${encodeURIComponent(sessionId)}` : '/chat'}>
              <Button 
                variant="outline" 
                className="w-full h-11 text-base font-semibold flex items-center justify-center gap-2"
              >
                <Home className="h-5 w-5" />
                Back to Chat
              </Button>
            </Link>
          </div>

          {/* Additional Info */}
          <div className="mt-8 pt-8 border-t border-border/50">
            <p className="text-xs text-muted-foreground text-center">
              Need help?{' '}
              <a 
                href="mailto:support@stayai.com" 
                className="text-primary hover:underline font-semibold"
              >
                Contact our support team
              </a>
            </p>
          </div>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center">
          <p className="text-sm text-muted-foreground">
            🔒 Secure payment processed by Stripe
          </p>
        </div>
      </div>
    </main>
  );
}

export default function PaymentSuccessPage({ searchParams }: SuccessPageProps) {
  return (
    <Suspense fallback={<main className="min-h-screen bg-background" />}>
      <PaymentSuccessContent searchParams={searchParams} />
    </Suspense>
  );
}
