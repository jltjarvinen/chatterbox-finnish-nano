# Known limitations

v0.1.0 is already useful for Finnish conversational TTS, but it is not error-free.

- **Occasional syllable/fragment drops.** A syllable or short part of a word can sometimes disappear. This was observed across several otherwise-good checkpoints and is not specific to the selected 015b step 20 checkpoint.
- **Trailing quiet/noise.** Some generations can end with several seconds of silence or very-low-level artifacts after the spoken sentence has finished. v0.1.0 does not silently trim this output.
- **Stochastic output.** T3 is autoregressive and sampled. Re-running the same sentence can produce a different result. The CLI therefore uses a random seed unless `--seed` is specified.
- **Sampling controls matter.** Lower temperature is generally more conservative; higher temperature can increase variation. v0.1.0 does not claim a globally optimal sampling preset.
- **Reference cloning is secondary.** The built-in no-reference path was the primary listening target. Optional reference conditioning is retained and was sanity-tested successfully with a previously unseen speaker, but it was less extensively evaluated than the built-in path.
- **Text normalization is intentionally small.** Basic punctuation cleanup and optional number expansion are included. Context-sensitive dates, times, units, abbreviations and every Finnish inflection are not yet normalized comprehensively.

These are appropriate targets for a later v0.2 rather than blockers for the first public release.
