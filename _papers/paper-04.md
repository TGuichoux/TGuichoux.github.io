---
title: '2D or not 2D: How Does the Dimensionality of Gesture Representation Affect 3D Co-Speech Gesture Generation?'
uid: p04
order: 4
authors:
- 'Téo Guichoux'
- 'Laure Soulier'
- 'Nicolas Obin'
- 'Catherine Pelachaud'

venue: 'IVA'
year: '2024'
description: 'In this article, we compare the impact of the dimensionality of gesture (2D or 3D keypoints) on the performances of gesture generation models.'
doi: '10.1145/3652988.3673934'
pdf: 'https://dl.acm.org/doi/pdf/10.1145/3652988.3673934'
arxiv: 'https://arxiv.org/pdf/2409.10357'
code: 'https://github.com/TGuichoux/2D-or-not-2D'
download: ''
bibtex: |
  @inproceedings{guichoux2024dimensionality,
  author = {Guichoux, T{\'e}o and Soulier, Laure and Obin, Nicolas and Pelachaud, Catherine},
  title = {2D or not 2D: How Does the Dimensionality of Gesture Representation Affect 3D Co-Speech Gesture Generation?},
  year = {2024},
  isbn = {9798400706257},
  publisher = {Association for Computing Machinery},
  address = {New York, NY, USA},
  url = {https://doi.org/10.1145/3652988.3673934},
  doi = {10.1145/3652988.3673934},
  booktitle = {Proceedings of the 24th ACM International Conference on Intelligent Virtual Agents},
  articleno = {22},
  numpages = {4},
  keywords = {Co-speech gesture generation, Diffusion Models, Pose Representation, Sequence modeling},
  location = {GLASGOW, United Kingdom},
  series = {IVA '24}
  }
---

## Abstract

Co-speech gestures are fundamental for communication. The advent of recent deep learning techniques has facilitated the creation of lifelike, synchronous co-speech gestures for Embodied Conversational Agents. "In-the-wild" datasets, aggregating video content from platforms like YouTube via human pose detection technologies, provide a feasible solution by offering 2D skeletal sequences aligned with speech. Concurrent developments in lifting models enable the conversion of these 2D sequences into 3D gesture databases. However, it is important to note that the 3D poses estimated from the 2D extracted poses are, in essence, approximations of the ground-truth, which remains in the 2D domain. This distinction raises questions about the impact of gesture representation dimensionality on the quality of generated motions. Our study examines the effect of using either 2D or 3D joint coordinates as training data on the performance of speech-to-gesture deep generative models


