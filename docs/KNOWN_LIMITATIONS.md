# Known limitations

v0.1.3 is intended for Finnish conversational TTS but it is not error-free.

- **Autoregressive stochastic output.** Different seeds can produce different speech.
- **Finite endpoint validation.** The 200-case v0.1.3 endpoint gate had zero >1 s audio tails and zero >1 s premature cases, but a finite gate cannot prove that no stochastic outlier can occur.
- **Occasional pronunciation errors.** Deliberately difficult phonetic inputs can still contain errors.
- **Reference cloning is secondary.** The built-in no-reference path is the primary release mode. Reference conditioning remains supported.
- **Normalization is deliberately small.** Common integers, decimals, percentages and euro amounts are supported. Dates, times, units, abbreviations and all context-sensitive Finnish inflections are not covered comprehensively.

The automatic WER and CER values are ASR-based intelligibility proxies, not MOS.
