import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Configure turbopack to use frontend directory as root to avoid lockfile conflicts
  turbopack: {
    root: __dirname, // Use current directory (frontend) as root
  },
  // Image configuration for MyAnimeList CDN
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.myanimelist.net',
        port: '',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
