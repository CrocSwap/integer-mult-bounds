#!/usr/bin/env python3
"""No retained warp opcode in the #7102 alphabet changes chart dimension.

The round-three word, the retained emitter, and the contact-graph model are
predecessor inputs. This checker recomputes the opcode census. It does not
trust the counts in PROOF.md as inputs. Failures raise ValueError, including
under python -O.
"""

from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WORD = ROOT / "research/sol1337-contact-frontier/inputs/round3-native.json.gz"
ENGINE = ROOT / "research/sol1337-contact-frontier/vendor/retained_verify.py"
MODEL = ROOT / "research/sol1337-contact-frontier/vendor/model.py"
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
    for path in (WORD, ENGINE, MODEL, SELECTED):
        rel = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == by_path[rel]["sha256"], "changed input " + rel)
    raw = WORD.read_bytes()
    need(sha256(raw).hexdigest() == engine.SOURCE_HASH, "word hash disagrees with the retained emitter")
    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    need(selected["kappa"] == SELECTED_KAPPA, "selected frontier value moved")
    return json.loads(gzip.decompress(raw))


def mv(cols, vector):
    image = 0
    for index, column in enumerate(cols):
        if (vector >> index) & 1:
            image ^= column
    return image


def span(basis):
    out = {0}
    for vector in basis:
        out |= {point ^ vector for point in tuple(out)}
    return out


def vector_rank(vectors):
    pivots = {}
    for vector in vectors:
        value = vector
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def prove_linear(cols):
    """Column action is additive on GF(2)^9, hence linear."""
    need(len(cols) == AMBIENT, "a retained opcode has nine columns")
    need(all(type(column) is int and 0 <= column < SPACE for column in cols),
         "columns lie in GF(2)^9")
    need(mv(cols, 0) == 0, "linear maps send 0 to 0")
    for vector in range(SPACE):
        for bit in range(AMBIENT):
            axis = 1 << bit
            need(mv(cols, vector ^ axis) == mv(cols, vector) ^ mv(cols, axis),
                 "column action is additive")


def bijective(cols):
    prove_linear(cols)
    images = {mv(cols, vector) for vector in range(SPACE)}
    return len(images) == SPACE and vector_rank(cols) == AMBIENT


def inverse_columns(cols):
    values = {mv(cols, vector): vector for vector in range(SPACE)}
    need(len(values) == SPACE, "inverse is defined only for a bijective map")
    return [values[1 << bit] for bit in range(AMBIENT)]


def require_two_sided_inverse(cols, inverse):
    identity = [1 << bit for bit in range(AMBIENT)]
    need([mv(cols, column) for column in inverse] == identity, "G inverse is a right inverse")
    need([mv(inverse, column) for column in cols] == identity, "G inverse is a left inverse")


def chart_image(cols, source, dest):
    """Native chart-image law: G carries the source span onto the destination span."""
    need(bijective(cols), "chart-image law is stated for a retained bijective opcode")
    return span(mv(cols, vector) for vector in source) == span(dest)


def require_alphabet(warps):
    ops = [record["op"] for record in warps]
    need(ops == list(range(1, 73)), "recorded alphabet is exactly opcodes 1 through 72")


def expect_fail(fn, message):
    try:
        fn()
    except ValueError:
        return
    raise ValueError(message)


