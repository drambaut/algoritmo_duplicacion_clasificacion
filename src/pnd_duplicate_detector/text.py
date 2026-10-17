"""Conservative Spanish text normalization."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter

SPANISH_STOPWORDS = frozenset(
    {
        "a", "al", "ante", "bajo", "con", "contra", "de", "desde", "durante", "e",
        "el", "ella", "ellos", "en", "entre", "es", "esa", "ese", "esta", "este",
        "hacia", "la", "las", "lo", "los", "mas", "mi", "o", "para", "pero", "por",
        "que", "se", "sin", "sobre", "su", "sus", "un", "una", "uno", "unos", "unas",
        "y", "ya", "como", "donde", "nos", "porque", "son", "tambien",
    }
) | frozenset({"d" + "el"})


def normalize_text(value: object) -> str:
    """Lowercase, remove accents, and retain letters, digits and spaces."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFD", str(value).lower())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text)).strip()


def tokenize(value: object, *, remove_stopwords: bool = True) -> list[str]:
    tokens = normalize_text(value).split()
    return [token for token in tokens if token not in SPANISH_STOPWORDS] if remove_stopwords else tokens


def token_counts(value: object) -> Counter[str]:
    return Counter(tokenize(value))


def character_shingles(value: object, size: int = 5) -> set[str]:
    """Set of contiguous character chunks, including content across word breaks."""
    compact = normalize_text(value).replace(" ", "")
    if not compact:
        return set()
    if len(compact) <= size:
        return {compact}
    return {compact[index : index + size] for index in range(len(compact) - size + 1)}
