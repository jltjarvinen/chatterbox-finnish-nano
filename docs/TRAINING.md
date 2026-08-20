# Training recipe used for v0.1.0

This document records the selected path rather than every experiment attempted during development.

## 1. Synthetic Finnish S3 dataset

The training text was assembled from Finnish Project Gutenberg prose and cleaned/split into short TTS-friendly utterances. The source pool used:

- *Rautatie* #10481
- *Seitsemän veljestä* #11940
- *Hanna* #13140
- *Papin tytär* #13662
- *Papin rouva* #13663
- *Lyhyitä kertomuksia* #12612
- *Lehtori Hellmanin vaimo* #11295

The synthetic teacher was `ResembleAI/Chatterbox-Multilingual-TTS`, referred to throughout the research notes as **Chatterbox Multilingual V2** to distinguish it from the separate `ResembleAI/Chatterbox-Multilingual-TTS-V3` release. A single selected Rautatie reference recording was used as V2 conditioning for every synthetic utterance; the other books contributed text only.

Approximately 15,000 unique Finnish text → speech-token targets were generated. The stored target was V2's own **free-running autoregressive S3 sequence**, not teacher logits or a KL target. The resulting cache therefore implements sequence-level distillation: after target generation, no V2/V3 teacher was required during the final Nano optimization.

## 2. Full-T3 Finnish adaptation (014)

Starting point: pristine stock Chatterbox Nano.

- data: the ~15k unique cached V2 S3 sequences
- conditioning during training: fixed Rautatie conditioning
- trainable: the complete used Nano T3 path (all 12 GPT-2-small blocks, position embedding, condition encoder, text/speech embeddings and heads, final layer norm)
- frozen: voice encoder and S3/MeanFlow waveform path
- objective: causal text next-token CE + causal speech next-token CE
- learning rate: `1e-4`
- epochs: 3
- selected parent: epoch 3

The three epoch schedule was informed by the public Danish CoRal Chatterbox Turbo recipe [CoRal-project/roest-v3-chatterbox-350m](https://huggingface.co/CoRal-project/roest-v3-chatterbox-350m), which reports three epochs at LR `1e-4`. It was used as a schedule starting point. Epoch 3 was still selected by listening to the Finnish Nano checkpoints.

Built-in Nano conditioning remained usable after training and sounded very similar to the Rautatie-conditioned evaluation, so reference audio was not required for the release path.

## 3. Real-audio micro-polish (015b)

A first full-T3 real-audio polish at LR `1e-5` collapsed into repetitive speech. It is **not** part of the release recipe.

The successful micro-polish returned to 014 epoch 3 and intentionally protected the autoregressive speech interface:

- real target: S3 tokens derived from the project's cleaned Rautatie audio
- max real clip duration: 20 s
- learning rate: constant `1e-6`
- optimizer: AdamW, betas `(0.9, 0.95)`, weight decay `0.01`
- gradient clip: `1.0`
- objective: speech next-token CE only
- trainable: `text_emb + last 2 GPT-2 blocks + ln_f`
- frozen: `cond_enc`, `speech_emb`, `speech_head`, `text_head`, `wpe`, first 10 GPT-2 blocks
- updates: 20 optimizer steps
- selected checkpoint: step 20

Continuing the same micro-polish to cumulative steps 30/40/60/80 produced no meaningful audible improvement, so step 20 was selected as the release checkpoint.

## Why the release stops here

The goal of v0.1 is a useful Finnish Nano, not an exhaustive benchmark optimum. Listening tests found 015b step 20 slightly better than 014 epoch 3, while further real-audio updates were effectively flat. Remaining defects are better treated as release limitations or future inference/training work than as a reason to keep the initial release blocked.
