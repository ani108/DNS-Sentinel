"""Feature extraction for domain classification.

Extracts 16 lexical/statistical features from domain names for ML classification.
"""
import math
import re
from typing import Dict
from collections import Counter
from app.core.constants import HIGH_RISK_TLDS

# English character bigram frequencies (simplified reference)
# Source: Aggregated from English word lists
_ENGLISH_BIGRAMS = {
    "th": 3.56, "he": 3.07, "in": 2.43, "er": 2.05, "an": 1.99,
    "re": 1.85, "on": 1.76, "at": 1.49, "en": 1.45, "nd": 1.35,
    "ti": 1.34, "es": 1.34, "or": 1.28, "te": 1.27, "of": 1.17,
    "ed": 1.17, "is": 1.13, "it": 1.12, "al": 1.09, "ar": 1.07,
    "st": 1.05, "to": 1.04, "nt": 1.04, "ng": 0.95, "se": 0.93,
    "ha": 0.93, "as": 0.87, "ou": 0.87, "io": 0.83, "le": 0.83,
    "ve": 0.83, "co": 0.79, "me": 0.79, "de": 0.76, "hi": 0.76,
    "ri": 0.73, "ro": 0.73, "ic": 0.70, "ne": 0.69, "ea": 0.69,
    "ra": 0.62, "ce": 0.65, "li": 0.62, "ch": 0.60, "ll": 0.58,
    "be": 0.58, "ma": 0.57, "si": 0.55, "om": 0.55, "ur": 0.54,
}

_ENGLISH_TRIGRAMS = {
    "the": 3.51, "and": 1.59, "ing": 1.47, "her": 0.82, "hat": 0.65,
    "his": 0.60, "tha": 0.59, "ere": 0.56, "for": 0.55, "ent": 0.53,
    "ion": 0.51, "ter": 0.46, "was": 0.46, "you": 0.44, "ith": 0.43,
    "ver": 0.43, "all": 0.42, "wit": 0.40, "thi": 0.39, "tio": 0.38,
}

VOWELS = set("aeiou")
CONSONANTS = set("bcdfghjklmnpqrstvwxyz")


def shannon_entropy(text: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not text:
        return 0.0
    freq = Counter(text)
    length = len(text)
    return -sum(
        (count / length) * math.log2(count / length)
        for count in freq.values()
    )


def _max_consecutive_run(text: str, char_set: set) -> int:
    """Find the longest consecutive run of characters from the given set."""
    max_run = 0
    current_run = 0
    for ch in text:
        if ch in char_set:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0
    return max_run


def _avg_ngram_freq(text: str, ngram_table: dict, n: int) -> float:
    """Calculate average n-gram frequency score against English reference."""
    if len(text) < n:
        return 0.0
    ngrams = [text[i:i+n] for i in range(len(text) - n + 1)]
    if not ngrams:
        return 0.0
    scores = [ngram_table.get(ng, 0.0) for ng in ngrams]
    return sum(scores) / len(scores)


def _parse_domain(domain: str) -> dict:
    """Parse domain into components."""
    domain = domain.lower().rstrip(".")
    labels = domain.split(".")
    
    tld = labels[-1] if labels else ""
    sld = labels[-2] if len(labels) >= 2 else ""
    subdomain = ".".join(labels[:-2]) if len(labels) > 2 else ""
    
    return {
        "full": domain,
        "labels": labels,
        "tld": tld,
        "sld": sld,
        "subdomain": subdomain,
    }


def extract_features(domain: str) -> list:
    """Extract the 16-feature vector for ML classification.
    
    Returns a list of 16 float values in the order expected by the model.
    """
    d = extract_features_dict(domain)
    return [
        d["domain_length"],
        d["sld_length"],
        d["subdomain_length"],
        d["num_labels"],
        d["shannon_entropy"],
        d["sld_entropy"],
        d["digit_ratio"],
        d["vowel_ratio"],
        d["consonant_max_run"],
        d["digit_max_run"],
        float(d["has_hyphen"]),
        d["special_char_count"],
        d["bigram_avg_freq"],
        d["trigram_avg_freq"],
        d["tld_risk_score"],
        float(d["is_punycode"]),
    ]


def extract_features_dict(domain: str) -> Dict:
    """Extract features as a named dictionary (for API responses)."""
    parsed = _parse_domain(domain)
    full = parsed["full"]
    sld = parsed["sld"]
    subdomain = parsed["subdomain"]
    tld = parsed["tld"]
    labels = parsed["labels"]
    
    # Only count alpha characters for vowel ratio
    alpha_chars = [c for c in sld if c.isalpha()]
    vowel_count = sum(1 for c in alpha_chars if c in VOWELS)
    
    return {
        "domain_length": len(full),
        "sld_length": len(sld),
        "subdomain_length": len(subdomain),
        "num_labels": len(labels),
        "shannon_entropy": round(shannon_entropy(full), 4),
        "sld_entropy": round(shannon_entropy(sld), 4),
        "digit_ratio": round(
            sum(1 for c in full if c.isdigit()) / max(len(full), 1), 4
        ),
        "vowel_ratio": round(
            vowel_count / max(len(alpha_chars), 1), 4
        ),
        "consonant_max_run": _max_consecutive_run(sld, CONSONANTS),
        "digit_max_run": _max_consecutive_run(full, set("0123456789")),
        "has_hyphen": "-" in full,
        "special_char_count": sum(
            1 for c in full if not c.isalnum() and c != "."
        ),
        "bigram_avg_freq": round(_avg_ngram_freq(sld, _ENGLISH_BIGRAMS, 2), 4),
        "trigram_avg_freq": round(_avg_ngram_freq(sld, _ENGLISH_TRIGRAMS, 3), 4),
        "tld_risk_score": 1.0 if tld in HIGH_RISK_TLDS else 0.0,
        "is_punycode": full.startswith("xn--") or any(
            label.startswith("xn--") for label in labels
        ),
    }