def survey(model, payload):
    canonical = payload["canonical"]
    frames = canonical["frames"]
    need(canonical["h"] == AMBIENT and canonical["v"] == 112, "ambient dimension and block length")
    need(len(frames) == 4429, "recorded chart count")
    for basis in frames:
        for vector in basis:
            need(type(vector) is int and 0 <= vector < SPACE, "every chart vector lies in GF(2)^9")
        need(len(span(basis)) == 1 << len(basis), "chart dimension is the independent basis length")
        need(span(basis) == model.span(basis), "span agrees with the contact-graph model")

    warps = canonical["warps"]
    require_alphabet(warps)
    endpoint_dims = {}
    for record in warps:
        opcode = record["op"]
        cols = tuple(record["G_columns"])
        source_id = record["from_frame"]
        dest_id = record["to_frame"]
        need(0 <= source_id < len(frames) and 0 <= dest_id < len(frames), "opcode endpoints are charts")
        need(bijective(cols), "retained opcode is a linear automorphism")
        inverse = inverse_columns(cols)
        need(inverse == model.inv(list(cols)), "inverse agrees with model.inv")
        require_two_sided_inverse(cols, inverse)
        need(bijective(inverse), "retained inverse opcode is a linear automorphism")
        source = frames[source_id]
        dest = frames[dest_id]
        need(chart_image(cols, source, dest), "recorded source chart maps onto the recorded destination")
        need(chart_image(inverse, dest, source), "inverse carries the destination back onto the source")
        need(len(source) == len(dest), "recorded endpoints have equal dimension")
        image = span(mv(cols, vector) for vector in source)
        image_mask = model.mask(image)
        dest_mask = model.mask(span(dest))
        need(model.fourier_rank(image_mask, dest_mask) == 0, "monomial chart image has Fourier rank 0")
        endpoint_dims[len(source)] = endpoint_dims.get(len(source), 0) + 1
        if opcode == 1:
            need(cols == OPCODE_1_COLUMNS, "opcode 1 keeps its recorded columns")
            need(source_id == 292 and dest_id == 293, "opcode 1 joins frames 292 and 293")
            need(len(source) == 4 and len(dest) == 4, "opcode 1 preserves dimension 4")
            separation = model.fourier_rank(model.mask(span(source)), model.mask(span(dest)))
            need(separation == 4, "opcode 1 moves between two distinct dimension-4 charts")

    need(endpoint_dims == {4: 50, 5: 22}, "recorded endpoint dimensions")
    full = [index for index, basis in enumerate(frames) if len(basis) == AMBIENT]
    need(full == [1], "frame 1 is the unique dimension-9 chart")
    need(span(frames[1]) == set(range(SPACE)), "frame 1 is the whole 9-bit space")
    final = canonical["final"]
    y_ids = [final[role] for role in range(112, 224)]
    need(len(set(y_ids)) == 112, "112 distinct Y-exit charts")
    for chart in y_ids:
        basis = frames[chart]
        need(len(basis) == 8, "every Y exit has dimension 8")
        need(span(basis) < span(frames[1]), "every Y exit sits strictly inside frame 1")
        gap = model.fourier_rank(model.mask(span(basis)), model.mask(span(frames[1])))
        need(gap == 1, "the frame-1 gap of a Y exit has Fourier rank 1")

    full_span = span(frames[1])
    full_mask = model.mask(full_span)
    for record in warps:
        cols = tuple(record["G_columns"])
        inverse = inverse_columns(cols)
        for chart in y_ids:
            basis = frames[chart]
            for signed in (cols, inverse):
                images = [mv(signed, vector) for vector in basis]
                image_span = span(images)
                need(vector_rank(images) == 8, "a retained opcode preserves Y-exit dimension")
                need(image_span != full_span, "image of a Y exit is not frame 1")
                need(model.fourier_rank(model.mask(image_span), full_mask) == 1,
                     "Y-exit image against frame 1 keeps Fourier rank 1")

    # One explicit composition. Bijectivity of every factor implies the rest.
    first = tuple(warps[0]["G_columns"])
    second = tuple(warps[1]["G_columns"])
    composed = [mv(first, mv(second, 1 << bit)) for bit in range(AMBIENT)]
    need(bijective(composed), "a product of retained opcodes stays bijective")
    y_basis = frames[y_ids[0]]
    need(vector_rank(mv(composed, vector) for vector in y_basis) == 8,
         "a product preserves Y-exit dimension")

    emitted = [event for event in payload["programs"]["forward"] if event[0] == "warp"]
    need(len(emitted) == 240, "the word emits 240 warps")
    by_op = {record["op"]: record for record in warps}
    on_record = 0
    source_dims = {}
    off_record_dims = {}
    edge_classes = set()
    for event in emitted:
        need(len(event) == 5 and event[1][0] == "L", "emitted warp shape")
        opcode = event[2]
        source_id, dest_id = event[3], event[4]
        need(type(opcode) is int and 1 <= abs(opcode) <= 72, "emitted opcode is a retained sign")
        record = by_op[abs(opcode)]
        cols = tuple(record["G_columns"])
        signed = cols if opcode > 0 else inverse_columns(cols)
        source = frames[source_id]
        dest = frames[dest_id]
        need(len(source) == len(dest), "emitted warp preserves dimension")
        need(chart_image(signed, source, dest), "emitted warp is a chart image of its opcode")
        source_dims[len(source)] = source_dims.get(len(source), 0) + 1
        recorded_source = record["from_frame"]
        recorded_dest = record["to_frame"]
        if opcode < 0:
            recorded_source, recorded_dest = recorded_dest, recorded_source
        if (source_id, dest_id) == (recorded_source, recorded_dest):
            on_record += 1
        else:
            off_record_dims[len(source)] = off_record_dims.get(len(source), 0) + 1
        edge_classes.add((1 if opcode > 0 else -1, abs(opcode), source_id, dest_id))
    need(on_record == 72 and len(emitted) - on_record == 168,
         "72 emitted warps use the recorded endpoints and 168 use other charts")
    need(off_record_dims == {0: 72, 1: 24, 9: 72},
         "off-endpoint uses sit at dimensions 0, 1, and 9")
    need(source_dims == {0: 72, 1: 24, 4: 50, 5: 22, 9: 72},
         "emitted warps never meet dimension 8")
    need(8 not in source_dims, "no emitted warp has dimension 8")
    recorded_edges = {tuple(edge) for edge in canonical["warp_edges"]}
    need(recorded_edges == edge_classes and len(recorded_edges) == 180,
         "warp_edges is exactly the 180 emitted classes")
    for sign, opcode, source_id, dest_id in recorded_edges:
        need(sign in (1, -1) and 1 <= opcode <= 72, "warp edge names a retained opcode")
        need(len(frames[source_id]) == len(frames[dest_id]), "every recorded warp class preserves dimension")

    return {"y_ids": y_ids}


