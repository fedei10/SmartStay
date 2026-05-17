import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL =
  process.env.BACKEND_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://backend:8001';

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ userId: string }> }
) {
  try {
    const { userId } = await context.params;

    const authHeader =
      request.headers.get('authorization') || request.headers.get('Authorization');

    const searchParams = request.nextUrl.searchParams.toString();
    const suffix = searchParams ? `?${searchParams}` : '';

    const response = await fetch(
      `${BACKEND_URL}/api/v1/bookings/${userId}${suffix}`,
      {
        method: 'GET',
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

    if (!response.ok) {
      console.error('[API] Backend bookings error:', response.status, data);
    }

    if (data === null) {
      return new NextResponse(null, { status: response.status });
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('[API] Bookings proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch bookings' },
      { status: 500 }
    );
  }
}
