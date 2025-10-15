import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
