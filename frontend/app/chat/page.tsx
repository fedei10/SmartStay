import { Suspense } from 'react';
import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { connection } from 'next/server';
import HomeClient from '../home-client';

export const dynamic = 'force-dynamic';

interface ChatPageProps {
  searchParams?: Promise<{
    payment_success?: string;
    session_id?: string;
    liteapi?: string;
    transaction_id?: string;
    prebook_id?: string;
    conversation_id?: string;
  }>;
}

async function ChatPageContent({ searchParams }: ChatPageProps) {
  await connection();
  const resolvedSearchParams = await searchParams;
  const paymentSuccess = resolvedSearchParams?.payment_success;
  const sessionId = resolvedSearchParams?.session_id;
  const liteapi = resolvedSearchParams?.liteapi;
  const transactionId = resolvedSearchParams?.transaction_id;
  const prebookId = resolvedSearchParams?.prebook_id;
  const conversationId = resolvedSearchParams?.conversation_id;
  const { userId } = await auth();

  if (!userId) {
    let chatRedirectUrl = '/chat';
    if (paymentSuccess === '1') {
      const params = new URLSearchParams({ payment_success: '1' });
      if (sessionId) params.set('session_id', sessionId);
      if (liteapi) params.set('liteapi', liteapi);
      if (transactionId) params.set('transaction_id', transactionId);
      if (prebookId) params.set('prebook_id', prebookId);
      if (conversationId) params.set('conversation_id', conversationId);
      chatRedirectUrl = `/chat?${params.toString()}`;
    }
    redirect(`/sign-in?redirect_url=${encodeURIComponent(chatRedirectUrl)}`);
  }

  return <HomeClient />;
}

export default function HomePage({ searchParams }: ChatPageProps) {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <ChatPageContent searchParams={searchParams} />
    </Suspense>
  );
}
