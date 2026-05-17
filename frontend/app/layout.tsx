import type { Metadata, Viewport } from 'next'
import { ThemeProvider } from 'next-themes'
import { ClerkProvider } from '@clerk/nextjs'
import { Suspense } from 'react'
import { Toaster } from '@/components/ui/toaster'

import './globals.css'

export const metadata: Metadata = {
  title: 'ttrip - AI travel planner',
  description: 'Plan trips, compare stays, and coordinate travel with an AI booking assistant.',
  generator: 'v0.app',
  openGraph: {
    title: 'ttrip - AI travel planner',
    description: 'Plan trips, compare stays, and coordinate travel with an AI booking assistant.',
    locale: 'en_US',
  },
}

export const viewport: Viewport = {
  themeColor: '#1aa39a',
  userScalable: true,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <Suspense fallback={<div className="min-h-screen bg-background" />}>
            <ClerkProvider>
              {children}
              <Toaster />
            </ClerkProvider>
          </Suspense>
        </ThemeProvider>
      </body>
    </html>
  )
}
