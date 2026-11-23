"""Validate the installed Clifford atlas against the independent chart verifier."""

import json
from pathlib import Path
import sys


def audit(runtime):
    sys.path.insert(0, str(runtime))
    from upstream import install

    paths = install()
    from strong_complex import digest, load_changed, required_pairs
    from phase_atlas import catalogue
    from charts import native_catalogue
    from check_complex import all_images
    from contacts import contact_receipt

    data = runtime / "inputs"
    graph, layout = load_changed(data)
    current = catalogue(graph, layout)
    assert (
        digest(current)
        == "f581128079a67c9fc6341ee96dce772342748f508c77f7d5956bf41408d97f58"
    )
    assert {(a, b) for a, b, _ in current["pairs"]} == required_pairs(graph, layout)
    checked = native_catalogue(graph, layout, current)
    images = all_images(checked)
    grade = paths[-1] / "research/grade14-native-realization"
    contacts = contact_receipt(
        layout,
        json.loads((grade / "retained/data/CALLER-PHASE-BASES.json").read_bytes())[
            "by_q"
        ],
    )
    return dict(
        atlas_sha256=digest(current),
        pairs=len(current["pairs"]),
        ports=len(current["ports"]),
        images=images,
        contacts=contacts,
    )


if __name__ == "__main__":
    if not __debug__:
        raise ValueError("Enable assertions")
    print(json.dumps(audit(Path(sys.argv[1]).resolve()), sort_keys=True))
