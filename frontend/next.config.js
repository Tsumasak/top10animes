/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // For static HTML export
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || '',
  assetPrefix: process.env.NEXT_PUBLIC_BASE_PATH || '',
  reactStrictMode: true,
  images: {
    unoptimized: true, // For static export with external images
  },
};
module.exports = nextConfig;
