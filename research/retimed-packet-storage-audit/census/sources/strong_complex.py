"""Bind the 48-call physical receiver to the 5,674-transfer source."""

from functools import cache
from fractions import Fraction
from types import SimpleNamespace
from hashlib import sha256
from pathlib import Path
import gzip
import json

WORD = "38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb"
LAYOUT = "0ce3f9e383fc4bfdd22612b9e34fc9759d97204215937b82d23aec2cedd9b8ee"
ADDITIONAL = "6ff19e063214b1698165d9da1fcd6182d9b837ac2d6e61aa71658b629aabbc95"
GRID = 154113755636630124932500335624192000
DYADIC = 30
ODD = GRID >> DYADIC


def digest(value):
    raw = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return sha256(raw).hexdigest()


def packed(path):
    return json.loads(gzip.decompress(path.read_bytes()))


@cache
def load_changed(data):
    """Reconstruct the 1,291-role program from the literal graph and its three journals."""
    import sys

    data = Path(data)
    source = data / "complex-source"
    for name, pin in json.loads((data / "complex-source.json").read_bytes()).items():
        if sha256((source / name).read_bytes()).hexdigest() != pin:
            raise ValueError(f"The circuit source differs at {name}")
    sys.path.insert(0, str(source))
    from verify_split_helpers import read, rebuild, reconstruct

    parent, layout = rebuild()
    graph, _ = reconstruct(parent, read("BANK-FACTORS.json.gz"))
    if digest(graph) != WORD or digest(layout) != LAYOUT:
        raise ValueError("The reconstructed Gaussian graph or its owner layout differs")
    return graph, layout


def required_pairs(graph, layout):
    main = (
        set(layout["live"])
        | {x + 112 for x in layout["live"]}
        | set(layout["hosted"]["X2"])
        | set(layout["hosted"]["Y2"])
    )
    helpers = {
        (a, b)
        for i, (a, b) in enumerate(zip(graph["initial"], graph["final"], strict=True))
        if i not in main
    }
    return helpers | {(a, b) for _, a, b in graph["moves"]}


def word(graph, layout):
    from powered import PoweredWord
    from tagged_sources import PINS, complex_ports, pinned
    import tagged_sources

    local = {
        key: pinned(key, PINS[key])
        for key in ("mixed_caller.py", "closed_caller.py", "data/CONJUGATE-CALLER.json.gz")
    }
    key = "data/CALLER.json.gz"
    caller = tagged_sources.packed(pinned(key, PINS[key]))
    raw = complex_ports(graph, layout, caller, local)
    return PoweredWord(153, raw.targets, raw.paid, 128, 16, 12, 12)


@cache
def artifacts(grade, data):
    """Construct every paid Clifford factor and true port from its signed frame."""
    from charts import native_catalogue
    from closed_caller import placement, templates
    from mixed_caller import instructions, layout_bindings
    from raw48 import contact, monomial, read_json

    graph, layout = load_changed(data)
    catalogue = native_catalogue(graph, layout)
    if digest(catalogue) != "8a9ff9558bf5fa3854699937fe063f98c86467d5d32a4488bfc878d2be081e70":
        raise ValueError("The generated all-column Clifford catalogue differs")
    tables = Path(grade) / "retained/data"
    bases = read_json(tables / "CALLER-PHASE-BASES.json")["by_q"]
    contacts = [contact(q, tuple(bases[str(q)])) for q in layout["ports"]]
    caller = read_json(tables / "CALLER.json.gz")
    words, roots = templates(caller), placement(caller)
    binds, offsets, census = layout_bindings(words, roots, layout, 48)
    hosted = layout["hosted"]
    pairs = dict(zip(hosted["Dports"], zip(hosted["X2"], hosted["Y2"], strict=True), strict=True))
    regs = [(x, x + 112) + pairs.get(i, ()) for i, x in enumerate(layout["live"])]
    return SimpleNamespace(
        graph=graph,
        layout=layout,
        contacts=contacts,
        words=words,
        roots=roots,
        offsets=offsets,
        instructions=lambda: instructions(words, roots, binds, offsets),
        binding_receipt=census,
        factors={
            (a, b): (r["rank"], monomial(r["right"]), monomial(r["left"]))
            for a, b, r in catalogue["pairs"]
        },
        port=[(monomial(left), monomial(right)) for _, left, right in catalogue["ports"]],
        regs=regs,
        main={n for row in regs for n in row},
        odd=ODD,
        moves={i: (a, b) for i, a, b in graph["moves"]},
        forms={i: tuple((j, Fraction(c)) for j, c in row) for i, row in graph["forms"]},
    )
