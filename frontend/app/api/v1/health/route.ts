import { NextRequest } from 'next/server';
import { proxyBackend } from '@/lib/backend';

export async function GET(request: NextRequest) {
  return proxyBackend(request, '/api/v1/health', { method: 'GET' });
}
