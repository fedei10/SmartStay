import { Suspense } from 'react';
import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import LiteApiPaymentClient from './payment-liteapi-client';

export const dynamic = 'force-dynamic';

type LiteApiPaymentSearchParams = {
  secret_key?: string;
  transaction_id?: string;
  prebook_id?: string;
  conversation_id?: string;
};

interface LiteApiPaymentPageProps {
  searchParams?: Promise<LiteApiPaymentSearchParams>;
}

function buildRedirectUrl(params?: LiteApiPaymentSearchParams): string {
  const query = new URLSearchParams();
  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value) query.set(key, value);
  });
  const queryString = query.toString();
  return queryString ? `/payment/liteapi?${queryString}` : '/payment/liteapi';
}

export default async function LiteApiPaymentPage({ searchParams }: LiteApiPaymentPageProps) {
  const resolvedSearchParams = await searchParams;
  const { userId } = await auth();

  if (!userId) {
    const redirectUrl = buildRedirectUrl(resolvedSearchParams);
    redirect(`/sign-in?redirect_url=${encodeURIComponent(redirectUrl)}`);
  }

  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <LiteApiPaymentClient />
    </Suspense>
  );
}
