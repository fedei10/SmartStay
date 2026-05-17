import { NextRequest, NextResponse } from 'next/server';

export const BACKEND_URL =
  process.env.BACKEND_INTERNAL_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8001';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export async function proxyBackend(
  request: NextRequest,
  path: string,
  options: {
    method?: HttpMethod;
    body?: unknown;
    searchParams?: URLSearchParams;
  } = {}
) {
  const authHeader =
    request.headers.get('authorization') || request.headers.get('Authorization');
  const method = options.method || (request.method as HttpMethod);
  const search = options.searchParams?.toString() || request.nextUrl.searchParams.toString();
  const suffix = search ? `?${search}` : '';

  const response = await fetch(`${BACKEND_URL}${path}${suffix}`, {
    method,
    headers: {
      ...(method !== 'GET' && { 'Content-Type': 'application/json' }),
      ...(authHeader && { Authorization: authHeader }),
    },
    body: method === 'GET' ? undefined : JSON.stringify(options.body ?? (await request.json().catch(() => undefined))),
  });

  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    console.error('[ttrip API] Backend error:', response.status, data);
  }

  if (data === '' || data === null) {
    return new NextResponse(null, { status: response.status });
  }

  return NextResponse.json(data, { status: response.status });
}

export function getCatchAllPath(parts: string[] | undefined) {
  return parts && parts.length > 0 ? `/${parts.map(encodeURIComponent).join('/')}` : '';
}
