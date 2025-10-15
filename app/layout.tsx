import Link from 'next/link';
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Top Anime Rankings",
  description: "Ranking top anime episodes and most anticipated series.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-900 text-white`}>
        <header className="bg-gray-800 shadow-md">
          <nav className="container mx-auto px-4 py-4 flex justify-between items-center">
            <Link href="/" className="text-xl font-bold">
              Anime Ranks
            </Link>
            <div className="space-x-4">
              <Link href="/" className="hover:text-yellow-400">
                Top Episodes
              </Link>
              <Link href="/anticipated" className="hover:text-yellow-400">
                Most Anticipated
              </Link>
            </div>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
