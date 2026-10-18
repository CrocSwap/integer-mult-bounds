"""Independent closed traffic formulas; no production arithmetic imported.

Arham Tahir with OpenAI Codex assistance. Apache-2.0.
"""


def countdown(n, digits):
    """Constructor, n decrements and close, including reads of the source word."""
    if n < 0 or digits < max(1, n.bit_length()):
        raise ValueError("unsigned encoded countdown")
    return 15*n + 14*digits - 5*n.bit_count() + 36 if n else 14*digits + 40


def suffix_probe(s):
    if s <= 0:
        raise ValueError("positive suffix")
    return 4 if s % 2 == 0 else (12 if s % 4 == 3 else 15)


def total(m, b, s, width=None):
    """All logical read/write/move traffic from entry through successful return."""
    if m < 2 or b < 1 or s < 1:
        raise ValueError("complete positive sign fibre")
    width = m.bit_length()+1 if width is None else width
    if width < m.bit_length()+1:
        raise ValueError("word margin")
    db, ds = b.bit_length()+1, s.bit_length()+1
    v = b*m*s
    suffix_counters = 4*b*(m-2) + (b*m if s != 1 else 0)
    return {
        "numerical_setup_disposal": 68*width+107,
        "extent_validation": 4*(db+ds)+14,
        "payload": 9*v+4*b*(m-2)*s+10,
        "suffix_probes": b*m*suffix_probe(s),
        "countdowns": (countdown(b, db) + 2*b*countdown(m-2, width)
                       + b*countdown(m-1, width)
                       + suffix_counters*countdown(s, ds)),
    }
