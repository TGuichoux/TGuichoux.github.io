---
title: 'Unified speech-gesture generation via interleaved token prediction'
uid: ch04
chapter_number: 4
description: 
pdf: ''
code: ''

---

<div class="toc" markdown="1">
**On this page**

* Contents
{:toc}
</div>



## Results of the user study


{% include figure.html
   src="/assets/images/gelina_mos.png"
   id="Figure 4.5"
   label="fig-ch04-4_5"
   caption="Mean Opinion Scores with 95% confidence intervals from user evaluation across three aspects: Voice human-likeness, speech-gesture synchrony, and Gesture human-likeness."
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
