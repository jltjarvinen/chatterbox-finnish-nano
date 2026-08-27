# Known limitations

v0.1.2 is useful for Finnish conversational TTS but it is not error-free.

- **Autoregressive EOS variation.** Rare sampled generations can continue beyond
  the expected utterance end before EOS.
- **Occasional pronunciation errors.** Deliberately difficult phonetic probes
  still contain errors.
- **Stochastic output.** Different seeds can produce different speech.
- **Reference cloning is secondary.** The built-in no-reference path is the
  primary release mode. Reference conditioning is supported and smoke-tested.
- **Normalization is deliberately small.** Common integers, decimals,
  percentages and euro amounts are supported. Dates, times, units,
  abbreviations and all context-sensitive Finnish inflections are not covered
  comprehensively.

The automatic WER and CER values are ASR-based intelligibility proxies, not MOS.
