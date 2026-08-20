from chatterbox_nano_fi.text import normalize_finnish, split_for_tts


def test_normalize_basic_finnish():
    assert normalize_finnish("hei maailma") == "Hei maailma."


def test_split_for_tts_keeps_short_text_single_chunk():
    assert split_for_tts("Hei! Mitä kuuluu?", max_chars=80) == ["Hei! Mitä kuuluu?"]


def test_number_expansion_is_opt_in():
    assert "12" in normalize_finnish("Kello on 12", expand_numbers=False)
    assert "12" not in normalize_finnish("Kello on 12", expand_numbers=True)
