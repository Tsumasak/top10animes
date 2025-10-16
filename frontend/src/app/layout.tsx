import Link from 'next/link';
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider, ThemeToggle } from "@/components/ThemeProvider";

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
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var theme = localStorage.getItem('theme');
                  if (theme && ['light', 'dark'].includes(theme)) {
                    document.documentElement.setAttribute('data-theme', theme);
                  } else {
                    document.documentElement.setAttribute('data-theme', 'dark');
                  }
                } catch (e) {
                  document.documentElement.setAttribute('data-theme', 'dark');
                }
              })();
            `,
          }}
        />
      </head>
      <body className={inter.className}>
        <ThemeProvider>
          <header className="theme-header border-b">
            <nav className="container mx-auto px-4 py-4 flex justify-between items-center">
              <Link href="/" className="text-xl font-bold">
                Anime Ranks
              </Link>
              <div className="flex items-center gap-6">
                <div className="space-x-4">
                  <Link href="/" className="theme-nav-link">
                    Top Episodes
                  </Link>
                  <Link href="/anticipated" className="theme-nav-link">
                    Most Anticipated
                  </Link>
                </div>
                <ThemeToggle />
              </div>
            </nav>
          </header>
          <main>{children}</main>
        </ThemeProvider>
      </body>
    </html>
  );
}
