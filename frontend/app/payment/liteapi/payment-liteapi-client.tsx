'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';

interface LiteAPIPaymentConfig {
  publicKey: 'sandbox' | 'live';
  secretKey: string;
  returnUrl: string;
  targetElement: string;
  appearance?: { theme?: 'flat' | string };
  options?: { business?: { name?: string } };
}

const LITEAPI_PAYMENT_SCRIPT =
  'https://payment-wrapper.liteapi.travel/dist/liteAPIPayment.js?v=a1';

type PaymentStatus = 'idle' | 'loading' | 'ready' | 'error';

function loadLiteApiPaymentScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(
      `script[src="${LITEAPI_PAYMENT_SCRIPT}"]`,
    );

    if (existing) {
      if (window.LiteAPIPayment) {
        resolve();
        return;
      }
      existing.addEventListener('load', () => resolve(), { once: true });
      existing.addEventListener(
        'error',
        () => reject(new Error('Failed to load LiteAPI payment SDK.')),
        { once: true },
      );
      return;
    }

    const script = document.createElement('script');
    script.src = LITEAPI_PAYMENT_SCRIPT;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load LiteAPI payment SDK.'));
    document.body.appendChild(script);
  });
}

export default function LiteApiPaymentClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initializedRef = useRef(false);

  const [status, setStatus] = useState<PaymentStatus>('idle');
  const [error, setError] = useState<string | null>(null);

  const secretKey = searchParams.get('secret_key');
  const transactionId = searchParams.get('transaction_id');
  const prebookId = searchParams.get('prebook_id');
  const conversationId = searchParams.get('conversation_id');

  const publicKey = useMemo<'sandbox' | 'live'>(() => {
    return process.env.NEXT_PUBLIC_LITEAPI_PAYMENT_ENV === 'live' ? 'live' : 'sandbox';
  }, []);

  const returnUrl = useMemo(() => {
    if (typeof window === 'undefined') return '';

    const url = new URL('/chat', window.location.origin);
    url.searchParams.set('payment_success', '1');
    url.searchParams.set('liteapi', '1');
    if (transactionId) url.searchParams.set('transaction_id', transactionId);
    if (prebookId) url.searchParams.set('prebook_id', prebookId);
    if (conversationId) url.searchParams.set('conversation_id', conversationId);

    return url.toString();
  }, [transactionId, prebookId, conversationId]);

  useEffect(() => {
    if (initializedRef.current) return;

    if (!secretKey || !transactionId || !prebookId) {
      setStatus('error');
      setError(
        'Missing LiteAPI payment data. Please return to the chat and restart checkout.',
      );
      return;
    }

    void (async () => {
      try {
        initializedRef.current = true;
        setStatus('loading');
        setError(null);

        await loadLiteApiPaymentScript();

        if (!window.LiteAPIPayment) {
          throw new Error('LiteAPI payment SDK is not available.');
        }

        const config: LiteAPIPaymentConfig = {
          publicKey,
          secretKey,
          returnUrl,
          targetElement: '#liteapi-payment-target',
          appearance: { theme: 'flat' },
          options: { business: { name: 'SmartStay' } },
        };
        // window.LiteAPIPayment is declared globally via LiteAPIPaymentWidget.tsx
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const payment = new (window.LiteAPIPayment as any)(config);

        setStatus('ready');
        payment.handlePayment();
      } catch (err) {
        console.error('[LiteAPI Payment] SDK initialization failed:', err);
        setStatus('error');
        setError(
          err instanceof Error ? err.message : 'Failed to initialize LiteAPI payment.',
        );
      }
    })();
  }, [prebookId, publicKey, returnUrl, secretKey, transactionId]);

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-2xl flex-col justify-center px-4 py-10">
      <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-foreground">Complete your payment</h1>

        <p className="mt-2 text-sm text-muted-foreground">
          Secure payment is handled by LiteAPI. After payment, you will return to the chat to
          finalize your booking.
        </p>

        {publicKey === 'sandbox' && (
          <div className="mt-4 rounded-lg border border-border bg-background p-4 text-sm text-muted-foreground">
            Sandbox test card:{' '}
            <span className="font-semibold text-foreground">4242 4242 4242 4242</span>, any
            3-digit CVV, and any future expiration date.
          </div>
        )}

        {status === 'loading' && (
          <div className="mt-6 flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading secure payment form...
          </div>
        )}

        {status === 'error' && (
          <div className="mt-6 rounded-lg border border-destructive/40 bg-destructive/10 p-4">
            <p className="text-sm text-destructive">
              {error || 'Payment could not be initialized.'}
            </p>
            <button
              type="button"
              onClick={() => router.push('/chat')}
              className="mt-4 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
            >
              Back to chat
            </button>
          </div>
        )}

        <div id="liteapi-payment-target" className="mt-6" />
      </div>
    </div>
  );
}
