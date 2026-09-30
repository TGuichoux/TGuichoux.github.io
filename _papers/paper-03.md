---
title: 'Low-Framerate Speech Tokenization via Two-Stage Latent Patch Modeling'
uid: p03
order: 3
authors:
- 'Théodor Lemerle'
- 'Diego Torres'
- 'Téo Guichoux'
- 'Nicolas Obin'
- 'Axel Roebel'

venue: 'Interspeech'
year: '2026'
description: 'We introduce a two-stage audio--codec for low-framerate text-to-speech.'
doi: '10.21437/Interspeech.2026-2863'
pdf: 'https://www.researchgate.net/profile/Nicolas-Obin/publication/414227348_Low-Framerate_Speech_Tokenization_via_Two-Stage_Latent_Patch_Modeling/links/6aa42d88fa52160a3abb0e73/Low-Framerate-Speech-Tokenization-via-Two-Stage-Latent-Patch-Modeling.pdf'
arxiv: ''
code: ''
download: ''

bibtex: |
  @inproceedings{lemerle2026lowframerate,
  title     = {{Low-Framerate Speech Tokenization via Two-Stage Latent Patch Modeling}},
  author    = {Théodor Lemerle and Diego Torres and Téo Guichoux and Nicolas Obin and Axel Roebel},
  year      = {2026},
  booktitle = {{Interspeech 2026}},
  pages     = {3971--3976},
  doi       = {10.21437/Interspeech.2026-2863},
  issn      = {2958-1796},
  }
---

## Abstract

Recent advances in neural speech tokenizers rely on lowframerate, semantically rich latent representations that facilitate downstream generative modeling tasks such as text-to-speech. However, achieving high perceptual quality at low bitrate and framerate remains computationally demanding, as it typically requires joint compression, adversarial training, and semantic supervision, resulting in expensive training. In this work, we introduce Z-CODEC, a two-stage latent speech codec. In the first stage, we train a high-framerate variational autoencoder (VAE) with adversarial objectives to capture fine-grained acoustic details and absorb the complexity of adversarial training. In the second stage, we perform final compression within the latent space of the first stage using flow matching and incorporate semantic supervision, enabling highquality low-framerate tokenization. Our approach achieves state-of-the-art reconstruction quality for both low-bitrate discrete tokenizers and continuous settings, outperforming or matching strong baselines. Importantly, the staged design of Z-CODEC makes training tractable on a single RTX 4070 GPU, enabling high-quality, low-framerate speech tokenizer reproducible on consumer-grade hardware.



