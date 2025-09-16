import React, { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface VideoPagerItem {
  id: string;
  title: string;
  description: string;
  videoSrc: string;
  posterSrc: string;
  prompt?: string;
  reference?: string;
  synthesis?: string;
}

interface VideoPagerProps {
  title: string;
  items: VideoPagerItem[];
  className?: string;
  subtitle?: React.ReactNode;
}

export const VideoPager: React.FC<VideoPagerProps> = ({ title, items, className, subtitle }) => {
  if (items.length === 0) {
    return (
      <section className={cn('w-full', className)} aria-label={`${title} video pager`}>
        <div className="flex items-center justify-between mb-4">
          <h3>{title}</h3>
          <div className="text-sm text-muted-foreground">0 / 0</div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6 text-sm text-muted-foreground">
          No videos available yet.
        </div>
      </section>
    );
  }

  const [index, setIndex] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);

  const item = items[index];

  const goPrev = () => setIndex((i) => (i - 1 + items.length) % items.length);
  const goNext = () => setIndex((i) => (i + 1) % items.length);

  return (
    <section className={cn('w-full', className)} aria-label={`${title} video pager`}>
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-foreground">{title}</h3>
          {subtitle ? (
            <div className="mt-2 text-sm text-muted-foreground leading-relaxed">{subtitle}</div>
          ) : null}
        </div>
        <div className="text-sm text-muted-foreground whitespace-nowrap">
          {index + 1} / {items.length}
        </div>
      </div>

      <div className="relative">
        <Button
          variant="outline"
          size="sm"
          className="absolute left-0 top-1/2 z-10 h-10 w-10 -translate-y-1/2 border-border/70 bg-card text-primary shadow-sm hover:bg-card"
          onClick={goPrev}
          aria-label="Previous video"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>

        <Button
          variant="outline"
          size="sm"
          className="absolute right-0 top-1/2 z-10 h-10 w-10 -translate-y-1/2 border-border/70 bg-card text-primary shadow-sm hover:bg-card"
          onClick={goNext}
          aria-label="Next video"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>

        <div className="px-12">
          <div className="rounded-2xl border border-border/70 bg-card/90 p-6 shadow">
            <div>
              <video
                key={item.id}
                ref={videoRef}
                controls
                preload="metadata"
                playsInline
                muted
                className="w-full max-h-[70vh] rounded"
                aria-label={`Video`}
                src={item.videoSrc}
                onLoadedData={() => {
                  const video = videoRef.current;
                  if (!video) return;
                  try {
                    if (video.currentTime > 0.001) {
                      video.currentTime = 0;
                    }
                    const playback = video.play();
                    if (playback && typeof playback.then === 'function') {
                      playback
                        .then(() => {
                          try { video.pause(); } catch {}
                        })
                        .catch(() => {
                          try { video.pause(); } catch {}
                        });
                    } else {
                      try { video.pause(); } catch {}
                    }
                  } catch {}
                }}
              >
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
