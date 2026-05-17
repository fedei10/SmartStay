'use client';

import { useMemo, useState, type MouseEvent } from 'react';

declare global {
  interface Window {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    LiteAPIPayment?: new (config: any) => { handlePayment: () => void };
  }
}

interface LiteAPIPaymentWidgetProps {
  secretKey: string;
  publicKey: string;
  transactionId: string;
  prebookId: string;
  conversationId?: string;
}

let sdkScriptPromise: Promise<void> | null = null;

function loadLiteAPISdk(): Promise<void> {
  if (typeof window === 'undefined') {
    return Promise.reject(new Error('يمكن تحميل SDK للدفع فقط داخل المتصفح.'));
  }

  if (window.LiteAPIPayment) {
    return Promise.resolve();
  }

  if (!sdkScriptPromise) {
    sdkScriptPromise = new Promise<void>((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://payment-wrapper.liteapi.travel/dist/liteAPIPayment.js?v=a1';
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('تعذر تحميل مكتبة الدفع من LiteAPI.'));
      document.head.appendChild(script);
    });
  }

  return sdkScriptPromise;
}

export function LiteAPIPaymentWidget({
  secretKey,
  publicKey,
  transactionId,
  prebookId,
  conversationId,
}: LiteAPIPaymentWidgetProps) {
  const [isLaunching, setIsLaunching] = useState(false);
  const [launchError, setLaunchError] = useState<string | null>(null);
  const targetElementId = useMemo(
    () => `liteapi-payment-${transactionId.replace(/[^a-zA-Z0-9_-]/g, '')}`,
    [transactionId]
  );

  const handlePayment = async (event?: MouseEvent<HTMLButtonElement>) => {
    event?.preventDefault();
    event?.stopPropagation();
    setIsLaunching(true);
    setLaunchError(null);

    try {
      await loadLiteAPISdk();

      if (!window.LiteAPIPayment) {
        throw new Error('تعذر تهيئة مكتبة الدفع.');
      }

      const returnUrlParams = new URLSearchParams({
        payment_success: '1',
        liteapi: '1',
        transaction_id: transactionId,
        prebook_id: prebookId,
      });
      if (conversationId) {
        returnUrlParams.set('conversation_id', conversationId);
      }
      const returnUrl = `${window.location.origin}/chat?${returnUrlParams.toString()}`;

      const liteAPIConfig: Record<string, unknown> = {
        publicKey,
        appearance: { theme: 'flat' },
        options: {
          business: {
            name: 'ttrip',
          },
          locale: 'ar',
        },
        targetElement: `#${targetElementId}`,
        secretKey,
        returnUrl,
      };

      const liteAPIPayment = new window.LiteAPIPayment(liteAPIConfig);
      liteAPIPayment.handlePayment();
    } catch (error) {
      setLaunchError(error instanceof Error ? error.message : 'تعذر فتح نموذج الدفع.');
    } finally {
      setIsLaunching(false);
    }
  };

  return (
    <div className="mt-4">
      <button
        type="button"
        onClick={handlePayment}
        disabled={isLaunching}
        className="group relative inline-flex w-full items-center justify-center overflow-hidden rounded-2xl border border-primary/30 bg-gradient-to-r from-primary via-primary/90 to-primary/80 px-6 py-4 font-bold text-primary-foreground shadow-lg shadow-primary/20 transition-all hover:scale-[1.01] hover:shadow-xl hover:shadow-primary/30 disabled:cursor-not-allowed disabled:opacity-60"
      >
        <span className="absolute inset-0 bg-white/10 opacity-0 transition-opacity group-hover:opacity-100" />
        <span className="relative flex items-center gap-2 text-sm sm:text-base">
          {isLaunching ? 'جاري فتح نموذج الدفع...' : '💳 ابدأ الدفع الآمن الآن'}
        </span>
      </button>
      <p className="mt-2 text-center text-xs text-foreground/60">دفع آمن عبر LiteAPI</p>
      {launchError && <p className="text-xs text-red-500 mt-2 text-center">{launchError}</p>}
      <div id={targetElementId} className="mt-3 min-h-[12px]" />
    </div>
  );
}
