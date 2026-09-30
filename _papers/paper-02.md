---
title: 'Lina-Speech: Gated Linear Attention and Initial-State Tuning for Multi-Sample Prompting Text-To-Speech Synthesis'
uid: p02
order: 2
authors:
- 'Théodor Lemerle'
- 'Téo Guichoux'
- 'Nicolas Obin'
- 'Axel Roebel'

venue: 'AAAI Workshop on audio centric AI'
year: '2026'
description: 'We introduce Lina-Speech, a codec-based TTS model based pnt gated-linear attention.'
doi: ''
pdf: 'https://arxiv.org/pdf/2410.23320'
arxiv: ''
code: 'https://github.com/theodorblackbird/lina-speech'
download: ''
bibtex: |
  @InProceedings{lemerle2026linaspeech,
  title = {Lina-Speech: Gated Linear Attention and Initial-State Tuning for Multi-Sample Prompting Text-To-Speech Synthesis},
  author = {Lemerle, Th\'eodor and Guichoux, T\'eo and Roebel, Axel and Obin, Nicolas},
  booktitle = {Proceedings of the AAAI 2026 Workshop on Audio-Centric AI: Towards Real-World Multimodal Reasoning and Application Use Cases (Audio-AAAI)},
  pages = {1--20},
  year = {2026},
  editor = {Komatsu, Tatsuya and Imoto, Keisuke and Gao, Xiaoxue and Ono, Nobutaka and Chen, Nancy F.},
  volume = {312},
  series = {Proceedings of Machine Learning Research},
  month = {26 Jan},
  publisher = {PMLR},
  pdf = {https://raw.githubusercontent.com/mlresearch/v312/main/assets/lemerle26a/lemerle26a.pdf},
  url = {https://proceedings.mlr.press/v312/lemerle26a.html}
  }
---

## Abstract

Neural codec language models, built on transformer architecture, have revolutionized text-to-speech (TTS) synthesis, excelling in voice cloning by treating it as a prefix continuation task. However, their limited context length hinders their effectiveness to short speech samples. As a result, the voice cloning ability is restricted to a limited coverage and diversity of the speaker’s prosody and style. Besides, adapting prosody, accent, or appropriate emotion from a short prefix remains a challenging task. Finally, the quadratic complexity of self-attention limits inference throughput. In this work, we introduce Lina-Speech, a TTS model with Gated Linear Attention (GLA) to replace standard self-attention as a principled backbone, improving inference throughput while matching state-of-the-art performance. Leveraging the stateful property of recurrent architecture, we introduce an Initial-State Tuning (IST) strategy that unlocks the possibility of multiple speech sample conditioning of arbitrary numbers and lengths and provides a comprehensive and efficient strategy for voice cloning and out-of-domain speaking style and emotion adaptation. We demonstrate the effectiveness of this approach for controlling fine-grained characteristics such as prosody and emotion. Code, checkpoints, and demo are freely available: https://github.com/theodorblackbird/lina-speech
