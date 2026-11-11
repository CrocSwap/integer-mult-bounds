#!/usr/bin/env python3
"""Opcode 1's chart images of the 112 dimension-8 Y exits.

The round-three word and the contact-graph span are predecessor inputs.
This checker recomputes every image. It does not trust the certificate
lines in PROOF.md until they match that recomputation. Failures raise
ValueError, including under python -O.
"""

from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WORD = ROOT / "research/sol1337-contact-frontier/inputs/round3-native.json.gz"
MODEL = ROOT / "research/sol1337-contact-frontier/vendor/model.py"
ENGINE = ROOT / "research/sol1337-contact-frontier/vendor/retained_verify.py"
SELECTED = ROOT / "certificates/selected-result.json"
SELECTED_KAPPA = "363005817/100000000000"
OPCODE_1_COLUMNS = (1, 2, 4, 8, 64, 19, 104, 197, 325)
AMBIENT = 9
SPACE = 1 << AMBIENT


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(engine):
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    by_path = {row["path"]: row for row in pins["files"]}
    for path in (WORD, MODEL, ENGINE, SELECTED):
        rel = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == by_path[rel]["sha256"], "changed input " + rel)
    raw = WORD.read_bytes()
    need(sha256(raw).hexdigest() == engine.SOURCE_HASH, "word hash disagrees with the retained emitter")
    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    need(selected["kappa"] == SELECTED_KAPPA, "selected frontier value moved")
    return json.loads(gzip.decompress(raw))


def bijective(model, cols):
    need(len(cols) == AMBIENT, "opcode 1 has nine columns")
    need(all(type(column) is int and 0 <= column < SPACE for column in cols),
         "opcode 1 columns lie in GF(2)^9")
    need(model.mv(cols, 0) == 0, "a linear map sends 0 to 0")
    for vector in range(SPACE):
        for bit in range(AMBIENT):
            axis = 1 << bit
            need(model.mv(cols, vector ^ axis) == model.mv(cols, vector) ^ model.mv(cols, axis),
                 "opcode 1 is additive")
    images = {model.mv(cols, vector) for vector in range(SPACE)}
    return len(images) == SPACE


def proof_certificate():
    """The claimed partition, stated as certificate lines in PROOF.md."""
    fixed, y_to_y, non_y = [], [], []
    unrecorded = None
    for line in (HERE / "PROOF.md").read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if not parts or parts[0] != "certificate":
            continue
        kind = parts[1]
        fields = dict(item.split("=", 1) for item in parts[2:])
        if kind == "fixed":
            fixed.append((int(fields["role"]), int(fields["source"])))
        elif kind == "y-to-y":
            y_to_y.append((int(fields["role"]), int(fields["source"]), int(fields["dest"])))
        elif kind == "non-y":
            non_y.append((int(fields["role"]), int(fields["source"]), int(fields["dest"])))
        elif kind == "unrecorded":
            need(unrecorded is None, "one unrecorded count")
            unrecorded = int(fields["count"])
        else:
            raise ValueError("unknown certificate line")
    need(unrecorded is not None, "PROOF.md states the unrecorded count")
    need(len(fixed) == 4 and len(y_to_y) == 24 and len(non_y) == 11, "certificate class sizes")
    need(unrecorded == 73, "certificate unrecorded count")
    need(len(fixed) + len(y_to_y) + len(non_y) + unrecorded == 112, "certificate covers 112 exits")
    return fixed, y_to_y, non_y, unrecorded


def classify(model, frames, dim8_index, cols, chart):
    image = model.span(model.mv(cols, vector) for vector in frames[chart])
    need(len(image) == 256, "an automorphism preserves Y-exit dimension")
    targets = dim8_index.get(frozenset(image), [])
    need(len(targets) <= 1, "dimension-8 chart spans are unique")
    return image, (targets[0] if targets else None)


