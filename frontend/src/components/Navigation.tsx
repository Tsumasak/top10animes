'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';

export default function Navigation() {
  const [theme, setTheme] = useState('dark');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme && ['light', 'dark'].includes(savedTheme)) {
      setTheme(savedTheme);
    } else {
      setTheme('dark');
    }
  }, []);

  useEffect(() => {
    // Apply theme to document
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const getThemeIcon = () => {
    return theme === 'dark' ? '☀️' : '🌙';
  };

  const getTooltip = () => {
    return theme === 'dark'
      ? 'Switch to light theme'
      : 'Switch to dark theme';
  };

  // Close mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (isMobileMenuOpen && !target.closest('.mobile-menu-container')) {
        closeMobileMenu();
      }
    };

    if (isMobileMenuOpen) {
      document.addEventListener('click', handleClickOutside);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [isMobileMenuOpen]);

  return (
    <>
      <header className="theme-header">
        <nav className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="text-xl font-bold theme-nav-link">
            Anime Ranks
          </Link>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-4">
            <div className="space-x-4">
              <Link href="/" className="theme-nav-link transition-colors">
                Top Episodes
              </Link>
              <Link href="/anticipated" className="theme-nav-link transition-colors">
                Most Anticipated
              </Link>
            </div>
            <button
              onClick={toggleTheme}
              className="theme-toggle flex items-center justify-center w-10 h-10 text-lg rounded-md"
              title={getTooltip()}
            >
              {getThemeIcon()}
            </button>
          </div>

          {/* Mobile Hamburger Button */}
          <div className="md:hidden mobile-menu-container">
            <button
              onClick={toggleMobileMenu}
              className="theme-toggle flex items-center justify-center w-10 h-10 text-lg rounded-md"
              aria-label="Toggle mobile menu"
            >
              <div className="hamburger-icon">
                <span className={`hamburger-line ${isMobileMenuOpen ? 'open' : ''}`}></span>
                <span className={`hamburger-line ${isMobileMenuOpen ? 'open' : ''}`}></span>
                <span className={`hamburger-line ${isMobileMenuOpen ? 'open' : ''}`}></span>
              </div>
            </button>
          </div>
        </nav>
      </header>

      {/* Mobile Menu Overlay */}
      <div className={`mobile-menu-overlay ${isMobileMenuOpen ? 'open' : ''}`} onClick={closeMobileMenu}></div>

      {/* Mobile Menu */}
      <div className={`mobile-menu ${isMobileMenuOpen ? 'open' : ''} mobile-menu-container`}>
        <div className="mobile-menu-header">
          <h3 className="text-lg font-semibold" style={{color: 'var(--foreground)'}}>Menu</h3>
          <button
            onClick={closeMobileMenu}
            className="close-button"
            aria-label="Close menu"
          >
            ×
          </button>
        </div>
        
        <nav className="mobile-menu-nav">
          <Link 
            href="/" 
            className="mobile-menu-link"
            onClick={closeMobileMenu}
          >
            📺 Top Episodes
          </Link>
          <Link 
            href="/anticipated" 
            className="mobile-menu-link"
            onClick={closeMobileMenu}
          >
            ⭐ Most Anticipated
          </Link>
        </nav>
        
        <div className="mobile-menu-footer">
          <button
            onClick={toggleTheme}
            className="mobile-menu-button theme-toggle"
          >
            {getThemeIcon()}
          </button>
        </div>
      </div>
    </>
  );
}