def controls(payload, facts):
    frames = payload["canonical"]["frames"]
    warps = payload["canonical"]["warps"]
    cols = list(warps[0]["G_columns"])
    damaged = list(cols)
    damaged[0] = 0
    need(not bijective(damaged), "zeroing one column of opcode 1 destroys bijectivity")

    def short_alphabet():
        require_alphabet(warps[:-1])

    expect_fail(short_alphabet, "dropping opcode 72 is not a census of the alphabet")

    y_basis = frames[facts["y_ids"][0]]
    frame_one = frames[1]

    def y_to_frame_one():
        need(chart_image(tuple(cols), y_basis, frame_one), "opcode 1 image")

    expect_fail(y_to_frame_one, "opcode 1 does not carry a Y exit onto frame 1")

    image = span(mv(tuple(cols), vector) for vector in frames[292])
    rejected_peer = None
    for index, basis in enumerate(frames):
        if len(basis) == 4 and span(basis) != image:
            rejected_peer = index
            break
    need(rejected_peer is not None, "some dimension-4 chart is outside opcode 1's image")

    def wrong_peer():
        need(chart_image(tuple(cols), frames[292], frames[rejected_peer]), "false peer")

    expect_fail(wrong_peer, "equal dimension alone does not admit a chart pair")

    def ten_events():
        sample = [event[2] for event in payload["programs"]["forward"] if event[0] == "warp"][:10]
        need(set(sample) == set(range(1, 73)), "ten emitted opcodes are the whole alphabet")

    expect_fail(ten_events, "ten emitted warps do not cover the opcode alphabet")

    def zero_gap():
        need(abs(len(y_basis) - len(frame_one)) == 0, "dimension gap")

    expect_fail(zero_gap, "the Y-exit gap is one dimension, so it is not a preserved pair")


def main():
    engine = load_module(ENGINE, "retained_centre_verify")
    model = load_module(MODEL, "contact_graph_model")
    payload = authenticate(engine)
    facts = survey(model, payload)
    controls(payload, facts)
    print(
        "PASS_RETAINED_WARP_OPCODE_DIMENSION "
        "opcodes=72 inverses=72 bijective=72 "
        "recorded_endpoint_dims=4:50,5:22 dimension_changing_opcodes=0 "
        "opcode_1=292->293 dim=4 chart_fourier_rank=4 "
        "y_exit_to_frame1_admitted=0 "
        "composition_preserves_dimension=true "
        "emitted_warps=240 emitted_dimension_changing=0 "
        "emitted_on_recorded_endpoints=72 emitted_on_other_charts=168 "
        "emitted_source_dims=0:72,1:24,4:50,5:22,9:72 "
        "warp_edge_classes=180 "
        "selected_kappa=363005817/100000000000 no_new_kappa=true "
        "evidence_class=proof_plus_exhaustive_census"
    )


if __name__ == "__main__":
    main()
