import { SignIn } from '@clerk/nextjs'
import { Metadata } from 'next'
import { Suspense } from 'react'
import { connection } from 'next/server'

export const dynamic = 'force-dynamic'

export const metadata: Metadata = {
  title: 'تسجيل الدخول - ttrip',
  description: 'سجّل الدخول إلى حساب ttrip',
}

interface SignInPageProps {
  searchParams?: Promise<{
    redirect_url?: string;
  }>;
}

async function SignInContent({ searchParams }: SignInPageProps) {
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
            أهلاً بعودتك إلى <span className="text-primary">ttrip</span>
          </h1>
          <p className="text-muted-foreground">سجّل الدخول لإدارة حجوزاتك الفندقية</p>
        </div>
        <SignIn forceRedirectUrl={postAuthRedirect} fallbackRedirectUrl={postAuthRedirect} />
      </div>
    </div>
  )
}

export default function SignInPage({ searchParams }: SignInPageProps) {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">جاري التحميل...</div>}>
      <SignInContent searchParams={searchParams} />
    </Suspense>
  )
}
