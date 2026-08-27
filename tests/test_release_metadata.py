from chatterbox_nano_fi import RELEASE_CHECKPOINT, RELEASE_NAME

def test_release_identity_is_public_version_only():
    assert RELEASE_NAME == "v0.1.2"
    assert RELEASE_CHECKPOINT == "v0.1.2"
