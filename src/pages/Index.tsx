import React from 'react';
import { Header } from '@/components/Header';
import { VideoPager } from '@/components/VideoPager';

const Index = () => {
  const BASE = import.meta.env.BASE_URL || '/';

  const clonePaths = Object.keys(
    import.meta.glob('/public/media/cloning/clone*.mov', { eager: true })
  );

  const sotaPaths = Object.keys(
    import.meta.glob('/public/media/sota/*.{mp4,mov}', { eager: true })
  );

  const failurePaths = Object.keys(
    import.meta.glob('/public/media/failures/*.{mp4,mov}', { eager: true })
  );

  const multimodalCloningItems = clonePaths
    .sort((pathA, pathB) => pathA.localeCompare(pathB))
    .map((fullPath) => {
      const relativePath = fullPath.replace(/^\/public\//, '');
      const normalizedPath = relativePath.startsWith('/') ? relativePath.slice(1) : relativePath;
      const filename = normalizedPath.split('/').pop() ?? 'clone';
      const baseId = filename.replace(/\.[^.]+$/, '');
      return {
        id: baseId,
        title: filename,
        description: '',
        videoSrc: `${BASE}${normalizedPath}`,
        posterSrc: '/placeholder.svg'
      };
    });

  // Demo data - easily replaceable
  // Speech+Gesture section: display videos from tts_gesture folder
  const textToSpeechGestureItems = [
    {
      id: 'ttsg-01',
      title: 'gelina_female',
      description: '',
      videoSrc: `${BASE}media/tts_gesture/gelina_female_random0001-0470.mp4`,
      posterSrc: '/placeholder.svg'
    },
    {
      id: 'ttsg-02',
      title: 'duck_female',
      description: '',
      videoSrc: `${BASE}media/tts_gesture/duck_female_random0001-0580.mp4`,
      posterSrc: '/placeholder.svg'
    },
    {
      id: 'ttsg-03',
      title: 'kings_cfm',
      description: '',
      videoSrc: `${BASE}media/tts_gesture/kings_cfm_cloning0001-0467.mp4`,
      posterSrc: '/placeholder.svg'
    }
  ];

  const createItemsFromPaths = (paths: string[]) =>
    paths
      .sort((a, b) => a.localeCompare(b))
      .map((fullPath) => {
        const relativePath = fullPath.replace(/^\/public\//, '');
        const normalizedPath = relativePath.startsWith('/') ? relativePath.slice(1) : relativePath;
        const filename = normalizedPath.split('/').pop() ?? 'sample';
        const baseId = filename.replace(/\.[^.]+$/, '');
        return {
          id: baseId,
          title: filename,
          description: '',
          videoSrc: `${BASE}${normalizedPath}`,
          posterSrc: '/placeholder.svg'
        };
      });

  const comparisonItems = createItemsFromPaths(sotaPaths);
  const failureItems = createItemsFromPaths(failurePaths);

  return (
    <div className="min-h-screen bg-background">
      <Header currentPath="/" />
      
      <main className="container max-w-6xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <section className="mb-16">
          <div className="rounded-2xl border border-border bg-card/95 px-6 py-12 shadow-md sm:px-10">
            <div className="mx-auto flex max-w-4xl flex-col items-center text-center gap-4">
              <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1 text-xs font-medium uppercase tracking-wide text-primary">
                ICASSP 2026 Demo Preview
              </span>
              <h1 className="mb-2 max-w-3xl text-foreground text-2xl sm:text-3xl md:text-4xl font-semibold">
                GELINA: Unified Speech and Gesture Synthesis via Interleaved Token Prediction
              </h1>
              <p className="text-muted-foreground text-base md:text-lg">
                Anonymous Authors
              </p>
              <p className="text-sm md:text-base text-muted-foreground/80">
                Code will be available soon.
              </p>
            </div>
          </div>
        </section>

        {/* Abstract Section */}
        <section className="mb-16">
          <div className="mx-auto max-w-4xl rounded-2xl border border-border bg-card/95 p-10 shadow-sm">
            <h2 className="mb-4 text-center text-foreground text-xl md:text-2xl font-semibold">Abstract</h2>
            <p className="text-foreground/85 leading-relaxed text-lg md:text-xl">
              Human communication is multimodal, with speech and gestures tightly coupled, yet most computational methods generate them sequentially, weakening synchrony and prosody alignment. We introduce Gelina, a unified framework that jointly synthesizes speech and co-speech gestures from text using interleaved token sequences in a discrete autoregressive backbone, with modality-specific decoders. Gelina supports multi-speaker and multi-style cloning, and enables gesture-only synthesis from speech inputs. Large-scale subjective and objective evaluations demonstrate competitive speech quality and improved gesture generation over unimodal baselines.
            </p>
          </div>
        </section>

        {/* Demos Section */}
        <section id="demos" className="mb-16">
          <div className="mx-auto mb-8 max-w-3xl text-center">
            <h2 className="mb-2 text-foreground text-xl md:text-2xl font-semibold">Demos</h2>
            <p className="text-muted-foreground text-base md:text-lg">
            </p>
          </div>

          <div className="space-y-16">
            <VideoPager
              title="Text to Speech + Gesture"
              items={textToSpeechGestureItems}
              className="rounded-2xl border border-border bg-card/95 p-4 shadow-sm"
            />
            <VideoPager
              title="Multimodal Cloning"
              items={multimodalCloningItems}
              className="rounded-2xl border border-border bg-card/95 p-4 shadow-sm"
            />
            <VideoPager
              title="Comparison to State of the Art"
              items={comparisonItems}
              className="rounded-2xl border border-border bg-card/95 p-6 shadow-sm"
              subtitle={
                <p className="text-base md:text-lg text-muted-foreground">
                  Gelina operates in speech-to-gesture mode for these runs: we condition on reference speech
                  and synthesise only the gestural modality to compare against other approaches.
                </p>
              }
            />
            <VideoPager
              title="Failure Cases"
              items={failureItems}
              className="rounded-2xl border border-destructive/40 bg-destructive/5 p-4 shadow-sm"
              subtitle={
                <div className="space-y-2 text-base md:text-lg text-muted-foreground/90">
                  <p>
                    We noticed several failures when generating speech and gestures. Some cases show incorrect rotations. Since the same issue appears in EMAGE, it may come from a bug in the shared rotation conversion code.
                  </p>
                  <p>
                    In random voice generation (without a prompt), some voices have poor quality — they may sound robotic or sometimes only partly understandable.
                  </p>
                </div>
              }
            />
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-background/80">
        <div className="container max-w-6xl mx-auto px-6 py-8">
          <div className="flex flex-col gap-3 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
            <span>© 2026 GELINA demo. No cookies. No tracking.</span>
            <a href="#" className="hover:text-primary transition-colors">
              Back to top
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
