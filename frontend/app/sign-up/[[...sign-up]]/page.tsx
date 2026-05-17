import { SignUp } from '@clerk/nextjs'
import { Metadata } from 'next'
import { Suspense } from 'react'
import { connection } from 'next/server'

export const dynamic = 'force-dynamic'

export const metadata: Metadata = {
  title: 'إنشاء حساب - ttrip',
  description: 'أنشئ حسابك في ttrip',
}

interface SignUpPageProps {
  searchParams?: Promise<{
    redirect_url?: string;
  }>;
}

async function SignUpContent({ searchParams }: SignUpPageProps) {
  await connection() // Explicitly mark as dynamic for Next.js 16 cacheComponents
  const resolvedSearchParams = await searchParams
  const requestedRedirect = resolvedSearchParams?.redirect_url
  const redirectUrl =
    typeof requestedRedirect === 'string' && requestedRedirect.startsWith('/')
      ? requestedRedirect
      : '/chat'
  const postAuthRedirect = redirectUrl

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            انضم إلى <span className="text-primary">ttrip</span>
          </h1>
          <p className="text-muted-foreground">أنشئ حسابًا لحجز أفضل الفنادق بسهولة</p>
        </div>
        <SignUp forceRedirectUrl={postAuthRedirect} fallbackRedirectUrl={postAuthRedirect} />
      </div>
    </div>
  )
}

export default function SignUpPage({ searchParams }: SignUpPageProps) {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">جاري التحميل...</div>}>
      <SignUpContent searchParams={searchParams} />
    </Suspense>
  )
}
