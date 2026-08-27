# Publishing v0.1.2

The publish workflow consumes a previously validated private release artifact. The private storage location is intentionally not part of the public repository.

Targets:

```text
GitHub
jltjarvinen/chatterbox-finnish-nano
tag v0.1.2

Hugging Face model
JJarvinen/chatterbox-finnish-nano
main = BF16
fp16 = FP16 T3 variant
tags v0.1.2 and v0.1.2-fp16

Hugging Face Space
JJarvinen/chatterbox-finnish-nano
```

Before replacing model main, preserve the old main as tag `v0.1.0`.

The final BF16 model must not contain `s3gen.safetensors`.
It must retain `s3gen_meanflow.safetensors` and `t3_nano_v1.yaml`.

The hosted Space pins model revision `v0.1.2` and enables Finnish number
expansion by default.
