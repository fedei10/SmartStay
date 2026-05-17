import { Suspense } from 'react';
import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { connection } from 'next/server';
import HomeClient from '../home-client';

export const dynamic = 'force-dynamic';

type ChatSearchParams = {
  payment_success?: string;
  session_id?: string;
  liteapi?: string;
  transaction_id?: string;
  prebook_id?: string;
  conversation_id?: string;
};

interface ChatPageProps {
  searchParams?: Promise<ChatSearchParams>;
}

function buildChatRedirectUrl(params?: ChatSearchParams): string {
  const query = new URLSearchParams();
  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value) query.set(key, value);
  });
  const queryString = query.toString();
  return queryString ? `/chat?${queryString}` : '/chat';
}

async function ChatPageContent({ searchParams }: ChatPageProps) {
  await connection();
  const resolvedSearchParams = await searchParams;
  const { userId } = await auth();

  if (!userId) {
    const redirectUrl = buildChatRedirectUrl(resolvedSearchParams);
    redirect(`/sign-in?redirect_url=${encodeURIComponent(redirectUrl)}`);
  }

  return (
    <HomeClient
      paymentSuccess={resolvedSearchParams?.payment_success === '1'}
      sessionId={resolvedSearchParams?.session_id}
      liteapi={resolvedSearchParams?.liteapi}
      transactionId={resolvedSearchParams?.transaction_id}
      prebookId={resolvedSearchParams?.prebook_id}
      conversationId={resolvedSearchParams?.conversation_id}
    />
  );
}

export default function ChatPage({ searchParams }: ChatPageProps) {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <ChatPageContent searchParams={searchParams} />
    </Suspense>
  );
}
