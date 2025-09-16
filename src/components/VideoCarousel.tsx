import React, { useState, useRef, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface VideoItem {
  id: string;
  title: string;
  description: string;
  videoSrc: string;
  posterSrc: string;
  prompt?: string;
  reference?: string;
  synthesis?: string;
}

interface VideoCarouselProps {
  title: string;
  items: VideoItem[];
  className?: string;
  showComparison?: boolean;
  onLayoutToggle?: () => void;
  comparisonLayout?: 'stacked' | 'side-by-side';
}

export const VideoCarousel: React.FC<VideoCarouselProps> = ({
  title,
  items,
  className,
  showComparison = false,
  onLayoutToggle,
  comparisonLayout = 'stacked'
}) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const checkScrollButtons = () => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  useEffect(() => {
    checkScrollButtons();
    const container = scrollContainerRef.current;
    if (container) {
      container.addEventListener('scroll', checkScrollButtons);
      return () => container.removeEventListener('scroll', checkScrollButtons);
    }
  }, [items]);

  const scrollLeft = () => {
    if (scrollContainerRef.current) {
      const itemWidth = 320; // Approximate item width
      scrollContainerRef.current.scrollBy({ left: -itemWidth, behavior: 'smooth' });
      setCurrentIndex(Math.max(0, currentIndex - 1));
    }
  };

  const scrollRight = () => {
    if (scrollContainerRef.current) {
      const itemWidth = 320;
      scrollContainerRef.current.scrollBy({ left: itemWidth, behavior: 'smooth' });
      setCurrentIndex(Math.min(items.length - 1, currentIndex + 1));
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'ArrowLeft' && canScrollLeft) {
      scrollLeft();
    } else if (event.key === 'ArrowRight' && canScrollRight) {
      scrollRight();
    }
  };

  return (
    <section className={cn("w-full", className)} aria-label={`${title} video carousel`}>
      <div className="flex items-center justify-between mb-6">
        <h3>{title}</h3>
        {showComparison && onLayoutToggle && (
          <Button
            variant="outline"
            size="sm"
            onClick={onLayoutToggle}
            className="text-sm"
          >
            {comparisonLayout === 'stacked' ? 'Side by side' : 'Stacked view'}
          </Button>
        )}
      </div>

      <div className="relative">
        {/* Navigation buttons */}
        <Button
          variant="outline"
          size="sm"
          className={cn(
            "absolute left-0 top-1/2 -translate-y-1/2 z-10 h-10 w-10 p-0 shadow-md",
            !canScrollLeft && "opacity-50 cursor-not-allowed"
          )}
          onClick={scrollLeft}
          disabled={!canScrollLeft}
          aria-label="Previous videos"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>

        <Button
          variant="outline"
          size="sm"
          className={cn(
            "absolute right-0 top-1/2 -translate-y-1/2 z-10 h-10 w-10 p-0 shadow-md",
            !canScrollRight && "opacity-50 cursor-not-allowed"
          )}
          onClick={scrollRight}
          disabled={!canScrollRight}
          aria-label="Next videos"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>

        {/* Carousel container */}
        <div
          ref={scrollContainerRef}
          className="flex gap-6 overflow-x-auto scrollbar-hide pb-4 px-8"
          style={{ scrollSnapType: 'x mandatory' }}
          onKeyDown={handleKeyDown}
          tabIndex={0}
          role="region"
          aria-label={`${title} carousel`}
          aria-live="polite"
        >
          {items.map((item, index) => (
            <div
              key={item.id}
              className="flex-none w-80"
              style={{ scrollSnapAlign: 'start' }}
            >
              <div className="bg-card border border-border rounded-lg p-4 h-full">
                <h4 className="font-medium mb-2 text-foreground">{item.title}</h4>
                
                {item.prompt && (
                  <p className="text-sm text-muted-foreground mb-3 italic">
                    "{item.prompt}"
                  </p>
                )}

                <div className="mb-3">
                  <video
                    controls
                    preload="metadata"
                    playsInline
                    poster={item.posterSrc}
                    className="w-full rounded"
                    aria-label={`Video: ${item.title}`}
                  >
                    {item.videoSrc.toLowerCase().endsWith('.mov') && (
                      <source
                        src={item.videoSrc.replace(/\.mov$/i, '.mp4')}
                        type="video/mp4"
                      />
                    )}
                    {/* Primary source */}
                    <source src={item.videoSrc} />
                    Your browser does not support the video tag.
                  </video>
                </div>

                <p className="text-sm text-muted-foreground mb-2">
                  {item.description}
                </p>

                {item.reference && (
                  <p className="text-xs text-muted-foreground">
                    <strong>Reference:</strong> {item.reference}
                  </p>
                )}
                
                {item.synthesis && (
                  <p className="text-xs text-muted-foreground">
                    <strong>Synthesis:</strong> {item.synthesis}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Screen reader announcements */}
      <div className="sr-only" aria-live="polite">
        Showing item {currentIndex + 1} of {items.length}
      </div>
    </section>
  );
};
