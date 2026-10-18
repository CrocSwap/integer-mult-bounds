#!/usr/bin/env python3
"""One fixed eight-corner composition experiment, no resynthesis. Apache-2.0.

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
Source circuits: PR980 (Davidson), PR1062 (Sagar Thakrar), and their credited
PR904/936/952/915/926/967/1015/923/589/555 predecessors.
"""
import argparse
import copy
from pathlib import Path
import runpy

C = runpy.run_path(str(Path(__file__).with_name("common.py")))


def cleanup(word):
    full = next(i for i, frame in enumerate(word["frames"]) if len(frame) == word["v"])
    v = word["v"]
    return [[full, d, list(ss)] for _, d, ss in reversed(word["A"] + word["B"])
            if d < v or d >= 2 * v]


def compose(baseline, a_word, bd_word, mask):
    C["need"](type(mask) is int and 0 <= mask < 8, "composition mask")
    word = copy.deepcopy(baseline)
    for flag, section, source in ((1, "A", a_word), (2, "B", bd_word), (4, "D", bd_word)):
        if mask & flag:
            word[section] = copy.deepcopy(source[section])
    word["C"] = cleanup(word)
    return word


def macro_bound(word, reverse=False):
    """Positive macro execution; verifier separately lowers explicit copies."""
    v = word["v"]
    values = [1] * (2 * v + word["R"])
    largest = 1
    phases = ("C", "B", "scatter", "A", "D") if reverse else ("D", "A", "scatter", "B", "C")
    for phase in phases:
        if phase == "scatter":
            for j in reversed(range(len(word["ret"]))) if reverse else range(len(word["ret"])):
                copied = values[word["ret"][j]]
                for i, sources in enumerate(word["scatter"]):
                    if j in sources:
                        values[v + i] += copied
                        largest = max(largest, values[v + i])
        else:
            for _, d, sources in reversed(word[phase]) if reverse else word[phase]:
                values[d] += sum(values[s] for s in sources)
                largest = max(largest, values[d])
    return largest


def price(word):
    f, b = macro_bound(word), macro_bound(word, True)
    sections = {s: sum(len(g[2]) for g in word[s]) for s in "DABC"}
    sections["scatter"] = sum(map(len, word["scatter"]))
    local, nine = 64 * f**3 * b**2, (1 << 18) * f**5 * b**4
    return dict(ADDs=sum(sections.values()), sections=sections, F=f, B=b,
                local_upper=str(local), nine_upper=str(nine),
                local_bits=local.bit_length(), nine_bits=nine.bit_length(),
                admitted=local < 1 << 104 and nine < 1 << 192)


def build(root):
    root = Path(root)
    baseline = C["load"](root / C["WORD"])
    a_word = C["load"](root / C["A_WORD"])
    bd_word = C["load"](C["HERE"] / C["BD_WORD"])
    # Historical assignment seed 13 fixes diagnostic order, not circuit search.
    order = sorted(range(8), key=lambda mask: mask ^ 13)
    words = {str(mask): compose(baseline, a_word, bd_word, mask) for mask in order}
    certificate = dict(format="r439-abc-star-composition/1", seed=13,
                       bit_order=["A_from_PR980", "B_from_PR1062", "D_from_PR1062"],
                       order=order, stopping_rule="all eight frozen subsets; no search or restart",
                       sources={"PR589": C["digest"](baseline), "PR980": C["digest"](a_word),
                                "PR1062": C["digest"](bd_word)},
                       corners={name: dict(sha256=C["digest"](word), **price(word))
                                for name, word in words.items()},
                       candidate_mask=7, new_kappa_claim=False)
    return words, certificate


def run(root, output):
    C["pins"](root)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    words, certificate = build(root)
    for name, word in words.items():
        C["write"](output / (name + ".json.gz"), word)
    C["write"](output / "CERTIFICATE.json", certificate)
    return words, certificate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    _, cert = run(args.source_root, args.output)
    print("COMPLETE", [(k, v["ADDs"], v["nine_bits"]) for k, v in cert["corners"].items()])
