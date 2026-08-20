from pathlib import Path

from chatterbox_nano_fi.release import model_card


ROOT = Path(__file__).resolve().parents[1]


def test_main_readme_has_no_ai_tell_punctuation():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "—" not in text
    assert "–" not in text
    assert ";" not in text
    assert " -- " not in text


def test_generated_model_card_has_no_ai_tell_punctuation():
    text = model_card("example/chatterbox-finnish-nano", "abc123")
    assert "—" not in text
    assert "–" not in text
    assert ";" not in text
    assert " -- " not in text


def test_space_template_exists_and_resets_conditioning():
    app = (ROOT / "space" / "app.py").read_text(encoding="utf-8")
    assert "@spaces.GPU" in app
    assert 'SPACES_ZERO_GPU' in app
    assert 'else "cpu"' in app
    assert "restore_builtin_conditioning()" in app
    assert "concurrency_limit=1" in app
    requirements = (ROOT / "space" / "requirements.txt").read_text(encoding="utf-8")
    assert "torch>=2.8" in requirements
    assert "torch==" not in requirements
    assert "torchaudio" not in requirements
    assert "gradio" not in requirements
    prepare = (ROOT / "tools" / "prepare_space.py").read_text(encoding="utf-8")
    assert "PackageNotFoundError" in prepare
    assert (ROOT / "tools" / "prepare_space.py").is_file()
    space_readme = (ROOT / "space" / "README.md").read_text(encoding="utf-8")
    assert "JJarvinen/chatterbox-finnish-nano" in space_readme
    assert "models:" in space_readme
