# v0.1.2 release checklist

- [x] Select E4 checkpoint and lock SHA256 `5a7fb1eaabff39f22af7274f1a7fc344d2910488c0c5e61c5fb6a863f21bcadc`.
- [x] Verify BF16 and FP16 loader behavior.
- [x] Run 100-utterance Finnish WER and CER evaluation.
- [x] Run EOS stress evaluation.
- [x] Verify built-in conditioning.
- [x] Verify optional reference conditioning.
- [x] Verify Finnish number expansion is default-on.
- [x] Remove only unused `s3gen.safetensors`.
- [x] Verify all other full-vs-slim model files are byte-identical.
- [x] Verify deterministic full-vs-slim tokens and waveforms are identical.
- [x] Verify slim CUDA and CPU loading.
- [x] Preserve Hugging Face v0.1.0 before changing model main.
- [x] Publish BF16 main and FP16 revision.
- [x] Update hosted Space.
- [x] Publish GitHub source and tag `v0.1.2`.
