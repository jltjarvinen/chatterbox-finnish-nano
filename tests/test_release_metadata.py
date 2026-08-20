from chatterbox_nano_fi import RELEASE_CHECKPOINT, RELEASE_NAME, RESEARCH_BUCKET_PATH


def test_release_candidate_is_015b_step_20():
    assert RELEASE_NAME == "v0.1.0"
    assert RELEASE_CHECKPOINT == "015b-step-020"
    assert RESEARCH_BUCKET_PATH.endswith("real-audio-micro-polish-v1/checkpoints/step-020.safetensors")
