'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ThemeToggle } from './ThemeProvider';
import { MobileMenu, HamburgerButton } from './MobileMenu';

interface ClientLayoutProps {
  children: React.ReactNode;
}

export const ClientLayout: React.FC<ClientLayoutProps> = ({ children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const openMobileMenu = () => setIsMobileMenuOpen(true);
  const closeMobileMenu = () => setIsMobileMenuOpen(false);

  return (
    <>
      <header className="theme-header border-b fixed top-0 left-0 right-0 z-50">
        <nav className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-xl font-bold">
            Anime Ranks
          </Link>
          
          {/* Desktop Navigation */}
          <div className="desktop-nav flex items-center gap-6">
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

          {/* Mobile Hamburger Button */}
          <HamburgerButton onClick={openMobileMenu} />
        </nav>
      </header>

      {/* Mobile Menu */}
      <MobileMenu 
        isOpen={isMobileMenuOpen} 
        onClose={closeMobileMenu} 
      />

      <main className="pt-20">{children}</main>
    </>
  );
};