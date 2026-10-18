#!/usr/bin/env python3
"""Independent exact operator audit of PR2443's retained QQ16 cut decoder.

No predecessor executable is imported. Formal input variables carry exact
affine owner/payload operators; coefficients are rational. Apache-2.0.
By ywz65 with substantial OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
U = tuple(p for p in range(112) if p not in A + T)
J = (1, 2, 3, 4, 5, 6, 8, 12)
S = tuple(p for p in U if p not in J)
E = tuple(1 << i for i in range(73))
MEMBERS = {
    "slots/local/CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "slots/local/LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    "t16/global/base/work/complex-nine-native/DATA-PHASES.json": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz": "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518",
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def source_bytes(root=ROOT):
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    result = {}
    for item in pins["files"]:
        if item["usage"] == "input":
            raw = (root / item["path"]).read_bytes()
            need(digest(raw) == item["sha256"], "source hash: " + item["path"])
            result[item["path"]] = raw
    return result


def act(columns, vector):
    out = 0
    while vector:
        bit = vector & -vector
        out ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return out


MAPS = [(E, 0)]
MAP_IDS = {MAPS[0]: 0}


def intern(columns, shift=0):
    pair = (tuple(columns), shift)
    if pair not in MAP_IDS:
        MAP_IDS[pair] = len(MAPS)
        MAPS.append(pair)
    return MAP_IDS[pair]


@lru_cache(None)
def compose(left, right):
    g, a = MAPS[left]
    h, b = MAPS[right]
    return intern(tuple(act(g, c) for c in h), a ^ act(g, b))


@lru_cache(None)
def undo(index):
    g, a = MAPS[index]
    gt = tuple(sum(((g[j] >> i) & 1) << j for j in range(73)) for i in range(73))
    result = intern(gt, act(gt, a))
    need(compose(index, result) == compose(result, index) == 0, "orthogonal affine inverse")
    return result


def combine(*weighted_rows):
    out = {}
    for coefficient, row in weighted_rows:
        if coefficient:
            for key, value in row.items():
                out[key] = out.get(key, Q(0)) + coefficient * value
    return {key: value for key, value in out.items() if value}


def moved(index, row):
    out = {}
    for (variable, old), value in row.items():
        key = (variable, compose(index, old))
        out[key] = out.get(key, Q(0)) + value
    return {key: value for key, value in out.items() if value}


def variable(index):
    return {(index, 0): Q(1)}


def inverse(matrix):
    n = len(matrix)
    rows = [[Q(x) for x in row] + [Q(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        need(pivot is not None, "singular minor")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [v / scale for v in rows[j]]
        for i in range(n):
            if i != j:
                scale = rows[i][j]
                rows[i] = [v - scale * w for v, w in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def matmul(a, b):
    return [[sum((x * y for x, y in zip(row, col)), Q(0)) for col in zip(*b)] for row in a]


def parse_sources(raw):
    packet = json.loads(gzip.decompress(raw["research/joint-query/certificate.json.gz"]))
    archive_raw = raw["research/community-frontier1042-audit/selected-replay.tar.gz"]
    decoded = {}
    with tarfile.open(fileobj=io.BytesIO(archive_raw), mode="r:gz") as archive:
        for name, pin in MEMBERS.items():
            entries = [m for m in archive.getmembers() if m.name == name]
            need(len(entries) == 1 and entries[0].isfile(), "unique archive member")
            data = archive.extractfile(entries[0]).read()
            need(digest(data) == pin, "member hash: " + name)
            decoded[name.rsplit("/", 1)[-1]] = json.loads(gzip.decompress(data) if name.endswith("gz") else data)
    word, programs = decoded["CANONICAL-WORD.json.gz"], decoded["LOCAL-PROGRAMS.json.gz"]
    need((word["v"], 2 * word["v"] + word["R"]) == (112, 704), "source geometry")
    # Reconstruct R directly from the retained scalar prefix; no QQ16 loader.
    registers = [variable(i) for i in range(712)]
    for event in programs["forward"]:
        if event == ["phase", "centers"]:
            break
        if event[0] != "scalar":
            continue
        op = event[1]
        at = op[1][1] + (704 if op[1][0] == "C" else 0)
        if op[0] == "clear":
            registers[at] = {}
        elif op[0] == "scale":
            registers[at] = combine((Q(op[2], op[3]), registers[at]))
        else:
            src = op[2][1] + (704 if op[2][0] == "C" else 0)
            need(op[0] in ("copy", "add"), "known scalar prefix operation")
            registers[at] = dict(registers[src]) if op[0] == "copy" else combine(
                (1, registers[at]), (Q(op[3], op[4]), registers[src]))
    else:
        raise ValueError("missing centre boundary")
    R = [[registers[c].get((p, 0), Q(0)) for p in range(112)] for c in word["centers"]]
    need(R == [[Q(row.get(str(p), 0)) for p in range(112)] for row in packet["R_rows"]], "source-derived R")
    need(tuple(packet["A_ports"]) == A and tuple(packet["T_ports"]) == T and tuple(packet["U_ports"]) == U, "partitions")
    need(all(Q(packet["K_rows"][p].get(str(i), 0)) == R[i][p] / 4 for p in range(112) for i in range(8)), "source K")
    need(decoded["GLOBAL-TEMPLATE.json.gz"]["recipe"][:2] == [
        {"kind": "local", "pair": 0, "reverse": False, "stage": 0},
        {"kind": "local", "pair": 0, "reverse": True, "stage": 1}], "consecutive pair-zero F0 B1")
    phases, program = decoded["DATA-PHASES.json"], packet["programs"]["B_1_2"]
    routes, native, bindings = {}, {}, []
    for p, recipe in enumerate(phases["recipes"]):
        need(recipe["port"] == p, "source port identity")
        basis = recipe["idle_children"][0]["orthogonal_axes"][:8]
        maps = [e[2] for e in program if e[0] == "cover_map" and e[1] == ["L", 112 + p]]
        need(len(maps) == 4, "four Y alignments")
        for stage, offset in ((2, 0), (1, 2)):
            swaps = [b ^ (1 << (9 + 8 * (stage - 1) + i)) for i, b in enumerate(basis)]
            columns = tuple(e ^ act(swaps, sum(((e & s).bit_count() % 2) << i for i, s in enumerate(swaps))) for e in E)
            beta = sum((((b.bit_count() - 1) // 2) % 2) << (9 + 8 * (stage - 1) + i) for i, b in enumerate(basis))
            shift = recipe["q"] ^ beta
            entry = packet["map_registry"][maps[offset]]
            back = packet["map_registry"][maps[offset + 1]]
            need(tuple(entry["owner_right_matrix_columns"]) == columns, "route from phase geometry")
            need(entry["payload_translation_at_identity_owner"] == shift, "native entry translation")
            native[stage, p] = intern(columns, shift)
            need(undo(native[stage, p]) == intern(back["owner_right_matrix_columns"], back["payload_translation_at_identity_owner"]), "registered native inverse")
            routes[stage, p] = intern(columns)
            bindings.append([stage, p, maps[offset], maps[offset + 1]])
    return R, routes, native, bindings


class Model:
    def __init__(self, R, routes, native):
        self.R, self.routes, self.native = R, routes, native
        self.minor = [[row[p] for p in J] for row in R]
        self.dual = inverse(self.minor)
        identity = [[Q(i == j) for j in range(8)] for i in range(8)]
        need(matmul(self.minor, self.dual) == matmul(self.dual, self.minor) == identity, "both minor inverse orders")
        for ports, scale in ((A, 4), (T, 4), (U, 48)):
            block = [[row[p] for p in ports] for row in R]
            need(matmul(block, list(zip(*block))) == [[scale * x for x in row] for row in identity], "Gram identity")

    def route(self, stage, port, native=False):
        return 0 if stage == 0 else (self.native if native else self.routes)[stage, port]

    def query(self, bank, ports, stage=0, native=False):
        routed = {p: moved(self.route(stage, p, native), bank[p]) for p in ports}
        return [combine(*[(row[p], routed[p]) for p in ports]) for row in self.R]

    def inject(self, query, ports, stage=0, native=False):
        return {p: moved(undo(self.route(stage, p, native)), combine(*[(self.R[i][p] / 4, query[i]) for i in range(8)])) for p in ports}

    def forward(self, x, y):
        f = self.query(x, range(112))
        correction = self.inject(f, U + T)
        old_t = self.inject(self.query(x, T), A)
        xx = {p: combine((1, x[p]), (-1, correction[p])) if p in U else old_t[p] if p in A else correction[p] for p in range(112)}
        yy = {p: combine((1, y[p]), (1, xx[p])) if p in U else combine((1, x[p]), (1, y[p]), (-1, xx[p])) for p in range(112)}
        return xx, yy

    def forward_inverse(self, xx, yy):
        f, old_c = self.query(xx, T), self.query(xx, A)
        kf = self.inject(f, U)
        x = {p: combine((1, xx[p]), (1, kf[p])) for p in U}
        x.update(self.inject(old_c, T))
        ordinary = self.query(x, U)
        a = [combine((1, f[i]), (-1, ordinary[i]), (-1, old_c[i])) for i in range(8)]
        x.update(self.inject(a, A))
        y = {p: combine((1, yy[p]), (-1, xx[p])) if p in U else combine((1, xx[p]), (1, yy[p]), (-1, x[p])) for p in range(112)}
        return x, y

    def observe(self, x, y):
        # These x,y are the arbitrary post-F0 state. Only B1's A logger and
        # ordinary target subtraction appear in the observation contract.
        delta = self.inject(self.query(y, U + T, 2), A, 2)
        return ({p: x[p] for p in A + T}, {p: y[p] for p in A + T},
                {p: combine((1, y[p]), (1, delta[p])) for p in A},
                {p: combine((1, x[p]), (-1, y[p])) for p in U},
                {p: x[p] for p in S})

    def decode_cut(self, observed, fault=None):
        xs, ys, ya, c, reads = observed
        use_native = fault == "native_alignment_for_logical_chart"
        q = self.query({p: combine((1, ya[p]), (0 if fault == "omit_old_A" else -1, ys[p])) for p in A}, A, 2, use_native)
        ct = self.query(ys, T, 2, use_native)
        cc = self.query(c, U, 2, use_native)
        known = self.query(reads, S, 2, use_native)
        rhs = [combine((1, q[i]), (0 if fault == "omit_T" else -1, ct[i]),
                       (-1 if fault == "wrong_C_sign" else 1, cc[i]), (-1, known[i])) for i in range(8)]
        if fault == "inverse_before_scalar":
            rhs = [moved(undo(self.route(2, p)), row) for p, row in zip(J, rhs)]
        solved = [combine(*list(zip(row, rhs))) for row in self.dual]
        x = dict(xs) | dict(reads)
        for p, row in zip(J, solved):
            x[p] = row if fault == "inverse_before_scalar" else moved(undo(self.route(2, p, use_native)), row)
        y = dict(ys) | {p: combine((1, x[p]), (-1, c[p])) for p in U}
        return x, y


def independent_pair(start=0):
    return ({p: variable(start + p) for p in range(112)}, {p: variable(start + 112 + p) for p in range(112)})


def free_observations():
    blocks, next_id = [], 0
    for ports in (A + T, A + T, A, U, S):
        blocks.append({p: variable(next_id + i) for i, p in enumerate(ports)})
        next_id += len(ports)
    need(next_id == 224, "exact cut observation count")
    return tuple(blocks)


def first_residual(want, actual):
    for bank, (a, b) in enumerate(zip(want, actual)):
        for p in a:
            residual = combine((1, b[p]), (-1, a[p]))
            if residual:
                (v, index), coefficient = next(iter(sorted(residual.items())))
                g, shift = MAPS[index]
                return {"block": bank, "port": p, "input_array": v,
                        "owner_columns": g, "payload_shift": shift,
                        "coefficient": str(coefficient), "terms_in_residual_row": len(residual)}
    return None


def forget_payload(row):
    return combine(*[(value, {(v, intern(MAPS[index][0])): Q(1)}) for (v, index), value in row.items()])


def run():
    raw = source_bytes()
    R, routes, native, bindings = parse_sources(raw)
    model = Model(R, routes, native)
    inputs = independent_pair()
    need(model.forward_inverse(*model.forward(*inputs)) == inputs, "F0 inverse after forward")
    need(model.forward(*model.forward_inverse(*inputs)) == inputs, "F0 forward after inverse")
    observed = model.observe(*inputs)
    need(model.decode_cut(observed) == inputs, "cut decoder after observation, all input arrays")
    free = free_observations()
    need(model.observe(*model.decode_cut(free)) == free, "cut observation after decoder, all observation arrays")
    controls = {}
    for fault in ("omit_old_A", "omit_T", "wrong_C_sign", "inverse_before_scalar", "native_alignment_for_logical_chart"):
        changed = model.decode_cut(observed, fault)
        witness = first_residual(inputs, changed)
        need(witness is not None, "ineffective mutation: " + fault)
        controls[fault] = witness
        if fault == "native_alignment_for_logical_chart":
            # Precisely demonstrate why payload-constant fixtures miss this fault.
            need(all(forget_payload(changed[b][p]) == inputs[b][p] for b in range(2) for p in range(112)), "native confusion is invisible only after forgetting translations")
    missing = list(observed)
    missing[2] = {p: {} for p in A}
    controls["discard_B1_A_cut"] = first_residual(inputs, model.decode_cut(tuple(missing)))
    need(controls["discard_B1_A_cut"] is not None, "lost cut must fail")
    dirty = model.forward_inverse(*model.decode_cut(observed))
    changed_dirty = (dirty[0], {p: {} if p in U else dirty[1][p] for p in range(112)})
    controls["discard_initial_Y_dirt"] = first_residual(dirty, changed_dirty)
    need(controls["discard_initial_Y_dirt"] is not None, "arbitrary Y dirt control")
    return {
        "status": "PASS_QQ16_CUT_OPERATOR_AUDIT",
        "source_sha256": {name: digest(data) for name, data in raw.items()},
        "archive_members": MEMBERS, "route_bindings": bindings,
        "selected_ordinary_partition": {"A": A, "T": T, "U": U, "unread": J, "read": S},
        "R_J": model.minor, "R_J_inverse": model.dual,
        "formal_input_arrays": 224, "formal_observation_arrays": 224,
        "identities": ["F0_inverse F0 = I", "F0 F0_inverse = I", "cut_decode cut_observe = I", "cut_observe cut_decode = I"],
        "logical_charts_have_zero_payload_shift": True,
        "native_substitution_passes_payload_constant_projection": True,
        "negative_controls": controls,
        "scope": "Exact ordered QQ16 retained two-cut algebra on arbitrary owner/payload arrays; native execution and final controller availability are not checked",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true", help="create new receipt; refuses overwrite")
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result, sort_keys=True, indent=2, default=str) + "\n"
    result_path = HERE / "RESULT.json"
    if args.write_result:
        with result_path.open("x", encoding="utf-8", newline="\n") as out:
            out.write(encoded)
    else:
        need(result_path.read_text(encoding="utf-8") == encoded, "committed result differs or missing")
    print(result["status"], "arrays=224 inverse_identities=4 registered_routes=224 controls=7 no_new_kappa")


if __name__ == "__main__":
    main()
