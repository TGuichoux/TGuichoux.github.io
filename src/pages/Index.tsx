import React from 'react';
import { Header } from '@/components/Header';
import { VideoPager } from '@/components/VideoPager';

const Index = () => {
  const BASE = import.meta.env.BASE_URL || '/';

  const cloneFiles = [
    'media/cloning/clone_kieks_0_3_3-seg-20001-0535.mov',
    'media/cloning/clone_scott_0_2_2-seg-10001-0467.mov',
    'media/cloning/clone_scott_0_4_4-seg-00001-0535.mov'
  ];

  const sotaFiles = [
    'media/sota/comparison_kieks_0_1_1-seg-20001-0435.mp4',
    'media/sota/comparison_scott_0_5_5-seg-30001-0240.mp4',
    'media/sota/comparison_wayne_0_2_2-seg-20001-0462.mp4',
    'media/sota/comparison_wayne_0_3_3-seg-20001-0435.mp4'
  ];

  const failureFiles = [
    'media/failures/FAILURE_10001-0330.mp4',
    'media/failures/Gelina_1_wayne_0_3_3-seg-3.mov'
  ];

  // Speech+Gesture demos
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
      .map((relativePath) => {
        const filename = relativePath.split('/').pop() ?? 'sample';
        const baseId = filename.replace(/\.[^.]+$/, '');
        return {
          id: baseId,
          title: filename,
          description: '',
          videoSrc: `${BASE}${relativePath}`,
          posterSrc: '/placeholder.svg'
        };
      });

  const multimodalCloningItems = createItemsFromPaths(cloneFiles);
  const comparisonItems = createItemsFromPaths(sotaFiles);
  const failureItems = createItemsFromPaths(failureFiles);

  return (
    <div className="min-h-screen bg-background">
      <Header currentPath="/" />

      <main className="container mx-auto max-w-6xl px-6 py-12">
        {/* Hero Section */}
        <section className="mb-16">
          <div className="rounded-3xl border border-border/60 bg-card/95 px-6 py-12 shadow-lg sm:px-10">
            <div className="mx-auto max-w-5xl">
              <div className="space-y-5 text-center md:text-left">
                <span className="inline-flex items-center justify-center gap-2 rounded-full bg-primary/10 px-4 py-1 text-xs font-semibold uppercase tracking-wide text-primary">
                  ICASSP 2026 · Demo Preview
                </span>
                <h1 className="text-balance text-3xl font-semibold leading-tight tracking-tight text-foreground sm:text-4xl md:text-5xl">
                  GELINA: unifies speech and gesture synthesis for robust multimodal communication
                </h1>
                <p className="text-sm text-muted-foreground/90 md:text-base">
                  Anonymous Authors · Code will be available soon
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Abstract Section */}
        <section className="mb-16">
          <div className="mx-auto max-w-4xl rounded-3xl border border-border/70 bg-card/95 p-10 shadow">
            <h2 className="mb-4 text-center text-foreground">Abstract</h2>
            <p className="text-foreground/90 text-lg leading-relaxed">
              Human communication is multimodal, with speech and gestures tightly coupled, yet most computational methods
              generate them sequentially, weakening synchrony and prosody alignment. We introduce Gelina, a unified framework
              that jointly synthesizes speech and co-speech gestures from text using interleaved token sequences in a discrete
              autoregressive backbone, with modality-specific decoders. Gelina supports multi-speaker and multi-style cloning,
              and enables gesture-only synthesis from speech inputs. Large-scale subjective and objective evaluations demonstrate
              competitive speech quality and improved gesture generation over unimodal baselines.
            </p>
          </div>
        </section>

        {/* Demos Section */}
        <section id="demos" className="mb-16">
          <div className="mx-auto mb-8 max-w-3xl text-center">
            <h2 className="mb-2 text-foreground">Demos</h2>
            <p className="text-base text-muted-foreground md:text-lg">
              Navigate through the carousels to inspect the different operating modes. Keyboard arrows or the on-screen
              controls let you step through each sample.
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
                <p className="text-base text-muted-foreground md:text-lg">
                  Gelina operates in speech-to-gesture mode for these runs: we condition on reference speech and synthesise
                  only the gestural modality to compare against other approaches.
                </p>
              }
            />
            <VideoPager
              title="Failure Cases"
              items={failureItems}
              className="rounded-2xl border border-destructive/40 bg-destructive/5 p-4 shadow-sm"
              subtitle={
                <div className="space-y-2 text-base text-muted-foreground/90 md:text-lg">
                  <p>
                    We noticed several failures when generating speech and gestures. Some cases show incorrect rotations.
                    Since the same issue appears in EMAGE, it may come from a bug in the shared rotation conversion code.
                  </p>
                  <p>
                    In random voice generation (without a prompt), some voices have poor quality — they may sound robotic
                    or sometimes only partly understandable.
                  </p>
                </div>
              }
            />
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-background/80">
        <div className="container mx-auto max-w-6xl px-6 py-8">
          <div className="flex flex-col gap-3 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
            <span>© 2026 GELINA demo. No cookies. No tracking.</span>
            <a href="#" className="transition-colors hover:text-primary">
              Back to top
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
