from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

_SPACES = re.compile(r"\s+")
_URL = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
_EMAIL = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")
_UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I)
_PERCENT = re.compile(r"(?<!\w)(-?\d+(?:[.,]\d+)?)\s*%")
_EURO = re.compile(r"(?<!\w)(-?\d+(?:[.,]\d+)?)\s*(?:€|eur\b)", re.I)
_INTEGER = re.compile(r"(?<![\w.,])(-?\d{1,9})(?![\w.,])")
_DECIMAL = re.compile(r"(?<!\w)(-?\d+)[,.](\d+)(?!\w)")
_DATE_DMY = re.compile(r"(?<!\d)(\d{1,2})\.(\d{1,2})\.(\d{4})(?!\d)")
_DATE_DM = re.compile(r"(?<!\d)(\d{1,2})\.(\d{1,2})\.(?!\d)")
_DATE_ISO = re.compile(r"(?<!\d)(\d{4})-(\d{1,2})-(\d{1,2})(?!\d)")
_TIME_KLO = re.compile(r"\b(?:klo|kello)\s*(\d{1,2})[.:](\d{2})(?!\d)", re.I)
_TIME_COLON = re.compile(r"(?<!\d)(\d{1,2}):(\d{2})(?!\d)")

_MONTHS_PARTITIVE = (
    "",
    "tammikuuta",
    "helmikuuta",
    "maaliskuuta",
    "huhtikuuta",
    "toukokuuta",
    "kesäkuuta",
    "heinäkuuta",
    "elokuuta",
    "syyskuuta",
    "lokakuuta",
    "marraskuuta",
    "joulukuuta",
)

_REPLACEMENTS = (
    ("\u00a0", " "),
    ("…", ", "),
    ("—", "-"),
    ("–", "-"),
    ("−", "-"),
    ("“", '"'),
    ("”", '"'),
    ("„", '"'),
    ("’", "'"),
    ("‘", "'"),
)

_DEFAULT_REJECT_PATTERNS = (
    r"<[^>]+>",
    r"\[(?:musiikkia|naurua|aplodit|epäselvää|katkos)[^\]]*\]",
    r"\b(?:http|www)\b",
)


@dataclass(frozen=True)
class TextQuality:
    accepted: bool
    reason: str = ""


def normalize_finnish(text: str, *, expand_numbers: bool = False) -> str:
    text = html.unescape(str(text or ""))
    text = unicodedata.normalize("NFC", text)
    for source, target in _REPLACEMENTS:
        text = text.replace(source, target)
    text = _UUID.sub(" ", text)
    text = _URL.sub(" ", text)
    text = _EMAIL.sub(" ", text)
    text = text.replace(" :", ":").replace(" ,", ",").replace(" .", ".")

    if expand_numbers:
        text = _expand_numbers(text)

    # Preserve the old punctuation behavior for colons that were not clock
    # times handled above.
    text = text.replace(":", ",")
    text = _SPACES.sub(" ", text).strip()
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    if text and text[-1] not in ".!?,-":
        text += "."
    return text


def _fallback_fi_number(number: int) -> str:
    ones = ("nolla", "yksi", "kaksi", "kolme", "neljä", "viisi", "kuusi", "seitsemän", "kahdeksan", "yhdeksän")
    if number < 0:
        return "miinus " + _fallback_fi_number(-number)
    if number < 10:
        return ones[number]
    if number < 20:
        return "kymmenen" if number == 10 else ones[number - 10] + "toista"
    if number < 100:
        tens, rest = divmod(number, 10)
        return ones[tens] + "kymmentä" + (ones[rest] if rest else "")
    if number < 1000:
        hundreds, rest = divmod(number, 100)
        prefix = "sata" if hundreds == 1 else ones[hundreds] + "sataa"
        return prefix + (_fallback_fi_number(rest) if rest else "")
    return str(number)


def _fi_number(value: str) -> str:
    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError):
        return value
    try:
        from num2words import num2words

        return num2words(number, lang="fi")
    except ImportError:
        # The package is a declared runtime dependency. This small fallback keeps
        # basic diagnostics usable in minimal environments.
        return _fallback_fi_number(number)


def _fi_ordinal(value: int) -> str:
    try:
        from num2words import num2words

        return num2words(value, lang="fi", to="ordinal")
    except ImportError:
        return _fallback_fi_number(value)


def _date_words(day: int, month: int, year: int | None = None) -> str | None:
    import datetime as _datetime

    try:
        _datetime.date(year if year is not None else 2000, month, day)
    except ValueError:
        return None
    parts = [_fi_ordinal(day), _MONTHS_PARTITIVE[month]]
    if year is not None:
        parts.append(_fi_number(str(year)))
    return " ".join(parts)


