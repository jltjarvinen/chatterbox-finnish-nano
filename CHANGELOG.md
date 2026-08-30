# Changelog

## v0.1.3 - 2026-08-30

- Updated the Finnish Nano release to the final constrained-EOS checkpoint.
- Canonical public T3 is FP16, SHA256 `d25e3ac95eefefb58c40ad4d5a47b4fa621bc1bd92e91f2d904f622d5458ad26`.
- Locked F32 projection source SHA256 `5a8bf48cc23938bcf462c26d10a5686616c2081dea94d0a0da983ff590f3fe35`.
- Final FP16 quality gate: Finnish WER 8.22%, CER 0.95%, exact 9/12.
- Finnish EOS-ASR: WER 8.48%, CER 1.38%, exact 60/100.
- Endpoint safety gate: 200 generations, 0 generation-limit hits, 0 premature >1 s cases, 0 audio tails >1 s, maximum tail 0.78 s.
- Added GGUF release path for CrispASR (F16, Q8_0, Q4_K T3); Nano reuses the unchanged Turbo MeanFlow S3Gen companion.

## v0.1.2 - 2026-08-27

- Updated the Finnish T3 model to the selected v0.1.2 checkpoint.
- Final T3 SHA256: `5a7fb1eaabff39f22af7274f1a7fc344d2910488c0c5e61c5fb6a863f21bcadc`.
- Finnish number-to-speech expansion is enabled by default.
- Release sampling defaults are `0.8 / 0.95 / 1000 / 1.2`.
- Automatic Finnish evaluation: WER 10.60%, CER 1.65%.
- Added the validated FP16 T3 revision.
- Removed only unused `s3gen.safetensors`.
- Slim package size is 1,507,172,022 bytes, 41.21% smaller than the full package.
- Restored the hosted Space template to the source repository.

## v0.1.0 - 2026-08-20

First public Finnish Nano release. Historical research-run identifiers are intentionally omitted from the current release documentation.
