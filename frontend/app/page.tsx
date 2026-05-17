import { Suspense } from 'react';
import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { connection } from 'next/server';
import { LandingHeader } from '@/components/landing/LandingHeader';
import { Hero } from '@/components/landing/Hero';
import { Features } from '@/components/landing/Features';
import { Pricing } from '@/components/landing/Pricing';
import { Testimonials } from '@/components/landing/Testimonials';
import { CTA } from '@/components/landing/CTA';
import { LandingFooter } from '@/components/landing/LandingFooter';

export const dynamic = 'force-dynamic';

interface LandingPageProps {
  searchParams?: Promise<{
    payment_success?: string;
    session_id?: string;
    conversation_id?: string;
  }>;
}

function LandingPageContent() {
  return (
    <div className="w-full bg-background">
      <LandingHeader />
      <Hero />
      <div id="features">
        <Features />
      </div>
      <div id="pricing">
        <Pricing />
      </div>
      <div id="testimonials">
        <Testimonials />
      </div>
      <CTA />
      <LandingFooter />
    </div>
  );
}

async function PublicHomeGate({ searchParams }: LandingPageProps) {
  await connection();
  const resolvedSearchParams = await searchParams;
  const paymentSuccess = resolvedSearchParams?.payment_success;
  const sessionId = resolvedSearchParams?.session_id;
  const conversationId = resolvedSearchParams?.conversation_id;

  if (paymentSuccess === '1' && sessionId) {
    const params = new URLSearchParams({
      payment_success: '1',
      session_id: sessionId,
    });
    if (conversationId) {
      params.set('conversation_id', conversationId);
    }
    redirect(`/chat?${params.toString()}`);
  }

  const { userId } = await auth();

  if (userId) {
    redirect('/chat');
  }

  return <LandingPageContent />;
}

export default function Page({ searchParams }: LandingPageProps) {
  return (
    <Suspense fallback={<main className="min-h-screen bg-background" />}>
      <PublicHomeGate searchParams={searchParams} />
    </Suspense>
  );
}
