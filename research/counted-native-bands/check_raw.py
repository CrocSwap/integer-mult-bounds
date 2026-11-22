"""Count the fixed rational reconstruction and regenerate the complete nine-axis atlas."""

from fractions import Fraction
from pathlib import Path
import sys

from upstream import HERE, install


def check():
    _, _, _, src = install()
    from strong_binary import native_word
    from strong_complex import artifacts, load_changed, word

    data = HERE / "inputs"
    terms = height = 0
    fraction_file = sys.modules["fractions"].__file__

    def audit(frame, event, result):
        nonlocal terms, height
        if event == "return" and frame.f_code.co_filename == fraction_file and isinstance(result, Fraction):
            terms += 1
            height = max(height, result.numerator.bit_length(), result.denominator.bit_length())

    sys.setprofile(audit)
    try:
        graph, layout = load_changed(data)
    finally:
        sys.setprofile(None)
    atlas = artifacts(src / "research/grade14-native-realization", data)
    bit, positive = native_word(128), word(graph, layout)
    assert (len(bit.targets), len(bit.paid)) == (18906,104904)
    assert (len(positive.targets), len(positive.paid)) == (52608,281568)
    assert len(atlas.factors) == 2971 and len(atlas.port) == 104
    assert len(graph["schedule"]) == 6965 and len(graph["initial"]) == 1291
    assert sum(len(row) for row in atlas.forms.values()) == 323573
    assert max(max(len(left),len(right)) for _, left, right in atlas.factors.values()) < 128
    assert 0 < height <= 512 and 0 < terms <= 2**36
    return terms, height, len(atlas.factors), len(atlas.port)


if __name__ == "__main__":
    print("journal rational returns, largest binary width, paid pairs and ports", *check(), flush=True)
