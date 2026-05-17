import Link from 'next/link';
import { AlertCircle, Home, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';

export default function PaymentCancelPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 via-background to-background flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Cancel Card */}
        <div className="rounded-2xl border border-border bg-card p-8 sm:p-12 shadow-lg">
          {/* Header with Icon */}
          <div className="flex flex-col items-center text-center mb-8">
            <div className="mb-6 relative">
              <div className="absolute inset-0 bg-orange-500/20 rounded-full blur-xl" />
              <AlertCircle className="h-16 w-16 text-orange-500 relative" />
            </div>
            
            <h1 className="text-4xl sm:text-5xl font-bold text-foreground mb-2">
              Payment Cancelled
            </h1>
            <p className="text-muted-foreground text-lg">
              Your payment process was cancelled. No charges have been made to your account.
            </p>
          </div>

          <Separator className="my-8" />

          {/* Details Section */}
          <div className="space-y-6 mb-8">
            {/* Status Badge */}
            <div className="flex justify-center">
              <Badge className="bg-orange-500/10 text-orange-700 border-orange-500/30 px-4 py-2 text-sm font-semibold">
                ⚠ Transaction Cancelled
              </Badge>
            </div>

            {/* What you can do */}
            <div className="space-y-4">
              <h3 className="font-semibold text-foreground">What happens now?</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-3">
                  <span className="text-orange-500 font-bold mt-0.5">✓</span>
                  <span>No charges have been applied to your account</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-orange-500 font-bold mt-0.5">✓</span>
                  <span>Your booking details have not been saved</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-orange-500 font-bold mt-0.5">✓</span>
                  <span>You can try again anytime</span>
                </li>
              </ul>
            </div>

            {/* Retry Info */}
            <div className="rounded-lg border border-border/50 bg-muted/30 p-6">
              <p className="text-sm text-foreground/90">
                If you encountered any issues during checkout, please try again or contact our support team for assistance.
              </p>
            </div>
          </div>

          <Separator className="my-8" />

          {/* Action Buttons */}
          <div className="grid sm:grid-cols-2 gap-4">
            <Link href="/chat">
              <Button className="w-full h-11 text-base font-semibold bg-primary hover:bg-primary/90 flex items-center justify-center gap-2">
                <Home className="h-5 w-5" />
                Back to Chat
              </Button>
            </Link>
            <Link href="/payment">
              <Button 
                variant="outline" 
                className="w-full h-11 text-base font-semibold flex items-center justify-center gap-2"
              >
                <RotateCcw className="h-5 w-5" />
                Try Again
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
