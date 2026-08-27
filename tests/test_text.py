from chatterbox_nano_fi.text import normalize_finnish, split_for_tts


def test_normalize_basic_finnish():
    assert normalize_finnish("hei maailma") == "Hei maailma."


def test_split_for_tts_keeps_short_text_single_chunk():
    assert split_for_tts("Hei! Mitä kuuluu?", max_chars=80) == ["Hei! Mitä kuuluu?"]


def test_number_expansion_is_opt_in():
    assert "12" in normalize_finnish("Kello on 12", expand_numbers=False)
    assert "12" not in normalize_finnish("Kello on 12", expand_numbers=True)


def test_number_expansion_handles_finnish_dates_before_decimals():
    assert normalize_finnish("Tänään 27.8.2026 on hyvä päivä", expand_numbers=True) == (
        "Tänään kahdeskymmenesseitsemäs elokuuta kaksituhatta kaksikymmentäkuusi on hyvä päivä."
    )
    assert normalize_finnish("Päivä on 27.8.", expand_numbers=True) == (
        "Päivä on kahdeskymmenesseitsemäs elokuuta."
    )
    assert normalize_finnish("Päivä on 2026-08-27", expand_numbers=True) == (
        "Päivä on kahdeskymmenesseitsemäs elokuuta kaksituhatta kaksikymmentäkuusi."
    )


def test_number_expansion_keeps_decimal_semantics():
    assert normalize_finnish("Arvo on 3.14", expand_numbers=True) == "Arvo on kolme pilkku yksi neljä."


def test_number_expansion_handles_clock_times():
    assert normalize_finnish("Kello on 12:30", expand_numbers=True) == "Kello on kaksitoista kolmekymmentä."
    assert normalize_finnish("Tavataan klo 12.30", expand_numbers=True) == "Tavataan kello kaksitoista kolmekymmentä."
    assert normalize_finnish("Kello on 9:05", expand_numbers=True) == "Kello on yhdeksän nolla viisi."