def _time_words(hour: int, minute: int, *, prefix: bool) -> str | None:
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        return None
    if minute == 0:
        spoken = _fi_number(str(hour))
    elif minute < 10:
        spoken = f"{_fi_number(str(hour))} nolla {_fi_number(str(minute))}"
    else:
        spoken = f"{_fi_number(str(hour))} {_fi_number(str(minute))}"
    return f"kello {spoken}" if prefix else spoken


def _expand_numbers(text: str) -> str:
    def date_dmy(match: re.Match[str]) -> str:
        day, month, year = map(int, match.groups())
        return _date_words(day, month, year) or match.group(0)

    def date_dm(match: re.Match[str]) -> str:
        day, month = map(int, match.groups())
        return _date_words(day, month) or match.group(0)

    def date_iso(match: re.Match[str]) -> str:
        year, month, day = map(int, match.groups())
        return _date_words(day, month, year) or match.group(0)

    def time_klo(match: re.Match[str]) -> str:
        hour, minute = map(int, match.groups())
        return _time_words(hour, minute, prefix=True) or match.group(0)

    def time_colon(match: re.Match[str]) -> str:
        hour, minute = map(int, match.groups())
        return _time_words(hour, minute, prefix=False) or match.group(0)

    def decimal(match: re.Match[str]) -> str:
        whole, fraction = match.group(1), match.group(2)
        sign = "miinus " if whole.startswith("-") else ""
        whole = whole.lstrip("-")
        spoken_fraction = " ".join(_fi_number(digit) for digit in fraction)
        return f"{sign}{_fi_number(whole)} pilkku {spoken_fraction}"

    # Date and clock patterns must run before the generic decimal rule so
    # 27.8.2026 is not interpreted as the decimal number 27.8.
    text = _DATE_DMY.sub(date_dmy, text)
    text = _DATE_ISO.sub(date_iso, text)
    text = _DATE_DM.sub(date_dm, text)
    text = _TIME_KLO.sub(time_klo, text)
    text = _TIME_COLON.sub(time_colon, text)
    text = _PERCENT.sub(lambda m: f"{_expand_numbers(m.group(1))} prosenttia", text)
    text = _EURO.sub(lambda m: f"{_expand_numbers(m.group(1))} euroa", text)
    text = _DECIMAL.sub(decimal, text)
    return _INTEGER.sub(lambda m: _fi_number(m.group(1)), text)


def assess_text(
    text: str,
    *,
    min_chars: int = 8,
    max_chars: int = 320,
    reject_patterns: Iterable[str] = _DEFAULT_REJECT_PATTERNS,
    max_uppercase_ratio: float = 0.45,
) -> TextQuality:
    if len(text) < min_chars:
        return TextQuality(False, "too_short")
    if len(text) > max_chars:
        return TextQuality(False, "too_long")
    if _URL.search(text) or _EMAIL.search(text):
        return TextQuality(False, "url_or_email")
    for pattern in reject_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return TextQuality(False, "editorial_or_markup")

    letters = [char for char in text if char.isalpha()]
    if not letters:
        return TextQuality(False, "no_letters")
    uppercase = sum(char.isupper() for char in letters) / len(letters)
    if uppercase > max_uppercase_ratio:
        return TextQuality(False, "too_much_uppercase")

    replacement_ratio = text.count("�") / max(1, len(text))
    if replacement_ratio > 0.0:
        return TextQuality(False, "invalid_unicode")
    return TextQuality(True)


def split_for_tts(text: str, max_chars: int = 220) -> list[str]:
    text = normalize_finnish(text)
    if len(text) <= max_chars:
        return [text]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(sentence) > max_chars:
            punctuation_parts = re.split(r"(?<=[,;:])\s+", sentence)
        else:
            punctuation_parts = [sentence]
        parts: list[str] = []
        for punctuation_part in punctuation_parts:
            if len(punctuation_part) <= max_chars:
                parts.append(punctuation_part)
                continue
            word_chunk = ""
            for word in punctuation_part.split():
                candidate = f"{word_chunk} {word}".strip()
                if word_chunk and len(candidate) > max_chars:
                    parts.append(word_chunk)
                    word_chunk = word
                else:
                    word_chunk = candidate
            if word_chunk:
                parts.append(word_chunk)
        for part in parts:
            candidate = f"{current} {part}".strip()
            if current and len(candidate) > max_chars:
                chunks.append(current)
                current = part
            else:
                current = candidate
    if current:
        chunks.append(current)
    return chunks
