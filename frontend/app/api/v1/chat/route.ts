import { NextRequest, NextResponse } from 'next/server';
import { BACKEND_URL } from '@/lib/backend';

interface BackendEnvelope<T> {
  code: number;
  message: string;
  data?: T;
}

interface BackendChatData {
  conversation_id?: string;
  message?: string;
  metadata?: {
    hotels?: unknown[];
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

function normalizeChatResponse(payload: BackendEnvelope<BackendChatData>) {
  const data = payload.data || {};
  const metadata = data.metadata || {};

  return {
    conversation_id: data.conversation_id,
    response: data.message || payload.message,
    intent: data.intent,
    agent: data.agent,
    next_action: data.next_action,
    hotels: Array.isArray(metadata.hotels) ? metadata.hotels : [],
    payment_url: metadata.payment_url,
    payment_sdk_secret_key: metadata.payment_sdk_secret_key,
    payment_sdk_public_key: metadata.payment_sdk_public_key,
    payment_transaction_id: metadata.payment_transaction_id,
    payment_prebook_id: metadata.payment_prebook_id,
    booking_status: metadata.booking_status,
    state: metadata.state,
    metadata,
  };
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const authHeader =
      request.headers.get('authorization') || request.headers.get('Authorization');

    const response = await fetch(`${BACKEND_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader && { Authorization: authHeader }),
      },
      body: JSON.stringify({
        conversation_id: body.conversation_id || 'default',
        message: body.message,
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
    }

    if (data === null) {
      return new NextResponse(null, { status: response.status });
    }

    return NextResponse.json(normalizeChatResponse(data as BackendEnvelope<BackendChatData>), {
      status: response.status,
    });
  } catch (error) {
    console.error('[API] Chat proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}
