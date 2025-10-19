import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Navigation from "../components/Navigation";
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
    <html lang="en" suppressHydrationWarning>
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
        <Navigation />
        <main>
          {children}
        </main>
      </body>
    </html>
  );
}
