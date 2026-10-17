from pnd_duplicate_detector.similarity import jaccard_shingles, lexical_cosine


def test_lexical_cosine_normalizes_accents_and_stopwords() -> None:
    left = "Arreglar las vias veredales y los puentes de Almeida"
    right = "Mejorar las vias y puentes veredales en Almeida"
    assert lexical_cosine(left, right) > 0.6


def test_jaccard_shingles_tolerates_a_typo() -> None:
    original = "Arreglar vias veredales y puentes de Almeida"
    typo = "Arreglar vias veredlales y puentes de Almeida"
    assert jaccard_shingles(original, typo) > 0.7
