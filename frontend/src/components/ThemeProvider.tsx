'use client';

import { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  resolvedTheme: 'light' | 'dark';
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>('dark');
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('dark');

  useEffect(() => {
    // Load theme from localStorage, default to dark if no preference
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme && ['light', 'dark'].includes(savedTheme)) {
      setTheme(savedTheme);
    } else {
      setTheme('dark'); // Default to dark theme
    }
  }, []);

  useEffect(() => {
    const handleThemeChange = () => {
      // Direct theme application - no system detection
      const newResolvedTheme = theme;
      setResolvedTheme(newResolvedTheme);
      
      // Apply theme to document
      const root = document.documentElement;
      root.setAttribute('data-theme', newResolvedTheme);
      
      // Save theme preference
      localStorage.setItem('theme', theme);
    };

    handleThemeChange();
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, resolvedTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const ThemeToggle: React.FC = () => {
  const { theme, setTheme } = useTheme();

  const toggleTheme = () => {
    if (theme === 'light') {
      setTheme('dark');
    } else {
      setTheme('light');
    }
  };

  // Show the icon for the NEXT theme (what will happen on click)
  const getNextThemeIcon = () => {
    return theme === 'dark' ? '☀️' : '🌙';
  };

  const getTooltip = () => {
    return theme === 'dark' 
      ? 'Switch to light theme' 
      : 'Switch to dark theme';
  };

  return (
    <button
      onClick={toggleTheme}
      className="theme-toggle flex items-center justify-center w-10 h-10 text-lg"
      title={getTooltip()}
    >
      {getNextThemeIcon()}
    </button>
  );
};