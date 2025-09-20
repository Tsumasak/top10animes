"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

interface ClientLayoutProps {
  children: React.ReactNode;
  periodInfo: string;
  headerTitle?: string;
}

const ClientLayout: React.FC<ClientLayoutProps> = ({ children, periodInfo, headerTitle = "TOP 50 ANIME EPISODES" }) => {
  const [isSideMenuOpen, setIsSideMenuOpen] = useState(false);
  const [showScrollToTop, setShowScrollToTop] = useState(false);
  const [scrollPosition, setScrollPosition] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      // Scroll-to-Top Button logic
      if (window.pageYOffset > 300) {
        setShowScrollToTop(true);
      } else {
        setShowScrollToTop(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    if (isSideMenuOpen) {
      document.body.classList.add('side-menu-open');
    } else {
      document.body.classList.remove('side-menu-open');
      window.scrollTo(0, scrollPosition); // Restore scroll position when menu closes
    }
  }, [isSideMenuOpen, scrollPosition]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const sideMenu = document.getElementById('side-menu');
      const navigationMenu = document.getElementById('navigation-menu');
      
      if (isSideMenuOpen && 
          sideMenu && 
          !sideMenu.contains(event.target as Node) && 
          navigationMenu && 
          !navigationMenu.contains(event.target as Node)) {
        setIsSideMenuOpen(false);
      }
    };

    if (isSideMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isSideMenuOpen]);

  const toggleSideMenu = () => {
    if (!isSideMenuOpen) {
      setScrollPosition(window.scrollY); // Save scroll position when menu opens
    }
    setIsSideMenuOpen(!isSideMenuOpen);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <>
      {/* Side Menu */}
      <div id="side-menu" className={`side-nav ${isSideMenuOpen ? 'open' : ''}`}>
        <button className="btn-close" id="btn-close-menu" onClick={toggleSideMenu}>&times;</button>
        <Link href="/">Weekly Episodes Rank</Link>
        <Link href="/anticipated">Most Anticipated</Link>
      </div>

      {/* Header */}
      <header className="header">
        <div className="logo">
          <img src="/assets/logo_transparent.png" alt="Top 10 Anime Logo" />
        </div>
        <div className="header-content">
          <h1 className="header-title">{headerTitle} <span className="header-subtitle">OF THE WEEK</span></h1>
          <p className="header-date">{periodInfo}</p>
        </div>
        <div id="navigation-menu" onClick={toggleSideMenu}>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </header>

      {/* Main Navigation - Hidden on all screens, replaced by hamburger */}
      {/* <nav className="main-nav" style={{ transform: isScrolled ? 'translateY(-100%)' : 'translateY(0)' }}>
        <Link href="/" className="active">Weekly Episodes Rank</Link>
        <Link href="/anticipated">Most Anticipated</Link>
      </nav> */}

      {/* Main Content */}
      <main className="main">
        {children}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p className="footer-text">Average score from 0 to 5 obtained from:</p>
        <div className="footer-logo">
          <img src="/assets/MAL_logo.png" alt="MyAnimeList Logo" style={{ width: '200px', height: 'auto' }} />
        </div>
      </footer>

      {/* Fixed buttons */}
      <div className="fixed-buttons">
        <a href="#" id="scrollToTop" className={`scroll-to-top ${showScrollToTop ? 'visible' : ''}`} onClick={scrollToTop}>
          ↑
        </a>
        <a href="https://www.instagram.com/top10_animes" target="_blank" rel="noopener noreferrer" className="instagram-button">
          <img src="https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/instagram-white-icon.png" alt="Instagram" style={{ width: '30px', height: '30px' }} />
        </a>
      </div>
    </>
  );
};

export default ClientLayout;