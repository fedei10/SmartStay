import { NextRequest, NextResponse } from 'next/server';
import { BACKEND_URL } from '@/lib/backend';

interface BackendEnvelope<T> {
  code?: number;
  message?: string;
  data?: T;
}

interface BackendChatData {
  conversation_id?: string;
  message?: string;
  intent?: string;
  agent?: string;
  next_action?: string;
  metadata?: {
    hotels?: unknown[];
    flights?: unknown[];
    payment_url?: unknown;
    payment_sdk_secret_key?: unknown;
    payment_sdk_public_key?: unknown;
    payment_transaction_id?: unknown;
    payment_prebook_id?: unknown;
    booking_status?: unknown;
    state?: unknown;
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

function asString(value: unknown): string | undefined {
  return typeof value === 'string' ? value : undefined;
}

function normalizeChatResponse(payload: BackendEnvelope<BackendChatData>) {
  const data = payload.data || {};
  const metadata = data.metadata || {};

  return {
    conversation_id: data.conversation_id,
    response: data.message || asString(payload.message) || '',
    intent: data.intent,
    agent: data.agent,
    next_action: data.next_action,

    hotels: Array.isArray(metadata.hotels) ? metadata.hotels : [],
    flights: Array.isArray(metadata.flights) ? metadata.flights : [],

    payment_url: asString(metadata.payment_url),
    payment_sdk_secret_key: asString(metadata.payment_sdk_secret_key),
    payment_sdk_public_key: asString(metadata.payment_sdk_public_key),
    payment_transaction_id: asString(metadata.payment_transaction_id),
    payment_prebook_id: asString(metadata.payment_prebook_id),
    booking_status: asString(metadata.booking_status),
    state: metadata.state,

    metadata,
  };
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const authHeader =
      request.headers.get('authorization') ||
      request.headers.get('Authorization');

    const response = await fetch(`${BACKEND_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader ? { Authorization: authHeader } : {}),
      },
      body: JSON.stringify({
        conversation_id: body.conversation_id || 'default',
        message: body.message,
        payment_completed: body.payment_completed ?? false,
        payment_transaction_id: body.payment_transaction_id,
        payment_prebook_id: body.payment_prebook_id,
      }),
    });

    const contentType = response.headers.get('content-type') || '';
    let data: unknown = null;

    if (contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = text ? { message: text } : null;
    }

    if (!response.ok) {
      console.error('[API] Backend error:', response.status, data);
      return NextResponse.json(
        { error: 'Backend chat request failed', detail: data },
        { status: response.status }
      );
    }

    if (data === null) {
      return new NextResponse(null, { status: response.status });
    }

    return NextResponse.json(
      normalizeChatResponse(data as BackendEnvelope<BackendChatData>),
      { status: response.status }
    );
  } catch (error) {
    console.error('[API] Chat proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}
