/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // For static HTML export
  reactStrictMode: true,
  images: {
    unoptimized: true, // For static export with external images
  },
};
module.exports = nextConfig;
