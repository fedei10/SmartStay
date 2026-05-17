import { Suspense } from 'react';
import { auth } from '@clerk/nextjs/server';
import { unauthorized } from 'next/navigation';
import PaymentClient from './payment-client';

export const dynamic = 'force-dynamic';

async function PaymentPageContent() {
  const { userId } = await auth();

  if (!userId) {
    unauthorized();
  }

  return <PaymentClient />;
}

export default function PaymentPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <PaymentPageContent />
    </Suspense>
  );
}
