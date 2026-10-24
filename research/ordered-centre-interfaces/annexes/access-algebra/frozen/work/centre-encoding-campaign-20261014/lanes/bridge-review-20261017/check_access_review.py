"""Review the future bridge program from pinned supplier data."""

from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
import gzip
import json
from pathlib import Path
import tarfile


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
ROOT = HERE.parents[3]
ARCHIVE = ROOT / "worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_PIN = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBERS = {
    "template": ("candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz", "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760"),
    "phases": ("candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json", "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"),
    "word": ("candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz", "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"),
}
PINS = {
    "bridge-access-20261017/ACCESS.md": "7fbce6a85b3704293e87ce11b8cd0add2f70f9781e2ade516ffd5fd5c29c6b58",
    "bridge-access-20261017/ACCESS.json": "33944a0fe4587aa1ae939dd9861ad7d4c2b7c523dcf05f88fc404e4eeff8c7e8",
    "bridge-access-20261017/check_bridge_access.py": "9510c5624dfb51d98767728084851e4ee75a135e6d7b546569a47fe458485111",
    "circuit-interface/INTERFACE.json": "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3",
    "interface-proof/ORIGINAL-COMPLEX-MODES-REVIEW.json": "8b8c4d814b44c2fc42cf9ad995f8451512309fcfc46bea9317ebe4b4d79e8a4d",
}
A = [0, 7, 20, 27, 36, 46, 57, 111]
U = [p for p in range(112) if p not in A]
E = [1 << i for i in range(73)]


def require(condition, label):
    if not condition:
        raise ValueError(label)


def read_sources():
    require(sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_PIN, "Archive pin")
    for name, pin in PINS.items():
        require(sha256((LANES / name).read_bytes()).hexdigest() == pin, name)
    data = {}
    with tarfile.open(ARCHIVE) as stream:
        for name, (member, pin) in MEMBERS.items():
            raw = stream.extractfile(member).read()
            require(sha256(raw).hexdigest() == pin, member)
            data[name] = json.loads(gzip.decompress(raw) if member.endswith(".gz") else raw)
    return data


@cache
def parity_polynomial(v):
    """Expand binary parity as an integer polynomial modulo four."""
    bits = [j for j in range(73) if (v >> j) & 1]
    out = {(j,): 1 for j in bits}
    out.update({(j, k): 2 for i, j in enumerate(bits) for k in bits[i + 1:]})
    return out


def append_phase(out, vector, coefficient=1):
    for term, value in parity_polynomial(vector).items():
        new = (out.get(term, 0) + coefficient * value) % 4
        if new:
            out[term] = new
        else:
            out.pop(term, None)


def phase(terms):
    out = {}
    for v, c in terms:
        append_phase(out, v, c)
    return out


@cache
def boundary(q, level, side):
    if level < 0:
        return phase([(q, 1)] if side == 0 else [])
    return phase([(v, 1) for v in E[:9 + 8 * level]] + ([(q, -1)] if side else []))


def action(columns, value):
    out = 0
    for i, column in enumerate(columns):
        if (value >> i) & 1:
            out ^= column
    return out


def stage_route(q, basis, t):
    """Build the map by its action on the supplied orthonormal basis."""
    block = E[9 + 8 * (t - 1):9 + 8 * t]
    fixed = [q] + [v for v in E[9:] if v not in block]
    pairs = list(zip(basis, block)) + list(zip(block, basis)) + [(v, v) for v in fixed]
    columns = []
    for coordinate in E:
        value = 0
        for old, new in pairs:
            if (old & coordinate).bit_count() % 2:
                value ^= new
        columns.append(value)
    require([action(columns, c) for c in columns] == E, "Involutive route")
    return columns


