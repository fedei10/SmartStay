'use server'

import { getStripe } from '@/lib/stripe'
import { getProductPrice } from '@/lib/data'
import { auth } from '@clerk/nextjs/server'
import { headers } from 'next/headers'

export async function createCheckoutSession(productId: string) {
  const { userId } = await auth()

  if (!userId) {
    throw new Error('User not authenticated')
  }

  // Validate product and get price server-side
  const price = await getProductPrice(productId)
  if (!price) {
    throw new Error('Product not found')
  }

  const hdrs = await headers()
  const requestOrigin = hdrs.get('origin')
  const forwardedHost = hdrs.get('x-forwarded-host')
  const host = forwardedHost ?? hdrs.get('host')
  const proto = hdrs.get('x-forwarded-proto') ?? 'http'
  const baseUrl =
    requestOrigin ??
    (host ? `${proto}://${host}` : process.env.NEXT_PUBLIC_APP_URL)

  if (!baseUrl) {
    throw new Error('Missing app base URL for Stripe redirects')
  }

  const session = await getStripe().checkout.sessions.create({
    mode: 'payment',
    payment_method_types: ['card'],
    line_items: [
      {
        price_data: {
          currency: 'usd',
          product_data: {
            name: productId,
            description: `Travel planning through ttrip - ${productId}`,
          },
          unit_amount: price,
        },
        quantity: 1,
      },
    ],
    success_url: `${baseUrl}/payment/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${baseUrl}/payment/cancel`,
    customer_email: undefined, // Clerk will provide this
    metadata: {
      userId,
      productId,
    },
  })

  return { sessionId: session.id }
}
