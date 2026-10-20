"""Exact positive-price envelope for the fixed five-source F2 connector.

Produced by Nick Petalas. Apache-2.0.
The prefix contract and twelve-toggle template are Ross Richardson's PR943.
"""

from fractions import Fraction
from itertools import combinations


ELIGIBLE_OUTPUTS = tuple(m for m in range(1, 32) if m.bit_count() in (3, 5))
EXTRA_SOURCE = (2, 0, 2, 1, 2, 0, 3, 1, 4, 2, 3, 4)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical_words():
    """Restricted-growth words: ten layers, five labels, two of each."""
    layer = [((), (0,) * 5, 0)]
    for _ in range(10):
        following = []
        for word, counts, used in layer:
            for label in range(min(5, used + 1)):
                if counts[label] == 2:
                    continue
                updated = list(counts)
                updated[label] += 1
                following.append((word + (label,), tuple(updated), max(used, label + 1)))
        layer = following
    return tuple(word for word, _, _ in layer)


def prefixes(word):
    require(len(word) in (10, 12), "source length must be ten or twelve")
    require(all(type(j) is int and 0 <= j < 5 for j in word), "source label")
    states = [0]
    for label in word:
        states.append(states[-1] ^ (1 << label))
    require(states[-1] == 0, "source path must restore the connector")
    return tuple(states)


def pair_choices(states):
    choices = {}
    for left, right in combinations(range(len(states)), 2):
        choices.setdefault(states[left] ^ states[right], (left, right))
    return choices


def make_schedule(source_word):
    """Put each output's two or four readouts at selected prefix boundaries."""
    states = prefixes(source_word)
    choices = pair_choices(states)
    for mask in range(1, 32):
        if mask in choices:
            continue
        for slots in combinations(range(len(states)), 4):
            value = 0
            for slot in slots:
                value ^= states[slot]
            if value == mask:
                choices[mask] = slots
                break
        require(mask in choices, "four-readout representation unavailable")
    word = []
    for boundary in range(len(states)):
        for mask in range(1, 32):
            if boundary in choices[mask]:
                word.append(("A", mask))
        if boundary < len(source_word):
            word.append(("B", source_word[boundary]))
    return tuple(word)


def relabel(word, source_mask, target_mask):
    require(source_mask.bit_count() == target_mask.bit_count(), "mask weights differ")
    old = [j for j in range(5) if source_mask >> j & 1]
    old += [j for j in range(5) if not source_mask >> j & 1]
    new = [j for j in range(5) if target_mask >> j & 1]
    new += [j for j in range(5) if not target_mask >> j & 1]
    labels = dict(zip(old, new, strict=True))
    return tuple(labels[j] for j in word)


def schedules():
    templates = {}
    for word in canonical_words():
        available = pair_choices(prefixes(word))
        missing = tuple(m for m in range(1, 32) if m not in available)
        if len(missing) == 1:
            templates.setdefault(missing[0].bit_count(), (word, missing[0]))
    require(set(templates) == {3, 5}, "sole-omission template classes changed")
    result = {}
    for label in range(5):
        word = tuple(label if j == 2 else 2 if j == label else j for j in EXTRA_SOURCE)
        result[f"B{label}"] = make_schedule(word)
    for mask in ELIGIBLE_OUTPUTS:
        template, old_mask = templates[mask.bit_count()]
        result[f"A{mask}"] = make_schedule(relabel(template, old_mask, mask))
    return result


def prices(source_prices, output_prices):
    require(len(source_prices) == 5 and len(output_prices) == 31, "price dimensions")
    values = tuple(source_prices) + tuple(output_prices)
    require(all(type(v) in (int, Fraction) and v > 0 for v in values),
            "prices must be positive exact integers or Fractions")
    return values


def optimum(source_prices, output_prices):
    values = prices(source_prices, output_prices)
    candidates = [(values[j], f"B{j}") for j in range(5)]
    candidates += [(values[4 + m], f"A{m}") for m in ELIGIBLE_OUTPUTS]
    cheapest, repeat = min(candidates)
    return 2 * sum(values) + 2 * cheapest, repeat


def invoice(word, source_prices, output_prices):
    values = prices(source_prices, output_prices)
    result = 0
    require(len(word) <= 74, "only retained witnesses are priced")
    for kind, index in word:
        require(kind in ("A", "B") and type(index) is int, "operator record")
        require(0 <= index < 5 if kind == "B" else 1 <= index <= 31, "operator index")
        result += values[index if kind == "B" else 4 + index]
    return result