def survey(model, payload):
    canonical = payload["canonical"]
    frames = canonical["frames"]
    final = canonical["final"]
    start = canonical["start"]
    need(canonical["h"] == AMBIENT and canonical["v"] == 112, "ambient dimension and block length")
    need(len(frames) == 4429, "recorded chart count")
    need(len(final) == len(start) == 632, "632 role charts")
    record = canonical["warps"][0]
    cols = tuple(record["G_columns"])
    need(record["op"] == 1 and cols == OPCODE_1_COLUMNS, "opcode 1 keeps its recorded columns")
    need(bijective(model, cols), "opcode 1 is a linear automorphism")

    spans = []
    for basis in frames:
        for vector in basis:
            need(type(vector) is int and 0 <= vector < SPACE, "every chart vector lies in GF(2)^9")
        space = model.span(basis)
        need(len(space) == 1 << len(basis), "chart dimension is the independent basis length")
        spans.append(space)
    full = [index for index, basis in enumerate(frames) if len(basis) == AMBIENT]
    need(full == [1] and spans[1] == set(range(SPACE)), "frame 1 is the whole space")

    y_ids = [final[role] for role in range(112, 224)]
    need(y_ids == list(range(142, 254)), "Y exits are frames 142 through 253 in role order")
    need(len(set(y_ids)) == 112, "112 distinct Y-exit charts")
    y_set = set(y_ids)
    for chart in y_ids:
        need(len(frames[chart]) == 8 and spans[chart] < spans[1], "every Y exit is a strict dimension-8 subspace")

    dim8_index = {}
    for index, basis in enumerate(frames):
        if len(basis) != 8:
            continue
        key = frozenset(spans[index])
        need(key not in dim8_index, "two dimension-8 charts share a span")
        dim8_index[key] = [index]
    need(len(dim8_index) == 162, "162 recorded dimension-8 charts")

    fixed, y_to_y, non_y, unrecorded = [], [], [], []
    for role, chart in enumerate(y_ids, start=112):
        image, dest = classify(model, frames, dim8_index, cols, chart)
        need(image != spans[1], "opcode 1 does not carry a Y exit onto frame 1")
        if dest is None:
            unrecorded.append(role)
            continue
        need(len(frames[dest]) == 8 and spans[dest] == image, "a hit is span equality with one dimension-8 chart")
        if dest == chart:
            fixed.append((role, chart))
        elif dest in y_set:
            y_to_y.append((role, chart, dest))
        else:
            need(dest not in y_set, "non-Y destination")
            need(dest not in start and dest not in final, "non-Y image is not a role start or final chart")
            non_y.append((role, chart, dest))
    need(len(fixed) + len(y_to_y) + len(non_y) + len(unrecorded) == 112, "every Y exit is classified once")
    return {
        "cols": cols,
        "frames": frames,
        "spans": spans,
        "y_ids": y_ids,
        "fixed": fixed,
        "y_to_y": y_to_y,
        "non_y": non_y,
        "unrecorded": unrecorded,
    }


def expect_fail(fn, message):
    try:
        fn()
    except ValueError:
        return
    raise ValueError(message)


def controls(model, facts):
    frames = facts["frames"]
    spans = facts["spans"]
    cols = facts["cols"]
    damaged = list(cols)
    damaged[0] = 0
    need(not bijective(model, tuple(damaged)), "zeroing one column of opcode 1 destroys bijectivity")

    role112 = facts["y_ids"][0]
    need(role112 == 142, "role 112 uses frame 142")
    image = model.span(model.mv(cols, vector) for vector in frames[142])
    for chart in facts["y_ids"]:
        need(image != spans[chart], "opcode 1 does not carry role 112 onto a Y-exit chart")
    need(len(image) == 256 and image != spans[1], "role 112 still has an 8-dimensional image")

    def short_domain():
        need(len(facts["y_ids"][:-1]) == 112, "111 exits are not the census")

    expect_fail(short_domain, "dropping one Y exit is not this census")

    def false_peer():
        need(image == spans[143], "role 112 image is frame 143")

    expect_fail(false_peer, "role 112 does not land on the next Y-exit chart")

    moved = [row for row in facts["y_to_y"] if row[1] == 146]
    need(moved == [(116, 146, 147)], "role 116 is the recorded move from frame 146 to frame 147")

    def fixed_reading():
        need(spans[146] == model.span(model.mv(cols, vector) for vector in frames[146]),
             "frame 146 is fixed")

    expect_fail(fixed_reading, "equal dimension does not make frame 146 a fixed chart")


def main():
    engine = load_module(ENGINE, "retained_centre_verify")
    model = load_module(MODEL, "contact_graph_model")
    payload = authenticate(engine)
    facts = survey(model, payload)
    claimed_fixed, claimed_y, claimed_non_y, claimed_unrecorded = proof_certificate()
    need(facts["fixed"] == claimed_fixed, "fixed charts disagree with PROOF.md")
    need(facts["y_to_y"] == claimed_y, "Y-to-Y images disagree with PROOF.md")
    need(facts["non_y"] == claimed_non_y, "non-Y images disagree with PROOF.md")
    named = {row[0] for row in facts["fixed"] + facts["y_to_y"] + facts["non_y"]}
    need(named.isdisjoint(facts["unrecorded"]), "a role is not in two classes")
    need(named | set(facts["unrecorded"]) == set(range(112, 224)), "the classes partition the 112 roles")
    need(len(facts["unrecorded"]) == claimed_unrecorded, "unrecorded count disagrees with PROOF.md")
    controls(model, facts)
    print(
        "PASS_OPCODE1_Y_EXIT_CHART_IMAGE "
        "y_exits=112 recorded_dim8_charts=162 "
        "fixed=4 y_to_y=24 non_y=11 unrecorded=73 "
        "role112_chart=142 role112_recorded_dim8_image=none "
        "frame1_admitted=0 "
        "selected_kappa=363005817/100000000000 no_new_kappa=true "
        "evidence_class=exhaustive_finite_census"
    )


if __name__ == "__main__":
    main()
