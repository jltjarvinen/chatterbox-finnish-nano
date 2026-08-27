# Licenses and provenance

## Repository source code

The source code in this repository is distributed under the MIT license in
`LICENSE`.

## Base model

The release is assembled from a pinned `ResembleAI/chatterbox-nano` snapshot and
a Finnish-adapted T3 checkpoint. The base model assets needed by the Nano runtime
are retained, including the built-in `conds.pt` conditioning and MeanFlow S3Gen
weights.

The final slim package intentionally omits only the legacy
`s3gen.safetensors` file because the pinned Nano runtime does not load it.

## Training sources

The Finnish adaptation uses cached synthetic Finnish S3 targets generated with
Chatterbox Multilingual V2 from public-domain Finnish prose source text. The
public runtime repository contains neither training audio, source-text dumps,
nor cached synthetic target sequences.

Exact release weights are identified by SHA256 rather than private experiment
names or research bucket paths.
