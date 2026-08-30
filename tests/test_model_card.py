from chatterbox_nano_fi.release import model_card

def test_model_card_explains_v013_public_release():
    card = model_card("example/chatterbox-finnish-nano", "abc123")
    assert "v0.1.3" in card
    assert "14,169" in card
    assert "s3gen_meanflow.safetensors" in card
    assert "s3gen.safetensors" in card
    assert "WER" in card
    assert "CER" in card
    assert "number-to-speech" in card
    assert "20 optimizer" not in card
    assert "real-audio" not in card
    assert "https://huggingface.co/spaces/JJarvinen/chatterbox-finnish-nano" in card
