---
title: 'Expressive speech and gesture synthesis with autoregressive continuous diffusion and decoupled classifier-free guidance'
uid: ch05
chapter_number: 5
description: 
pdf: ''
code: ''

---

<div class="toc" markdown="1">
**On this page**

* Contents
{:toc}
</div>



## Difference in the dynamics of the speech and gesture signals


{% include figure.html
   src="/assets/images/latent_properties.png"
   id="Figure 5.2.1"
   label="fig-ch05-5_2_1"
   caption="*Top and middle:* PCA views of gesture and speech latent sequences. Gesture and speech embedding sequences exhibit different properties. Gesture latent sequences (top) are smooth and slow-evolving, as demonstrated by repetitive patterns. As opposed to speech latent sequence is fast-varying and discontinuous. *Bottom:* Latent velocity of speech and gesture sequences. Velocity is computed as the difference between consecutive steps. Speech latent velocity (green) is much higher and more stable than the gesture latent velocity (blue), illustrating the different nature of both signals."
   layout="wide"
%}

{% include figure.html
   src="/assets/images/signal_properties.png"
   id="Figure 5.2.2"
   label="fig-ch05-5_2_2"
   caption="*Top:* Rotation-space motion velocity of the example segment. Velocity in the rotation space (before gesture encoding) and in the latent space are highly correlated. *Middle:* F0 of the corresponding segment. *Bottom:* Waveform of the corresponding segment"
   layout="wide"
%}

The associated speech-gesture animated sequence is provided bellow:

{% include video-group.html
   keys="ch05-5_1"
   columns=1
   label="Associated video"
%}

## Results of the user study


{% include figure.html
   src="/assets/images/gaspard_mos.png"
   id="Figure 5.11"
   label="fig-ch05-5_11"
   caption="Mean Opinion Scores with 95% confidence intervals from user evaluation across three aspects: Voice human-likeness, speech-gesture synchrony, and Gesture human-likeness."
   layout="wide"
%}


### Example stimuli from the user study:

We provide below illustrative samples from the user study conducted in Chapter 5.

#### Human recordings

{% include video-group.html
   keys="ch05-5_2,ch05-5_3,ch05-5_4,ch05-5_5"
   columns=3
   label="Examples from the user study."
%}

#### Gaspard with $$\gamma^G_g = 1.0$$ $$\gamma^G_s = 2.5$$

{% include video-group.html
   keys="ch05-5_6,ch05-5_7,ch05-5_8,ch05-5_9"
   columns=3
   label="Examples from the user study."
%}

#### Gaspard with $$\gamma^G_g = 0.825 $$ $$\gamma^G_s = 6.5$$

{% include video-group.html
   keys="ch05-5_10,ch05-5_11,ch05-5_12,ch05-5_13"
   columns=3
   label="Examples from the user study."
%}

#### Cascaded ablation

{% include video-group.html
   keys="ch05-5_14,ch05-5_15,ch05-5_16,ch05-5_17"
   columns=3
   label="Examples from the user study."
%}


## Speech adaptation to gestures

{% include figure.html
   src="/assets/images/speech_adaptation.png"
   id="Figure 5.10"
   label="fig-ch05-5_10"
   caption="Impact of gesture speed on speech generation. Speech is generated while conditioning the model on fixed gesture inputs with varying speeds. Increasing gesture speed results in a higher speech rate and fewer IPUs."
   layout="wide"
%}

{% include video-group.html
   keys="ch05-5_18,ch05-5_19"
   columns=3
   label="Examples from the user study."
%}