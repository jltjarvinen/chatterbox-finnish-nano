# v0.1.2 training recipe

## Base

- Model: `ResembleAI/chatterbox-nano`
- Base revision: `71ccd1d0081b430592cea481f4307e764e07bc64`
- Runtime revision: `5de7a54aa4e5e2baadb0182dde554908b48b85c2`

## Clean Finnish targets

Final rows: `14,169`

Source SHA256:

```text
56b72efe90369e50e0eea35af2ea2fca540a74d84fdbfbd8bc7ef57b0fd4841d
```

Composition:

```text
original strict pass  12,602
regenerated accepted   1,567
final                  14,169
```

QC trailing silence was translated to S3-token trimming:

```text
remove_tokens = floor(trailing_removed_sec * 25)
```

There was no extra margin and leading trim was unchanged.

The trainer appends exactly one speech EOS target after `speech_ids`.

## Optimization

```text
3 epochs
LR 1e-4 to 0
joint text next-token CE + speech next-token CE

then

1 continuation epoch
LR 1e-5 to 0
fresh AdamW and scheduler
886 steps
```

Final continuation-epoch average losses:

```text
total CE   5.6305036394
text CE    2.8558590560
speech CE  2.7746445829
```

Final T3 SHA256:

```text
5a7fb1eaabff39f22af7274f1a7fc344d2910488c0c5e61c5fb6a863f21bcadc
```

The final checkpoint contains 155 BF16 tensors.
