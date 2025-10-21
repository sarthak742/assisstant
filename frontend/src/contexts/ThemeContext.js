import React, { createContext, useContext, useState, useEffect } from 'react';

const themes = {
  blueCyan: {
    name: 'Blue-Cyan',
    primary: '#00D4FF',
    secondary: '#0099CC',
    accent: '#66E5FF',
    glow: '#00D4FF',
    background: '#0A0F1C',
    backgroundSecondary: '#0F1419',
    text: '#FFFFFF',
    textSecondary: '#B0C4DE',
    glass: 'rgba(0, 212, 255, 0.1)',
    glassHover: 'rgba(0, 212, 255, 0.2)',
    border: 'rgba(0, 212, 255, 0.3)',
    shadow: '0 8px 32px rgba(0, 212, 255, 0.3)',
    gradient: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 153, 204, 0.05) 100%)',
    orbGradient: 'radial-gradient(circle, #00D4FF 0%, #0099CC 50%, #003D52 100%)',
    particleColor: '#00D4FF'
  },
  violetPink: {
    name: 'Violet-Pink',
    primary: '#9D4EDD',
    secondary: '#C77DFF',
    accent: '#E0AAFF',
    glow: '#9D4EDD',
    background: '#0A0F1C',
    backgroundSecondary: '#0F1419',
    text: '#FFFFFF',
    textSecondary: '#D8BFD8',
    glass: 'rgba(157, 78, 221, 0.1)',
    glassHover: 'rgba(157, 78, 221, 0.2)',
    border: 'rgba(157, 78, 221, 0.3)',
    shadow: '0 8px 32px rgba(157, 78, 221, 0.3)',
    gradient: 'linear-gradient(135deg, rgba(157, 78, 221, 0.1) 0%, rgba(199, 125, 255, 0.05) 100%)',
    orbGradient: 'radial-gradient(circle, #9D4EDD 0%, #C77DFF 50%, #4A1A5C 100%)',
    particleColor: '#9D4EDD'
  },
  amberGold: {
    name: 'Amber-Gold',
    primary: '#FFB000',
    secondary: '#FF8C00',
    accent: '#FFD700',
    glow: '#FFB000',
    background: '#0A0F1C',
    backgroundSecondary: '#0F1419',
    text: '#FFFFFF',
    textSecondary: '#F5DEB3',
    glass: 'rgba(255, 176, 0, 0.1)',
    glassHover: 'rgba(255, 176, 0, 0.2)',
    border: 'rgba(255, 176, 0, 0.3)',
    shadow: '0 8px 32px rgba(255, 176, 0, 0.3)',
    gradient: 'linear-gradient(135deg, rgba(255, 176, 0, 0.1) 0%, rgba(255, 140, 0, 0.05) 100%)',
    orbGradient: 'radial-gradient(circle, #FFB000 0%, #FF8C00 50%, #B8860B 100%)',
    particleColor: '#FFB000'
  }
};

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState('blueCyan');
  const [isTransitioning, setIsTransitioning] = useState(false);

  const changeTheme = (themeName) => {
    if (themeName !== currentTheme && themes[themeName]) {
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentTheme(themeName);
        setTimeout(() => setIsTransitioning(false), 300);
      }, 150);
    }
  };

  const theme = themes[currentTheme];

  // Apply theme changes with smooth transitions
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Add transition class before changing theme
    document.body.classList.add('theme-transition');
    
    // Update CSS variables
    const root = document.documentElement;
    Object.entries(theme).forEach(([key, value]) => {
      if (typeof value === 'string') {
        root.style.setProperty(`--theme-${key}`, value);
      }
    });
    
    // Apply color-transition class to key elements
    document.querySelectorAll('.jarvis-panel, .glass-container, button, input').forEach(el => {
      el.classList.add('color-transition');
    });
    
    // Remove transition class after changes are complete
    const transitionTimeout = setTimeout(() => {
      document.body.classList.remove('theme-transition');
    }, 500);
    
    return () => clearTimeout(transitionTimeout);
  }, [theme, currentTheme]);

  const value = {
    theme,
    currentTheme,
    changeTheme,
    isTransitioning,
    themes: Object.keys(themes)
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};