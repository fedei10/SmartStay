import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Keep auth/search-param driven pages stable in production.
  // Cache Components + Clerk dynamic APIs can throw DYNAMIC_SERVER_USAGE.
  cacheComponents: false,
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    const backendUrl = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
    return [
      {
        source: '/api/v1/:path*',
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ]
  },
};

export default nextConfig;
