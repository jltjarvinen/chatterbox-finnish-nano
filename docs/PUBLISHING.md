# Publishing v0.1.0

The source repository and the model repository are separate releases.

## 1. Finalize the model directory

If `models/chatterbox-nano-fi-v0.1-rc1` is the already-listened-to artifact:

```bash
./scripts/finalize_rc1.sh
```

This does not retrain or alter model weights. It copies the verified directory to
`models/chatterbox-nano-fi-v0.1.0` and regenerates final release metadata.

## 2. Upload the model privately

```bash
export HF_REPO_ID=YOUR_NAMESPACE/chatterbox-finnish-nano
./scripts/publish_model.sh
```

The default is private. The uploaded repository contains only the standalone model
runtime files, model card and release metadata. It does not contain the training
corpus, experiment caches or private bucket contents.

Download the private repo by ID and run at least one built-in zero-shot synthesis
and, optionally, one reference-speaker synthesis before changing visibility.

## 3. Make the verified model public

Changing visibility does not require uploading the weights again:

```bash
export HF_REPO_ID=YOUR_NAMESPACE/chatterbox-finnish-nano
./scripts/make_model_public.sh
```

## 4. Publish the source repository

The clean source repository intentionally contains no model weights or training
data. A minimal first publication is:

```bash
git init
git add .
git commit -m "Release Chatterbox Finnish Nano v0.1.0"
git branch -M main
# Add your chosen GitHub remote here.
git tag -a v0.1.0 -m "Chatterbox Finnish Nano v0.1.0"
git push -u origin main
git push origin v0.1.0
```

Review `docs/LICENSES_AND_PROVENANCE.md` before changing either repository from
private to public.

## Update the model card without re-uploading weights

If the private model repository is already uploaded and only the model-card text changes, regenerate the local model card and upload `README.md` only:

```bash
export HF_REPO_ID=YOUR_NAMESPACE/chatterbox-finnish-nano
./scripts/update_model_card.sh
```

This does not modify model weights or repository visibility. It is safe to run before `make_model_public.sh`.

## Optional Hugging Face Space

The repository includes a standalone Gradio template in `space/`.

A practical publication order is:

1. Keep the model repository private while checking the final model card and files.
2. Make the model repository public.
3. Create a Gradio Space and copy the contents of `space/` into it.
4. Set the Space variable `MODEL_ID` to the public model repository ID.
5. Select ZeroGPU in the Space hardware settings.

If you want to test the Space before the model becomes public, add an `HF_TOKEN` Space Secret with read access to the private model. Remove that secret when it is no longer needed.

The Space template serializes inference requests and restores the built-in conditioning after each request. This matters because reference audio changes the conditioning stored in the Chatterbox model instance.
