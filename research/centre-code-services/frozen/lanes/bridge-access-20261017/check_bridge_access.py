"""Check future projection bridges at the actual supplier cuts."""

import argparse
from bisect import bisect_left
from collections import Counter, defaultdict
from fractions import Fraction
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
    "circuit-interface/INTERFACE.json": "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3",
    "cover-algebra/BRIDGES.md": "0db4e1e4589da903e50057b2d8657512c1185159a9ee18e605ad54c027c7dc80",
    "interface-proof/BRIDGE-OPERATOR-REVIEW.json": "c905a19d70f34c435c5f5454c6190bbfb1ce4594b1513bf76156acf620d7c6fc",
    "interface-proof/ORIGINAL-COMPLEX-MODES-REVIEW.json": "8b8c4d814b44c2fc42cf9ad995f8451512309fcfc46bea9317ebe4b4d79e8a4d",
}
SELECTED = [0, 7, 20, 27, 36, 46, 57, 111]
ORDINARY = [p for p in range(112) if p not in SELECTED]
UNIT = [1 << j for j in range(73)]
ZERO = (0, 0, 0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def owner(replica, pair, side, port):
    return 896 * replica + 224 * pair + 112 * side + port


def act(columns, vector):
    result = 0
    while vector:
        low = vector & -vector
        result ^= columns[low.bit_length() - 1]
        vector ^= low
    return result


def add_phase(a, b):
    return a[0] ^ b[0], a[1] ^ b[1] ^ (a[0] & b[0]), a[2] ^ b[2]


def negative(a):
    return a[0], a[1] ^ a[0], a[2]


@cache
def line(vector, exponent=1):
    cross = 0
    for j in range(73):
        if vector >> j & 1:
            cross ^= (vector & ((1 << j) - 1)) << (j * (j - 1) // 2)
    return (vector if exponent & 1 else 0,
            vector if exponent & 2 else 0, cross if exponent & 1 else 0)


def product(terms):
    result = ZERO
    for vector, exponent in terms:
        result = add_phase(result, line(vector, exponent % 4))
    return result


def canonical(q, level, side):
    if level == -1:
        return line(q) if side == 0 else ZERO
    frame = ((1 << (9 + 8 * level)) - 1, 0, 0)
    return add_phase(frame, line(q, 3)) if side else frame


def chart(q):
    hole = next(i for i in range(9) if not q >> i & 1)
    v = q ^ (1 << hole)
    order = list(range(9))
    order[0], order[hole] = order[hole], order[0]
    basis = [(1 << j) ^ (v if v >> j & 1 else 0) for j in order] + UNIT[9:]
    need(basis[0] == q and all((a & b).bit_count() % 2 == int(i == j)
         for i, a in enumerate(basis) for j, b in enumerate(basis)), "Actual orthogonal port chart")
    return basis


def route(basis, stage):
    columns = list(UNIT)
    if stage:
        swaps = [basis[j + 1] ^ UNIT[9 + 8 * (stage - 1) + j] for j in range(8)]
        columns = [v ^ sum_xor(a for a in swaps if (a & v).bit_count() & 1) for v in columns]
    need([act(columns, v) for v in columns] == UNIT, "Stage route is an involution")
    return columns


def sum_xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def phases_and_views(data):
    views, checks, controls = {}, Counter(), Counter()
    for p, recipe in enumerate(data["phases"]["recipes"]):
        q, basis = recipe["q"], chart(recipe["q"])
        need(basis[1:9] == recipe["idle_children"][0]["orthogonal_axes"][:8], "Source port basis")
        beta = sum((((v.bit_count() - 1) // 2) & 1) << j for j, v in enumerate(basis[1:9]))
        local_beta = act(basis[1:9], beta)
        for t in range(1, 9):
            rho = route(basis, t)
            lifted_beta = beta << (9 + 8 * (t - 1))
            delta_y = q ^ lifted_beta
            delta_x = local_beta ^ lifted_beta
            need(act(rho, recipe["stage_alignment"][t]["entry_Y"]) == delta_y,
                 "Future view has the literal supplier entry translation")
            need(recipe["stage_alignment"][t]["exit_X"] == delta_x,
                 "Past view has the literal supplier exit translation")
            for level in range(t):
                terms = [(act(rho, e), 1) for e in UNIT[:9 + 8 * level]] + [(q, -1)]
                actual = product(terms)
                common_axes = list(range(9, 9 + 8 * level)) + list(range(9 + 8 * (t - 1), 9 + 8 * t))
                expected = product([(UNIT[j], 1) for j in common_axes])
                need(add_phase(actual, line(delta_y, 2)) == expected, "Full future-Y phase identity")
                checks["future_Y"] += 1
                controls["omitted_Y_translation"] += actual != expected
                controls["wrong_Y_translation_order"] += add_phase(actual, line(act(rho, delta_y), 2)) != expected
            for level in range(t, 9):
                actual = product([(act(rho, e), 1) for e in UNIT[:9 + 8 * level]])
                expected = canonical(q, level, 0)
                need(add_phase(actual, line(delta_x, 2)) == expected, "Full past-X phase identity")
                checks["past_X"] += 1
                controls["omitted_X_translation"] += actual != expected
            views[p, t, "Y"] = dict(port=p, stage=t, side="Y", route_columns=rho,
                translation_after_route=delta_y, translation_before_route=act(rho, delta_y))
            views[p, t, "X"] = dict(port=p, stage=t, side="X", route_columns=rho,
                translation_after_route=delta_x, translation_before_route=act(rho, delta_x))
    need(checks == {"future_Y": 4032, "past_X": 4032}, "Full cone coverage")
    need(controls == {"omitted_Y_translation": 4032, "wrong_Y_translation_order": 4032,
                      "omitted_X_translation": 4032}, "All exact phase controls fail")
    return views, dict(checks), dict(controls)


def scalar_word(B, sign):
    word = [["add", 112 + p, p, str(sign)] for p in ORDINARY]
    word += [["add", 112 + a, p, str(-sign * B[i][j])]
             for i, a in enumerate(SELECTED) for j, p in enumerate(ORDINARY) if B[i][j]]
    return word


def scalar_check(B):
    receipts = {}
    for sign in (-1, 1):
        word = scalar_word(B, sign)
        rows = [{j: Fraction(1)} for j in range(224)]
        max_norm = Fraction(1)
        for _, target, source, coefficient in word:
            coefficient = Fraction(coefficient)
            need(source < 112 and target >= 112 and source in ORDINARY, "No changed or selected source is read")
            for origin, value in rows[source].items():
                rows[target][origin] = rows[target].get(origin, 0) + coefficient * value
            max_norm = max(max_norm, sum(abs(x) for x in rows[target].values()))
        expected = [{j: Fraction(1)} for j in range(224)]
        for p in ORDINARY:
            expected[112 + p][p] = Fraction(sign)
        for i, a in enumerate(SELECTED):
            for j, p in enumerate(ORDINARY):
                if B[i][j]:
                    expected[112 + a][p] = -sign * B[i][j]
        need(rows == expected and len(word) == 520 and max_norm == 27, "Exact arbitrary-data U bridge")
        need(rows[:112] == [{j: Fraction(1)} for j in range(112)], "Every source is unchanged")
        receipts[str(sign)] = dict(program=word, arbitrary_input_columns=224,
            unit_adds=104, half_adds=416, real_scalar_bound=4992,
            maximum_intermediate_row_one_norm=str(max_norm), native_children=0,
            private_fields=0, unchanged_source_rows=112)
    return receipts


def schedule_audit(data, views, mixed):
    template, phases, word = data["template"], data["phases"]["recipes"], data["word"]
    events, calls = template["execution_schedule"], template["calls"]
    bases = [chart(r["q"]) for r in phases]
    positions = {e["time"]: i for i, e in enumerate(events) if e["kind"] == "local_cover_sweep"}
    touches, deadline = defaultdict(list), {}
    for i, e in enumerate(events):
        if e["kind"] == "local_cover_sweep":
            c = calls[e["time"]]
            touches[c["replica"], c["pair"]].append(i)
        elif e["kind"] == "bridge":
            for pair in (e["src"], e["dst"]):
                touches[e["replica"], pair].append(i)
        elif e["kind"] == "idle_cover_sweep":
            for side, child in enumerate(e["child_indices"]):
                deadline[e["replica"], child] = (i, side)
    jobs, suffixes, partition = defaultdict(list), defaultdict(list), defaultdict(set)
    for index, job in enumerate(template["hosting"]["pooled_slots"]):
        end, side = deadline[job["owner_replica"], job["child"]]
        e = events[end]
        used = touches[job["owner_replica"], e["pair"]]
        offset = bisect_left(used, end)
        release = used[offset - 1] if offset else -1
        need(release < positions[job["time"]] < end, "Old complete helper strict window")
        family = owner(job["owner_replica"], e["pair"], side, job["port"])
        role = 224 + job["helper"]
        width = len(word["frames"][word["final"][role]]) - len(word["frames"][word["start"][role]])
        begin = 8 * (e["from_level"] + 1) + 1 + job["offset"]
        axes = list(range(begin, begin + width))
        spectators = [j for j in range(73) if j not in axes][:9 - width]
        descriptor = [3, job["child"], job["offset"]] if width == 9 else [4, job["child"], job["offset"], width, spectators]
        need(job["family"] == family and job["width"] == width
             and calls[job["time"]]["owners"][role] == [family, descriptor], "Literal helper role and route")
        key = job["owner_replica"], job["child"], job["port"]
        need(not partition[key].intersection(axes), "No helper axis repeats")
        partition[key].update(axes)
        jobs[job["time"]].append((family, product([(bases[job["port"]][j], 1) for j in axes])))
    for job in template["idle_children"]:
        end, side = deadline[job["replica"], job["child"]]
        e = events[end]
        begin = 8 * (e["from_level"] + 1) + 1 + job["pending_offset"]
        stop = 8 * (e["to_level"] + 1) + 1
        axes = list(range(begin, stop))
        family = owner(job["replica"], e["pair"], side, job["port"])
        need(job["family"] == family and len(axes) == job["rank"], "Literal idle suffix")
        key = job["replica"], job["child"], job["port"]
        need(not partition[key].intersection(axes), "No suffix axis repeats")
        partition[key].update(axes)
        suffixes[end].append((family, product([(bases[job["port"]][j], 1) for j in axes])))
    for (replica, child), (end, _) in deadline.items():
        e = events[end]
        expected = set(range(8 * (e["from_level"] + 1) + 1, 8 * (e["to_level"] + 1) + 1))
        for p in range(112):
            need(partition[replica, child, p] == expected, "Every pending axis is used once")
    frames = [canonical(phases[f % 112]["q"], -1, (f // 112) % 2) for f in range(14336)]
    retired, cuts, counts = set(), [], Counter()
    bridge_count = Counter()

    def complete(replica, pair, level):
        for side in (0, 1):
            for p in range(112):
                f = owner(replica, pair, side, p)
                expected = canonical(phases[p]["q"], level, side)
                if f in retired:
                    expected = add_phase(expected, line(phases[p]["q"]))
                need(frames[f] == expected, "Actual complete bank phase")

    for position, event in enumerate(events):
        kind, replica = event["kind"], event.get("replica")
        if kind == "local_cover_sweep":
            call = calls[event["time"]]
            pair, stage = call["pair"], call["stage"]
            need(len(call["owners"]) == len({o[0] for o in call["owners"]}) == 704, "No local owner alias")
            complete(replica, pair, stage - 1)
            for side in (0, 1):
                for p in range(112):
                    f = owner(replica, pair, side, p)
                    need(call["owners"][112 * side + p] == [f, [1, stage, p]], "Actual active route")
                    frames[f] = canonical(phases[p]["q"], stage, side)
                    if mixed and side == 1 and p in SELECTED and stage in (2, 4, 6, 8):
                        retired.add(f)
                        frames[f] = add_phase(frames[f], line(phases[p]["q"]))
            for f, phase in jobs[event["time"]]:
                frames[f] = add_phase(frames[f], phase)
                counts["helper_jobs"] += 1
            complete(replica, pair, stage)
            counts["local_calls"] += 1
        elif kind == "idle_cover_sweep":
            for f, phase in suffixes[position]:
                frames[f] = add_phase(frames[f], phase)
                counts["idle_suffixes"] += 1
            for side, child in enumerate(event["child_indices"]):
                for p in range(112):
                    f = owner(replica, event["pair"], side, p)
                    frames[f] = add_phase(frames[f], line(phases[p]["idle_children"][child]["translation_after"], 2))
            complete(replica, event["pair"], event["to_level"])
            counts["idle_events"] += 1
        elif kind == "bridge":
            index = bridge_count[replica]
            bridge_count[replica] += 1
            if index < 6:
                src_pair, dst_pair, side = event["dst"], event["src"], 1
                stage = 2 * dst_pair + 1
                level = 2 * src_pair + 1 + (index % 2)
                sign = -event["coefficient"]
                need(src_pair + 1 == dst_pair and level < stage, "Future Y bridge order")
                counts["future_Y_cuts"] += 1
            else:
                src_pair, dst_pair, side = event["src"], event["dst"], 0
                stage, level, sign = 2 * dst_pair + 1, 8, 1
                need(src_pair + 1 == dst_pair and stage <= level, "Past X tail order")
                counts["past_X_tail_cuts"] += 1
            families = [owner(replica, src_pair, side, p) for p in ORDINARY]
            families += [owner(replica, dst_pair, side, p) for p in range(112)]
            need(len(families) == len(set(families)) == 216, "No bridge source/target owner alias")
            for p in ORDINARY:
                source = owner(replica, src_pair, side, p)
                target = owner(replica, dst_pair, side, p)
                expected = canonical(phases[p]["q"], level, side)
                need(frames[source] == frames[target] == expected, "Exact same-port ordinary bridge phase")
            for p in SELECTED:
                target = owner(replica, dst_pair, side, p)
                need(target not in retired and frames[target] == canonical(phases[p]["q"], level, side),
                     "Every selected target has the required unmodified phase")
            name = "Y" if side else "X"
            cuts.append(dict(position=position, source_event=event["source_event"], replica=replica,
                source_pair=src_pair, target_pair=dst_pair, side=name, stage=stage,
                completed_level=level, sign=sign,
                source_ordinary_families=[owner(replica, src_pair, side, p) for p in ORDINARY],
                target_families=[owner(replica, dst_pair, side, p) for p in range(112)],
                aligned_source_ports=ORDINARY, aligned_target_ports=SELECTED,
                scalar_word_key=str(sign), new_affine_view_maps=224,
                retained_X_bridge=(index < 6), removed_Y_tail=(index >= 6)))
            counts["all_bridge_frame_pairs"] += 224
        elif kind == "terminal_Y_translations":
            for pair in range(4):
                complete(replica, pair, 8)
            counts["preterminal_endpoints"] += 1
        elif kind == "terminal":
            counts["terminal_events"] += 1
        else:
            need(kind in ("bank_padding_cover_sweep", "translate_every_live_family"), "Known source event")
    need(all(v == 9 for v in bridge_count.values()) and len(cuts) == 144, "All new bridge cuts")
    need(counts["helper_jobs"] == 69120 and counts["idle_suffixes"] == 7526
         and counts["future_Y_cuts"] == 96 and counts["past_X_tail_cuts"] == 48, "Complete source schedule")
    need(len(retired) == (512 if mixed else 0), "Selected FULL exceptions")
    return dict(mixed_selected_outputs=mixed, checked_counts=dict(counts), cuts=cuts,
                retired_selected_fields_not_read=512 if mixed else 0)


def main(args):
    raw = ARCHIVE.read_bytes()
    need(sha256(raw).hexdigest() == ARCHIVE_PIN, "Selected archive pin")
    data = {}
    with tarfile.open(ARCHIVE) as stream:
        for key, (path, pin) in MEMBERS.items():
            raw = stream.extractfile(path).read()
            need(sha256(raw).hexdigest() == pin, "Archive member pin: " + key)
            data[key] = json.loads(gzip.decompress(raw) if path.endswith(".gz") else raw)
    for path, pin in PINS.items():
        need(sha256((LANES / path).read_bytes()).hexdigest() == pin, "Premise pin: " + path)
    interface = json.loads((LANES / "circuit-interface/INTERFACE.json").read_bytes())
    R = [[Fraction(row.get(str(p), "0")) for p in range(112)] for row in interface["R"]]
    need(interface["ports"] == [r["q"] for r in data["phases"]["recipes"]], "Actual port order")
    need(all(sum(R[k][a] * R[k][b] for k in range(8)) == 4 * int(i == j)
         for i, a in enumerate(SELECTED) for j, b in enumerate(SELECTED)), "Selected square minor")
    B = [[sum(R[k][a] * R[k][p] for k in range(8)) / 4 for p in ORDINARY] for a in SELECTED]
    need(sum(bool(c) for row in B for c in row) == 416
         and all(sum(bool(c) for c in row) == 52 for row in B)
         and all(abs(c) == Fraction(1, 2) for row in B for c in row if c), "Exact sparse B matrix")
    views, checks, controls = phases_and_views(data)
    scalar = scalar_check(B)
    uniform, mixed = [schedule_audit(data, views, setting) for setting in (False, True)]
    need(uniform["cuts"] == mixed["cuts"], "One program handles both retirement phase policies")
    payload = dict(format="future-projection-bridge-v1", views=list(views.values()),
                   scalar_words={k: v["program"] for k, v in scalar.items()}, cuts=uniform["cuts"],
                   operation_order=["104 same-port ordinary ADDs", "Align 104 source U and 8 target A fields",
                                    "416 half ADDs", "Undo 112 affine views"],
                   inverse_view_order="Undo translation, then undo the route; rho is its own inverse")
    payload_raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    args.program.write_bytes(gzip.compress(payload_raw, mtime=0))
    for row in scalar.values():
        del row["program"]
    receipt = dict(status="PASS_ACTUAL_FUTURE_PROJECTION_BRIDGES", archive_sha256=ARCHIVE_PIN,
        source_member_sha256={k: v[1] for k, v in MEMBERS.items()}, premise_sha256=PINS,
        checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        payload_sha256=sha256(payload_raw).hexdigest(), phase_checks=checks, phase_controls=controls,
        scalar_words=scalar, uniform_schedule=uniform["checked_counts"], mixed_schedule=mixed["checked_counts"],
        mixed_retired_selected_fields_not_read=512, new_native_children=0, new_private_fields=0,
        unchanged_original_helper_jobs=69120, unchanged_original_idle_suffixes=7526,
        complete_T_equals_W_bridge_invoice=dict(U_updates=144, real_scalar_bound=718848,
            retained_X_unit_adds=10752, retained_X_real_scalar_bound=86016,
            total_real_scalar_bound=804864, new_affine_view_maps=32256,
            native_profile_delta={}, live_delta=0, physical_stock_delta=0),
        complete_T_zero_bridge_invoice=dict(U_updates=96, real_scalar_bound=479232,
            retained_X_real_scalar_bound=86016, total_real_scalar_bound=565248,
            new_affine_view_maps=21504, native_profile_delta={}, live_delta=0, physical_stock_delta=0),
        tensor_scope="All phase polynomials are exact modulo four and have zero constant. The identities tensor to every positive width.",
        scope="Literal source-bound bridge macros and exact phase/owner admission. This is not a complete supplier, precision invoice, or kappa claim.",
        open_costs=["Compile affine view maps in the complete finite invoice", "Bind the selected controller and all new local maps", "Price complete controller growth and recursive supplier"])
    args.out.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(receipt["status"])
    print(json.dumps(dict(cuts=144, new_native_children=0, scalar=804864, affine_views=32256), sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "ACCESS.json")
    parser.add_argument("--program", type=Path, default=HERE / "BRIDGE-PROGRAMS.json.gz")
    main(parser.parse_args())