def phase_review(recipes, payload):
    views = {(v["port"], v["stage"], v["side"]): v for v in payload["views"]}
    require(len(views) == len(payload["views"]) == 1792, "All unique views")
    counts = Counter()
    for p, recipe in enumerate(recipes):
        q = recipe["q"]
        b = recipe["idle_children"][0]["orthogonal_axes"][:8]
        chart = [q] + b + E[9:]
        require(all((v & w).bit_count() % 2 == (i == j)
                    for i, v in enumerate(chart) for j, w in enumerate(chart)), "Source basis")
        beta = [((v.bit_count() - 1) // 2) % 2 for v in b]
        for t in range(1, 9):
            rho = stage_route(q, b, t)
            lifted = sum(beta[j] * E[9 + 8 * (t - 1) + j] for j in range(8))
            local = 0
            for j in range(8):
                if beta[j]:
                    local ^= b[j]
            deltas = {"Y": q ^ lifted, "X": local ^ lifted}
            require(action(rho, recipe["stage_alignment"][t]["entry_Y"]) == deltas["Y"], "Supplier Y gauge")
            require(recipe["stage_alignment"][t]["exit_X"] == deltas["X"], "Supplier X gauge")
            for side, delta in deltas.items():
                v = views[p, t, side]
                require(v["route_columns"] == rho and v["translation_after_route"] == delta
                        and v["translation_before_route"] == action(rho, delta), "Literal affine view")
            for h in range(9):
                side = "Y" if h < t else "X"
                terms = [(action(rho, v), 1) for v in E[:9 + 8 * h]]
                if side == "Y":
                    terms.append((q, -1))
                    common = phase([(v, 1) for v in E[9:9 + 8 * h] + E[9 + 8 * (t - 1):9 + 8 * t]])
                else:
                    common = boundary(q, h, 0)
                old = phase(terms)
                corrected = dict(old)
                append_phase(corrected, deltas[side], 2)
                require(corrected == common, "Every exact phase coefficient")
                require(old != common, "Omitted translation control")
                if side == "Y":
                    wrong = dict(old)
                    append_phase(wrong, action(rho, deltas[side]), 2)
                    require(wrong != common, "Wrong route order control")
                counts[side] += 1
    require(counts == {"Y": 4032, "X": 4032}, "All phase cone cases")
    return dict(counts)


def scalar_review(payload):
    interface = json.loads((LANES / "circuit-interface/INTERFACE.json").read_bytes())
    r = [[F(row.get(str(p), 0)) for p in range(112)] for row in interface["R"]]
    require(all(sum(r[i][p] * r[j][p] for p in range(112)) == 56 * (i == j)
                for i in range(8) for j in range(8)), "Actual centre Gram matrix")
    require(all(sum(r[k][a] * r[k][b] for k in range(8)) == 4 * (a == b)
                for a in A for b in A), "Actual selected minor")
    b = {(a, p): sum(r[k][a] * r[k][p] for k in range(8)) / 4 for a in A for p in U}
    b = {key: value for key, value in b.items() if value}
    require(len(b) == 416 and set(map(abs, b.values())) == {F(1, 2)}, "Actual half coefficients")
    require(Counter(a for a, p in b) == {a: 52 for a in A}, "Actual selected row support")
    require(all(sum(b.get((a, p), 0) * b.get((c, p), 0) for p in U) == 13 * (a == c)
                for a in A for c in A), "Actual B D equals thirteen identity")
    for sign in [-1, 1]:
        program = payload["scalar_words"][str(sign)]
        require(len(program) == 520, "Literal word length")
        rows = [{i: F(1)} for i in range(224)]
        max_norm = F(1)
        for index, (op, target, source, coefficient) in enumerate(program):
            coefficient = F(coefficient)
            require(op == "add" and source in U and target >= 112, "Only ordinary sources")
            if index < 104:
                require(target == 112 + source and coefficient == sign, "Old-frame same-port prefix")
            else:
                require(target - 112 in A and coefficient == -sign * b[target - 112, source], "Aligned sparse suffix")
            for j, value in rows[source].items():
                rows[target][j] = rows[target].get(j, 0) + coefficient * value
            max_norm = max(max_norm, sum(abs(v) for v in rows[target].values()))
        expected = [{i: F(1)} for i in range(224)]
        for p in U:
            expected[112 + p][p] = F(sign)
        for (a, p), value in b.items():
            expected[112 + a][p] = -sign * value
        require(rows == expected and max_norm == 27, "All arbitrary bank input columns")
    return {"signs": 2, "input_columns_per_sign": 224, "maximum_row_one_norm": "27",
            "real_scalar_per_update": 104 * 8 + 416 * 10, "affine_maps_per_update": 2 * (104 + 8)}


def family(replica, pair, side, port):
    return replica * 896 + pair * 224 + side * 112 + port


def schedule_review(data, payload, mixed):
    template, word, recipes = data["template"], data["word"], data["phases"]["recipes"]
    events, calls = template["execution_schedule"], template["calls"]
    positions = {e["time"]: i for i, e in enumerate(events) if e["kind"] == "local_cover_sweep"}
    ends = {(e["replica"], child): (i, e, side) for i, e in enumerate(events)
            if e["kind"] == "idle_cover_sweep" for side, child in enumerate(e["child_indices"])}
    jobs, suffixes, covered = defaultdict(list), defaultdict(list), defaultdict(list)
    touches = defaultdict(list)
    for i, e in enumerate(events):
        if e["kind"] == "local_cover_sweep":
            c = calls[e["time"]]
            touches[c["replica"], c["pair"]].append(i)
        elif e["kind"] == "bridge":
            for pair in [e["src"], e["dst"]]:
                touches[e["replica"], pair].append(i)
    for job in template["hosting"]["pooled_slots"]:
        end, idle, side = ends[job["owner_replica"], job["child"]]
        p, role = job["port"], 224 + job["helper"]
        f = family(job["owner_replica"], idle["pair"], side, p)
        width = len(word["frames"][word["final"][role]]) - len(word["frames"][word["start"][role]])
        axes = recipes[p]["idle_children"][job["child"]]["orthogonal_axes"][job["offset"]:job["offset"] + width]
        source_pos = positions[job["time"]]
        release = max([-1] + [i for i in touches[job["owner_replica"], idle["pair"]] if i < end])
        require(release < source_pos < end and len(axes) == width == job["width"], "Strict source helper window")
        first = 9 + 8 * idle["from_level"] + job["offset"]
        indices = list(range(first, first + width))
        spectators = [j for j in range(73) if j not in indices][:9 - width]
        descriptor = [3, job["child"], job["offset"]] if width == 9 else [4, job["child"], job["offset"], width, spectators]
        require(job["family"] == f and calls[job["time"]]["owners"][role] == [f, descriptor], "Unchanged helper route")
        covered[job["owner_replica"], job["child"], p].extend(axes)
        jobs[job["time"]].append((f, axes))
    for job in template["idle_children"]:
        end, idle, side = ends[job["replica"], job["child"]]
        p = job["port"]
        axes = recipes[p]["idle_children"][job["child"]]["orthogonal_axes"][job["pending_offset"]:]
        f = family(job["replica"], idle["pair"], side, p)
        require(job["family"] == f and len(axes) == job["rank"], "Unchanged idle suffix")
        covered[job["replica"], job["child"], p].extend(axes)
        suffixes[end].append((f, axes))
    for (rep, child), (end, idle, side) in ends.items():
        for p in range(112):
            axes = recipes[p]["idle_children"][child]["orthogonal_axes"]
            require(Counter(covered[rep, child, p]) == Counter(axes) and len(axes) == len(set(axes)), "Exact native axis partition")
    state = [dict(boundary(recipes[f % 112]["q"], -1, (f // 112) % 2)) for f in range(14336)]
    retired, counts, cuts, tail_order = set(), Counter(), [], defaultdict(list)

    def complete(rep, pair, level):
        for side in [0, 1]:
            for p in range(112):
                f = family(rep, pair, side, p)
                want = dict(boundary(recipes[p]["q"], level, side))
                if f in retired:
                    append_phase(want, recipes[p]["q"])
                require(state[f] == want, "Complete source bank phase")

    for position, event in enumerate(events):
        kind, rep = event["kind"], event.get("replica")
        if kind == "local_cover_sweep":
            c = calls[event["time"]]
            stage, pair = c["stage"], c["pair"]
            require(c["orientation"] == ("backward" if stage % 2 else "forward")
                    and pair == max(0, (stage - 1) // 2), "Actual pair and local orientation")
            require(len(c["owners"]) == len({o[0] for o in c["owners"]}) == 704, "No local owner alias")
            complete(rep, pair, stage - 1)
            for side in [0, 1]:
                for p in range(112):
                    f = family(rep, pair, side, p)
                    require(c["owners"][112 * side + p] == [f, [1, stage, p]] and f not in retired, "Original active owner route")
                    state[f] = dict(boundary(recipes[p]["q"], stage, side))
                    if mixed and side == 1 and p in A and stage in [2, 4, 6, 8]:
                        retired.add(f)
                        append_phase(state[f], recipes[p]["q"])
            for f, axes in jobs[event["time"]]:
                for axis in axes:
                    append_phase(state[f], axis)
                counts["helper_jobs"] += 1
                counts["retired_helper_jobs"] += int(f in retired)
            complete(rep, pair, stage)
            counts["local_calls"] += 1
        elif kind == "idle_cover_sweep":
            for f, axes in suffixes[position]:
                for axis in axes:
                    append_phase(state[f], axis)
                counts["idle_suffixes"] += 1
                counts["retired_idle_suffixes"] += int(f in retired)
            for side, child in enumerate(event["child_indices"]):
                for p in range(112):
                    f = family(rep, event["pair"], side, p)
                    append_phase(state[f], recipes[p]["idle_children"][child]["translation_after"], 2)
            complete(rep, event["pair"], event["to_level"])
            counts["idle_events"] += 1
        elif kind == "bridge":
            tail = event["src"] < event["dst"]
            if tail:
                src, dst, side = event["src"], event["dst"], 0
                level, sign = 8, 1
                counts["X_tail"] += 1
                tail_order[rep].append(dst)
            else:
                src, dst, side = event["dst"], event["src"], 1
                level = 2 * src + 1 + int(event["coefficient"] == -1)
                sign = -event["coefficient"]
                counts["Y_bridge"] += 1
                require(calls[event["time"]]["pair"] == src
                        and calls[event["time"]]["stage"] == level, "Y bridge follows its specified local call")
            stage = 2 * dst + 1
            require(dst == src + 1 and (stage <= level if tail else level < stage), "Actual bridge cone")
            sources = [family(rep, src, side, p) for p in U]
            targets = [family(rep, dst, side, p) for p in range(112)]
            require(len(set(sources + targets)) == 216, "No bridge family alias")
            for p in U:
                require(state[family(rep, src, side, p)] == state[family(rep, dst, side, p)]
                        == boundary(recipes[p]["q"], level, side), "Same-port ordinary frame")
            for p in A:
                f = family(rep, dst, side, p)
                require(f not in retired and state[f] == boundary(recipes[p]["q"], level, side), "Selected target frame")
            cuts.append(dict(position=position, source_event=event["source_event"], replica=rep,
                source_pair=src, target_pair=dst, side="X" if tail else "Y", stage=stage,
                completed_level=level, sign=sign, source_ordinary_families=sources,
                target_families=targets, aligned_source_ports=U, aligned_target_ports=A,
                scalar_word_key=str(sign), new_affine_view_maps=224,
                retained_X_bridge=not tail, removed_Y_tail=tail))
        elif kind == "terminal_Y_translations":
            for pair in range(4):
                complete(rep, pair, 8)
            counts["preterminal"] += 1
        elif kind == "terminal":
            counts["terminal"] += 1
        else:
            require(kind in ["bank_padding_cover_sweep", "translate_every_live_family"], "Known event")
    require(cuts == payload["cuts"], "Every literal program cut")
    require(len(tail_order) == 16 and all(v == [3, 2, 1] for v in tail_order.values()), "Descending X tails")
    require(counts["Y_bridge"] == 96 and counts["X_tail"] == 48
            and counts["helper_jobs"] == 69120 and counts["idle_suffixes"] == 7526, "Full schedule counts")
    require(len(retired) == (512 if mixed else 0), "All selected exceptions")
    return dict(counts)


def main():
    data = read_sources()
    raw = gzip.decompress((LANES / "bridge-access-20261017/BRIDGE-PROGRAMS.json.gz").read_bytes())
    payload = json.loads(raw)
    require(sha256(raw).hexdigest() == "57e2f089e0dd9f363603fc0278612b8ae8b98956a7422aa41fbd592922213abc", "Literal payload pin")
    phases = phase_review(data["phases"]["recipes"], payload)
    scalar = scalar_review(payload)
    schedules = {str(mixed): schedule_review(data, payload, mixed) for mixed in [False, True]}
    receipt = dict(status="PASS_INDEPENDENT_FUTURE_BRIDGE_ACCESS", source_pins=PINS,
        archive_sha256=ARCHIVE_PIN, archive_members={k: p for k, (_, p) in MEMBERS.items()},
        payload_sha256=sha256(raw).hexdigest(), checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        phase_cases=phases, scalar=scalar, schedules=schedules,
        total_T_equals_W=dict(real_scalar=144 * 4992 + 96 * 112 * 8, affine_maps=144 * 224),
        total_T_zero=dict(real_scalar=96 * 4992 + 96 * 112 * 8, affine_maps=96 * 224),
        native_children_delta=0, private_fields_delta=0,
        scope="Bridge macro admission only. New local maps, idle-X codes, decoder, finite map costs and recursion remain separate.")
    (HERE / "ACCESS-REVIEW.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])
    print(json.dumps({"phase_cases": phases, "schedule": schedules["True"]}, sort_keys=True))


if __name__ == "__main__":
    main()
