import { NextRequest } from 'next/server';
import { getCatchAllPath, proxyBackend } from '@/lib/backend';

interface RouteContext {
  params: Promise<{ path?: string[] }>;
}

export async function GET(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return proxyBackend(request, `/api/v1/flights${getCatchAllPath(path)}`, { method: 'GET' });
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return proxyBackend(request, `/api/v1/flights${getCatchAllPath(path)}`, { method: 'POST' });
}
