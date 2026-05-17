import { Suspense } from 'react';
import { auth } from '@clerk/nextjs/server';
import { unauthorized } from 'next/navigation';
import BookingsClient from './bookings-client';

export const dynamic = 'force-dynamic';

async function BookingsPageContent() {
  const { userId } = await auth();

  if (!userId) {
    unauthorized();
  }

  return <BookingsClient />;
}

export default function BookingsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <BookingsPageContent />
    </Suspense>
  );
}
