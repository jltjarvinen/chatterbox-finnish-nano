from chatterbox_nano_fi.release import model_card


def test_model_card_explains_training_teacher_and_sources():
    card = model_card("example/chatterbox-finnish-nano", "abc123")
    assert "ResembleAI/Chatterbox-Multilingual-TTS" in card
    assert "ResembleAI/Chatterbox-Multilingual-TTS-V3" in card
    assert "Rautatie" in card
    assert "Seitsemän veljestä" in card
    assert "Hanna" in card
    assert "Papin tytär" in card
    assert "Papin rouva" in card
    assert "Lyhyitä kertomuksia" in card
    assert "Lehtori Hellmanin vaimo" in card
    assert "15,000 unique free-running S3" in card
    assert "sequence-level" in card
    assert "20 optimizer" in card
    assert "https://huggingface.co/spaces/JJarvinen/chatterbox-finnish-nano" in card
