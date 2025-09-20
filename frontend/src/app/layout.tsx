import './globals.css';
import type { Metadata } from 'next';
import ClientLayout from '@/components/ClientLayout';

export const metadata: Metadata = {
  title: 'Top 50 Anime Episodes of the Week',
  description: 'Top 50 Anime Episodes of the Week',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en-US">
      <body>
        {children}
      </body>
    </html>
  );
}