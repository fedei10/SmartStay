import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL =
  process.env.BACKEND_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://backend:8001';

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ bookingReference: string }> }
) {
  try {
    const { bookingReference } = await context.params;
    const authHeader =
      request.headers.get('authorization') || request.headers.get('Authorization');

    let reason: string | undefined;
    try {
      const body = await request.json();
      if (body && typeof body.reason === 'string') {
        reason = body.reason.trim();
      }
    } catch {
      reason = undefined;
    }

    const params = new URLSearchParams(request.nextUrl.searchParams.toString());
    if (reason && !params.has('reason')) {
      params.set('reason', reason);
    }

    const suffix = params.toString() ? `?${params.toString()}` : '';
    const response = await fetch(
      `${BACKEND_URL}/api/v1/bookings/${encodeURIComponent(bookingReference)}/cancel${suffix}`,
      {
        method: 'POST',
        headers: {
          ...(authHeader && { Authorization: authHeader }),
        },
      }
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
    console.error('[API] Booking cancel proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to cancel booking' },
      { status: 500 }
    );
  }
}
