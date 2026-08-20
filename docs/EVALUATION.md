# Evaluation notes for v0.1.0

This release was selected primarily through controlled subjective listening rather than a formal MOS/WER benchmark.

## Checkpoint selection

- `014 epoch 3` was judged highly natural and already good Finnish.
- A conservative real-audio micro-polish from that parent improved quality slightly by `015b step 20`.
- Continuing the same micro-polish to cumulative steps 30, 40, 60 and 80 produced no meaningful audible improvement, so step 20 was retained.
- An earlier aggressive full-T3 real-audio polish at LR `1e-5` collapsed into repetitive speech and was discarded.

## Conditioning checks

- Built-in `conds.pt` reference-free generation remained good after Finnish adaptation.
- Rautatie-conditioned and built-in-conditioned evaluation sounded very similar during the full-T3 stage.
- After selecting `015b step 20`, reference conditioning with a previously unseen speaker was sanity-tested and worked correctly.

## Remaining audible defects

The main observed defects are stochastic rather than constant: an occasional syllable/short fragment may be dropped, and some generations can include a long quiet or low-level noisy tail after the spoken content. These were not considered blockers for v0.1.0.

No claim of a globally optimal sampling preset is made in this release.
