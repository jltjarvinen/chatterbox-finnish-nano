# v0.1.0 release checklist

- [x] Build `015b step 20` model and verify it locally.
- [x] Verify built-in zero-shot Finnish synthesis by listening.
- [x] Sanity-test optional reference conditioning with a previously unseen speaker.
- [ ] Promote the verified RC1 directory to `models/chatterbox-nano-fi-v0.1.0` with `./scripts/finalize_rc1.sh`.
- [ ] Inspect final model `README.md`, `RELEASE.json` and T3 SHA256.
- [ ] Upload model repo privately first.
- [ ] Confirm model can be downloaded by repo ID and synthesized through `cbnano-fi-infer`.
- [ ] Make the model repo public only after license/provenance review.
- [ ] Publish this clean source repository/tag as `v0.1.0`.
