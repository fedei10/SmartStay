import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL =
  process.env.BACKEND_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://backend:8001';

interface RouteContext {
  params: Promise<{ sessionId: string }>;
}

export async function GET(request: NextRequest, context: RouteContext) {
  try {
    const { sessionId } = await context.params;

    const authHeader =
      request.headers.get('authorization') || request.headers.get('Authorization');

    const response = await fetch(
      `${BACKEND_URL}/api/v1/payments/verify-session/${encodeURIComponent(sessionId)}`,
      {
        method: 'GET',
        headers: {
          ...(authHeader && { Authorization: authHeader }),
        },
      },
    );

    const contentType = response.headers.get('content-type') || '';
    let data: unknown = null;

    if (contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = text ? { message: text } : null;
    }

    if (data === null) {
      return new NextResponse(null, { status: response.status });
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('[API] Payment verify proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to verify payment session' },
      { status: 500 }
    );
  }
}
