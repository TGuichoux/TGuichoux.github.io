---
title: 'Gelina: Unified Speech and Gesture Synthesis via Interleaved Token Prediction'
uid: p01
order: 1
authors:
- 'Téo Guichoux'
- 'Théodor Lemerle'
- 'Shivam Mehta'
- 'Gustav Eje Henter'
- 'Jonas Beskow'
- 'Laure Soulier'
- 'Catherine Pelachaud'
- 'Nicolas Obin'
venue: 'ICASSP'
year: '2026'
description: 'In this paper, we introduce Gelina, a discrete autoregressive model for the joint synthesis of speech and gestures. This webpage provides the supplementary materials, videos and others associated with the paper.'
doi: '10.1109/ICASSP55912.2026.11464562'
pdf: 'https://arxiv.org/pdf/2510.12834'
code: 'https://github.com/TGuichoux/Gelina/tree/main'
download: ''
math: true
bibtex: |
  @INPROCEEDINGS{guichoux2026gelina,
  author={Guichoux, Téo and Lemerle, Théodor and Mehta, Shivam and Beskow, Jonas and Henter, Gustav Eje and Soulier, Laure and Pelachaud, Catherine and Obin, Nicolas},
  booktitle={ICASSP 2026 - 2026 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)}, 
  title={Gelina: Unified Speech and Gesture Synthesis Via Interleaved Token Prediction}, 
  year={2026},
  volume={},
  number={},
  pages={16122-16126},
  keywords={Radio broadcasting;Frequency modulation;Contacts;Codecs;Modulation;Radio broadcasting;Frequency modulation;Radio access networks;Regional area networks;Protocols;Text-to-speech (TTS);co-speech gesture generation;unified multimodal synthesis;autoregressive transformers;flow-matching;Human behavior synthesis},
  doi={10.1109/ICASSP55912.2026.11464562}}
---

<div class="toc" markdown="1">
**On this page**

* Contents
{:toc}
</div>

## Abstract

Human communication is multimodal, with speech and gestures tightly coupled, yet most computational methods for generating speech and gestures synthesize them sequentially, weakening synchrony and prosody alignment. We introduce Gelina, a unified framework that jointly synthesizes speech and co-speech gestures from text using interleaved token sequences in a discrete autoregressive backbone, with modality-specific decoders. Gelina supports multi-speaker and multi-style cloning and enables gesture-only synthesis from speech inputs. Subjective and objective evaluations demonstrate competitive speech quality and improved gesture generation over unimodal baselines.

{% include figure.html src="/assets/images/gelina_ar.png" id="Figure 1" label="fig-p01-1" caption="Overview of the Gelina architecture." %}

## Results of the user study


{% include figure.html
   src="/assets/images/gelina_mos.png"
   id="Figure 4.5"
   label="fig-ch04-4_5"
   caption="Mean Opinion Scores with 95\% confidence intervals from user evaluation across three aspects: Voice human-likeness, speech-gesture synchrony, and Gesture human-likeness."
   layout="wide"
%}

## Illustrative examples


### Speech-gesture generation capabilities

These videos illustrate the capabilities of Gelina for speech and gesture generation from a textual input.

{% include video-group.html
   keys="ch04-4_1,ch04-4_2,ch04-4_3"
   columns=3
   label="Speech-gesture generation capabilities"
%}

### Cloning capabilities

These videos illustrate the *cloning* capabilities of Gelina. Speech-gesture generation is conditioned on a short prefix (around 5-7s), enabling voice and gestural style cloning.

{% include video-group.html
   keys="ch04-4_4,ch04-4_5,ch04-4_6"
   columns=3
   label="Cloning capabilities"
%}

### Comparison to state-of-the-art gesture generation models

These videos illustrate the differences between Gelina and other gesture generation models. In these examples, Gelina is used in the *Speech-to-gesture* mode, allowing the comparison of temporally aligned gestures.

{% include video-group.html
   keys="ch04-4_7,ch04-4_8,ch04-4_9,ch04-4_10"
   columns=2
   label="Comparison against unimodal gesture generation models"
%}

### Failure cases

We noticed several failures when generating speech and gestures. Some cases show incorrect rotations. Since the same issue appears in EMAGE, it may come from a bug in the shared rotation conversion code.

In random voice generation (without a prompt), some voices have poor quality — they may sound robotic or sometimes only partly understandable

{% include video-group.html
   keys="ch04-4_11,ch04-4_12"
   columns=2
   label="Failure cases"
%}
