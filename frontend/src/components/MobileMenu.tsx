'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ThemeToggle } from './ThemeProvider';

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MobileMenu: React.FC<MobileMenuProps> = ({ isOpen, onClose }) => {
  // Close menu on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when menu is open
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div 
        className="mobile-menu-overlay"
        onClick={onClose}
        aria-label="Close menu"
      />

      {/* Menu Panel */}
      <div 
        className="mobile-menu-panel"
        role="menu"
        aria-label="Navigation menu"
      >
        {/* Header with close button */}
        <div className="mobile-menu-header">
          <h2 className="mobile-menu-title">Menu</h2>
          <button 
            onClick={onClose}
            className="mobile-menu-close"
            aria-label="Close menu"
          >
            ✕
          </button>
        </div>

        {/* Menu Items */}
        <nav className="mobile-menu-nav">
          <Link 
            href="/" 
            className="mobile-menu-item"
            onClick={onClose}
            role="menuitem"
          >
            Top Episodes
          </Link>
          <Link 
            href="/anticipated" 
            className="mobile-menu-item"
            onClick={onClose}
            role="menuitem"
          >
            Most Anticipated
          </Link>
          
          {/* Theme Toggle */}
          <div className="mobile-menu-theme">
            <span className="mobile-menu-theme-label">Theme</span>
            <ThemeToggle />
          </div>
        </nav>
      </div>
    </>
  );
};

interface HamburgerButtonProps {
  onClick: () => void;
}

export const HamburgerButton: React.FC<HamburgerButtonProps> = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="hamburger-button"
      aria-label="Open menu"
      aria-expanded="false"
    >
      <span className="hamburger-icon">☰</span>
    </button>
  );
};