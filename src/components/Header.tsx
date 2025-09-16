import React from 'react';
import { Link } from 'react-router-dom';

interface HeaderProps {
  currentPath?: string;
}

export const Header: React.FC<HeaderProps> = ({ currentPath }) => {
  return (
    <header className="w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container max-w-5xl mx-auto flex h-16 items-center justify-between px-6">
        {/* Site title */}
        <Link 
          to="/" 
          className="text-xl font-semibold text-foreground hover:no-underline focus:no-underline"
          aria-label="GELINA homepage"
        >
          GELINA
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-6">
          {currentPath !== '/' ? (
            <Link
              to="/#demos"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Demos
            </Link>
          ) : (
            <a
              href="#demos"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Demos
            </a>
          )}
        </nav>
      </div>
    </header>
  );
};
