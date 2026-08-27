# Evaluation notes for v0.1.2

v0.1.2 was selected using controlled listening and a reproducible automatic
release evaluation.

## Automatic Finnish evaluation

A fixed 100-utterance Finnish set scored:

```text
WER   10.60%
CER    1.65%
exact 54%
```

The values are ASR-based intelligibility proxies, not MOS.

## EOS stability

The 100-generation release smoke produced 2 structured runaway events over one
second and 1 over two seconds. It produced no generation-limit hits and no
tail45 events over one second.

## Conditioning

The built-in no-reference voice is the primary release mode. Optional reference
conditioning was also smoke-tested successfully.
