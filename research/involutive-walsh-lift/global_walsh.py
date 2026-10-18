"""Emit and check the selected global doubled Walsh frame binding.

New code: Apache-2.0. Research and verification used OpenAI Codex assistance.
"""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import sources


BASE = sources.BASE
ARCHIVE = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBERS = {
    "template": ("candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz",
                 "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760"),
    "phases": ("candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json",
               "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"),
    "word": ("candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz",
             "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"),
    "programs": ("candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz",
                 "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"),
}
FULL = (1 << 73)-1


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def content_digest(path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def save_gzip(path, value):
    data = bytearray(gzip.compress(canonical(value), mtime=0))
    data[9] = 255
    path.write_bytes(data)
    return sha256(canonical(value)).hexdigest()


def parity(value):
    return value.bit_count() & 1


def multiply(columns, vector):
    out = 0
    while vector:
        bit = vector & -vector
        out ^= columns[bit.bit_length()-1]
        vector ^= bit
    return out


def transpose(columns):
    return [sum(((column >> i) & 1) << j for j, column in enumerate(columns))
            for i in range(len(columns))]


def double_vector(vector, copy):
    return sum(1 << (2*i+copy) for i in range(73) if vector >> i & 1)


def double_columns(columns):
    return [double_vector(v, copy) for v in columns for copy in (0, 1)]


def port_basis(q):
    zero = next(i for i in range(9) if not (q >> i & 1))
    even = q ^ (1 << zero)
    order = list(range(9))
    order[0], order[zero] = order[zero], order[0]
    basis = [(1 << i) ^ (even if even >> i & 1 else 0) for i in order]
    basis.extend(1 << i for i in range(9, 73))
    require(basis[0] == q, "Port is the first chart axis")
    require(all(parity(x & y) == int(i == j)
                for i, x in enumerate(basis) for j, y in enumerate(basis)),
            "The full port chart is orthogonal")
    return basis


def route_columns(basis, stage):
    if stage == 0:
        return [1 << i for i in range(73)]
    permuted = basis.copy()
    for j in range(8):
        a, b = j+1, 8*stage+j+1
        permuted[a], permuted[b] = permuted[b], permuted[a]
    inverse = transpose(basis)
    return [multiply(permuted, v) for v in inverse]


def mask(indices):
    return sum(1 << i for i in indices)


def level_mask(level, side):
    return ((1 << (8*(level+1)+1))-2) | int(side == 0)


def matrix_add(rows, target, source, coefficient):
    rows[target] = [x+coefficient*y for x, y in zip(rows[target], rows[source])]


def terminal(rows):
    old = [row.copy() for row in rows]
    for pair in range(4):
        rows[2*pair] = old[2*pair+1]
        rows[2*pair+1] = [-x for x in old[2*pair]]


def controller_matrix(recipe, bad_bridge=False):
    rows = [[int(i == j) for j in range(8)] for i in range(8)]
    for event in recipe:
        kind = event["kind"]
        if kind == "local":
            x = 2*event["pair"]
            target, source, coefficient = ((x, x+1, -1) if event["reverse"]
                                           else (x+1, x, 1))
            matrix_add(rows, target, source, coefficient)
        elif kind == "bridge":
            x, y, c = 2*event["dst"], 2*event["src"], event["coefficient"]
            matrix_add(rows, x, y, c)
            matrix_add(rows, y+1, x+1, c if bad_bridge else -c)
        else:
            require(kind == "terminal", "Known controller event")
            terminal(rows)
    return rows


def load(args):
    pins = {name: pin for name, pin in MEMBERS.values()}
    raw = sources.archive_members(args.repo, sources.SELECTED_ARCHIVE, ARCHIVE, pins)
    values = {key: sources.decode_json(raw[name], name)
              for key, (name, _) in MEMBERS.items()}
    reviews, review_hashes = {}, {}
    for name in ("WALSH-RETARGET-REVIEW.json", "DOUBLED-WALSH-REVIEW.json"):
        path = args.evidence/name
        review_hashes[name] = content_digest(path)
        reviews[name] = json.loads(path.read_bytes())
    local = reviews["WALSH-RETARGET-REVIEW.json"]
    doubled = reviews["DOUBLED-WALSH-REVIEW.json"]
    require(local["status"] == "PASS_INDEPENDENT_WALSH_RETARGET_FRAMES_AND_ACTUAL_WORD_LEDGER",
            "The exact local frame and scalar review passed")
    require(doubled["status"] == "PASS_EXACT_DOUBLED_WALSH_NATIVE_LOWERING",
            "The exact doubled native review passed")
    require(local["source_base"] == BASE and local["source_archive_sha256"] == sources.LOCAL_ARCHIVE_SHA256,
            "The local proof uses the pinned source")
    for key in ("word", "programs"):
        filename = MEMBERS[key][0].split("/")[-1]
        require(local["source_member_sha256"][filename] == MEMBERS[key][1],
                "The native review uses the selected actual word")
    for orientation in ("forward", "backward"):
        ledger = local["original_word_frame_ledgers"][orientation]
        require((ledger["arbitrary_persistent_inputs"], ledger["exact_scalar_input_columns"],
                 ledger["private_outputs"]) == (704, 712, "zero"),
                "The complete arbitrary-input local contract")
    require(doubled["source_square"] == "I for every positive lambda", "The source phase is an involution")
    native = local["fused_native_recipe_review"]
    payloads = {
        "WALSH-RETARGET-NATIVE.json.gz": native["payload_sha256"],
        "WALSH-RETARGET-HELPER-NORMALIZATION.json": native["helper_normalization_sha256"],
        "DOUBLED-WALSH-NATIVE.json.gz": doubled["explicit_emission"]["payload_sha256"],
    }
    for name, expected in payloads.items():
        require(content_digest(args.evidence/name) == expected, "The reviewed native payload: "+name)
    require(doubled["base_native_payload_sha256"] == native["payload_sha256"]
            == doubled["explicit_emission"]["source_native_payload_sha256"],
            "Doubled native factor provenance")
    require(doubled["explicit_emission"]["source_helper_normalization_sha256"]
            == native["helper_normalization_sha256"], "Doubled complete-helper provenance")
    return values, reviews, review_hashes, payloads


def emit(args):
    source, reviews, review_hashes, payloads = load(args)
    local_review_hash = review_hashes["WALSH-RETARGET-REVIEW.json"]
    doubled_review_hash = review_hashes["DOUBLED-WALSH-REVIEW.json"]
    t, old, word = (source[k] for k in ("template", "phases", "word"))
    require((t["m"], t["live"], t["physical"]) == (73, 14336, 14826), "Selected stock")
    require(len(t["calls"]) == 144 and len(t["execution_schedule"]) == 482,
            "Complete selected schedule")
    require(word["ports"] == [r["q"] for r in old["recipes"]], "Actual port labels")
    identity = [[int(i == j) for j in range(8)] for i in range(8)]
    require(controller_matrix(t["recipe"]) == identity, "Exact full scalar controller")
    require(controller_matrix(t["recipe"], True) != identity, "Wrong bridge sign control")
    bases, pending, phase_recipes = [], {}, []
    for port, q in enumerate(word["ports"]):
        basis = port_basis(q)
        bases.append(basis)
        routes = []
        for stage in range(9):
            columns = route_columns(basis, stage)
            require(multiply(columns, q) == q, "A data route fixes its port")
            require(all(multiply(columns, v) == 1 << j for j, v in enumerate(columns)),
                    "A data route is an involution")
            require(columns == transpose(columns), "A data route is orthogonal")
            before = basis[1:8*stage+1]
            background = [1 << j for j in range(9, 9+8*stage)]
            require({multiply(columns, v) for v in before} == set(background),
                    "Exact stage background axes")
            after = basis[1:8*(stage+1)+1]
            require({multiply(columns, v) for v in after} == set(basis[1:9]+background),
                    "Exact stage exit axes")
            routes.append(dict(stage=stage, matrix_columns=double_columns(columns),
                               cover_owner="d*rho", entry_translation=0,
                               exit_translation=0, global_unit_exponent=0,
                               local_background_axes=list(range(18, 18+16*stage)),
                               source_rank=2, local_rank=18, hole_rank=16))
        idle = []
        for child, frame in enumerate(old["recipes"][port]["idle_children"]):
            indices = [basis.index(v) for v in frame["orthogonal_axes"]]
            require(len(indices) == len(set(indices)) == frame["rank"], "Exact old idle axes")
            require(0 not in indices, "No idle child changes the port plane")
            pending[port, child] = indices
            idle.append(dict(child=child, rank=2*len(indices),
                             chart_axis_indices=[2*i+c for i in indices for c in (0, 1)],
                             translation_after=0, global_unit_exponent=0))
        phase_recipes.append(dict(port=port, q_plane=[double_vector(q, c) for c in (0, 1)],
                                  orthogonal_chart_columns=double_columns(basis), stages=routes,
                                  idle_children=idle, terminal_Y_translation=0))

    calls = t["calls"]
    rows = t["hosting"]["pooled_slots"]
    require(len(rows) == 69120, "Every selected helper role")
    widths = [len(word["frames"][word["final"][j]])-len(word["frames"][word["start"][j]])
              for j in range(224, 704)]
    require(widths == t["local_providers"]["gauge44"]["widths"], "Actual residual widths")
    by_call, by_idle = defaultdict(list), defaultdict(list)
    helper_jobs, idle_jobs, chart_recipes = [], [], {}
    owner_child_pair, owner_child_side = {}, {}
    deadlines, positions, releases, last_touch = {}, {}, {}, {}
    projection = defaultdict(list)
    for position, event in enumerate(t["execution_schedule"]):
        replica, kind = event.get("replica"), event["kind"]
        if replica is None:
            continue
        projection[replica].append(event["source_event"])
        if kind == "local_cover_sweep":
            call = calls[event["time"]]
            positions[event["time"]] = position
            last_touch[replica, call["pair"]] = position
        elif kind == "bridge":
            last_touch[replica, event["src"]] = last_touch[replica, event["dst"]] = position
        elif kind == "idle_cover_sweep":
            for side, child in enumerate(event["child_indices"]):
                owner_child_pair[child], owner_child_side[child] = event["pair"], side
                deadlines[replica, child] = position
                releases[replica, child] = last_touch.get((replica, event["pair"]), -1)
    require(all(projection[r] == list(range(30)) for r in range(16)), "Every replica source order")
    for index, row in enumerate(rows):
        time, helper, port, child = (row[k] for k in ("time", "helper", "port", "child"))
        owner, width, offset = (row[k] for k in ("owner_replica", "width", "offset"))
        require(width == widths[helper], "Complete helper width")
        require(releases[owner, child] < positions[time] < deadlines[owner, child],
                "Strict original whole-family owner window")
        family = owner*896+(2*owner_child_pair[child]+owner_child_side[child])*112+port
        require(row["family"] == family and row["copy"] == 112*owner+port,
                "Exact helper family and copy")
        occupied = pending[port, child][offset:offset+width]
        require(len(occupied) == width, "Complete hosted slice")
        spectators = [i for i in range(73) if i not in occupied][:9-width]
        route = [3, child, offset] if width == 9 else [4, child, offset, width, spectators]
        require(calls[time]["owners"][224+helper] == [family, route], "Actual selected helper route")
        order = occupied+spectators+[i for i in range(73) if i not in occupied+spectators]
        require(sorted(order) == list(range(73)), "Whole owner address permutation")
        chart_key = ":".join(map(str, (port, child, offset, width)))
        chart_recipes[chart_key] = dict(port=port, old_axis_order=order,
                                        doubled_axis_order=[2*i+c for i in order for c in (0, 1)],
                                        matrix_columns="orthogonal_chart_columns[doubled_axis_order]",
                                        inverse_matrix_rows="orthogonal_chart_columns[doubled_axis_order]",
                                        cover_owner="d*sigma^-1", invocation_class="g*sigma", rank=2*width)
        record = dict(source_role=index, time=time, helper=helper, family=family,
                      chart=chart_key, rank=2*width, child=child,
                      pending_offset=2*offset, operator="Gamma", translation_after=0)
        helper_jobs.append(record)
        by_call[time].append((family, mask(occupied)))
    for index, row in enumerate(t["idle_children"]):
        port, child, offset, rank = (row[k] for k in ("port", "child", "pending_offset", "rank"))
        axes = pending[port, child][offset:]
        require(len(axes) == rank and row["replicas"] == 1, "Exact complete idle remainder")
        by_idle[row["replica"], child].append((row["family"], mask(axes)))
        idle_jobs.append(dict(source_remainder=index, family=row["family"], port=port,
                              child=child, pending_offset=2*offset, rank=2*rank,
                              operator="Gamma", chart_axis_indices=[2*i+c for i in axes for c in (0, 1)],
                              translation_after=0))

    frames = [int((family//112) % 2 == 0) for family in range(14336)]
    initial_frames = frames.copy()
    logical = [[[int(i == j) for j in range(8)] for i in range(8)] for _ in range(16)]
    events, checkpoints, counts = [], [], Counter()

    def add_axes(family, axes):
        require(not (frames[family] & axes), "An owner applies only new disjoint Walsh axes")
        frames[family] |= axes

    for position, event in enumerate(t["execution_schedule"]):
        kind, replica = event["kind"], event.get("replica")
        output = dict(event)
        if kind == "local_cover_sweep":
            call = calls[event["time"]]
            stage, pair, time = (call[k] for k in ("stage", "pair", "time"))
            require((call["replica"], event["stage"], event["provider_id"]) ==
                    (replica, stage, "gauge44"), "Exact selected invocation")
            require(call["orientation"] == ("backward" if stage % 2 else "forward"), "Orientation")
            require(call["window"] == dict(local_axes=list(range(9)),
                                           prefix_axes=list(range(9, 9+8*stage))), "Local window")
            require(len({o[0] for o in call["owners"]}) == 704, "No complete-call owner alias")
            for side in range(2):
                for port in range(112):
                    family = replica*896+(2*pair+side)*112+port
                    require(call["owners"][112*side+port] == [family, [1, stage, port]],
                            "Actual active data owner and route")
                    require(frames[family] == level_mask(stage-1, side), "Actual data entrance frame")
                    add_axes(family, mask(range(8*stage+1, 8*stage+9)))
                    require(frames[family] == level_mask(stage, side), "Actual data exit frame")
                    counts["data_endpoint_bindings"] += 1
            x = 2*pair
            target, origin, coefficient = ((x, x+1, -1) if stage % 2 else (x+1, x, 1))
            matrix_add(logical[replica], target, origin, coefficient)
            for family, axes in by_call[time]:
                add_axes(family, axes)
                counts["helper_jobs"] += 1
            output["entry_exit_phase_adapters"] = "DATA-PHASES: identity"
            output["native_provider"] = "normalized_doubled_walsh"
            checkpoints.append(dict(position=position, replica=replica, stage=stage,
                                    entry_masks=[level_mask(stage-1, side) for side in range(2)],
                                    exit_masks=[level_mask(stage, side) for side in range(2)]))
        elif kind == "idle_cover_sweep":
            pair = event["pair"]
            for side, child in enumerate(event["child_indices"]):
                for family, axes in by_idle[replica, child]:
                    add_axes(family, axes)
                    counts["idle_remainders"] += 1
                for port in range(112):
                    family = replica*896+(2*pair+side)*112+port
                    require(frames[family] == level_mask(event["to_level"], side),
                            "Hosted prefix and idle suffix complete the exact frame")
            output["translation_after"] = 0
        elif kind == "bridge":
            dst, src, c = event["dst"], event["src"], event["coefficient"]
            for port in range(112):
                for side in range(2):
                    a, b = (replica*896+(2*p+side)*112+port for p in (dst, src))
                    require(frames[a] == frames[b], "Exact common-frame bridge access")
                    counts["bridge_frame_checks"] += 1
            matrix_add(logical[replica], 2*dst, 2*src, c)
            matrix_add(logical[replica], 2*src+1, 2*dst+1, -c)
            output["scalar_word"] = [["add_X", dst, src, c], ["add_Y", src, dst, -c]]
        elif kind == "terminal_Y_translations":
            output = dict(kind="identity_phase_checkpoint", replica=replica,
                          time=event["time"], source_event=event["source_event"],
                          old_kind=kind, reason="Q_q^2=I")
        elif kind == "terminal":
            for pair in range(4):
                for port in range(112):
                    x = replica*896+2*pair*112+port
                    y = x+112
                    require((frames[x], frames[y]) == (FULL, FULL ^ 1), "Complete preterminal frames")
                    frames[x], frames[y] = frames[y], frames[x]
            terminal(logical[replica])
            require(logical[replica] == identity, "Actual terminal returns every logical input")
            output["scalar_word"] = ["X=Y", "Y=-old_X"]
        elif kind == "bank_padding_cover_sweep":
            require(t["bank_padding"]["families"] == t["bank_padding"]["children"] == [],
                    "No omitted productive bank stock")
        else:
            require(kind == "translate_every_live_family", "Known final cover event")
            output = dict(kind="identity_phase_checkpoint", source_event=event["source_event"],
                          old_kind=kind, reason="Exact orthogonal Walsh covariance")
        events.append(output)
        counts[kind] += 1
    require(counts["helper_jobs"] == 69120 and counts["idle_remainders"] == 7526,
            "All selected native owner jobs are executed")
    require(all((after ^ before) == FULL for before, after in zip(initial_frames, frames)),
            "Every raw productive input receives the full Walsh operator")
    paid = Counter()
    local_review = reviews["WALSH-RETARGET-REVIEW.json"]
    for call in calls:
        for rank, number in local_review["original_word_frame_ledgers"][call["orientation"]]["child_profile"].items():
            paid[2*int(rank)] += number
    paid.update(job["rank"] for job in idle_jobs)
    require(dict(paid) == {2:349604, 4:60192, 6:62585, 8:20448,
                           10:11808, 14:7, 16:1152, 96:4866}, "Complete doubled child profile")
    require(sum(r*n for r, n in paid.items()) == 2082816, "Complete doubled rank mass")

    # Old terminal translations are nontrivial in the new endpoint convention.
    q = word["ports"][0]
    input_bit = q & -q
    require(parity(q & input_bit) == 1, "Stale terminal translation changes an output sign")
    first_chart = bases[0]
    delta = sum((((v.bit_count()-1)//2) & 1) << i for i, v in enumerate(transpose(first_chart)))
    require(delta != 0, "An actual orthogonal chart has a nonzero old cover correction")
    require(parity(delta & (delta & -delta)) == 1,
            "Stale cover translation changes a Walsh output sign")
    direction_witness = None
    for key, chart in chart_recipes.items():
        basis = bases[chart["port"]]
        sigma = [basis[i] for i in chart["old_axis_order"]]
        inverse = transpose(sigma)
        require(all(multiply(inverse, v) == 1 << i for i, v in enumerate(sigma)),
                "The explicit inverse helper cover route gives the required axes")
        width = chart["rank"]//2
        wanted = mask(chart["old_axis_order"][:width])
        for j in range(width):
            wrong = multiply(transpose(basis), inverse[j])
            if wrong & ~wanted:
                direction_witness = dict(chart=key, local_axis=j, wrong_owner_axis=inverse[j],
                                         required_owner_axis=sigma[j], expected_chart_axes=wanted)
                break
        if direction_witness is not None:
            break
    require(direction_witness is not None, "Wrong helper route changes the actual pending subspace")

    phase_output = dict(schema="normalized-doubled-walsh-data-phases-v1", source_base=BASE,
                        source_archive_sha256=ARCHIVE, m=146, tensor_parameter="all positive mu",
                        coordinate_order="(old_axis,copy), copy=0,1", recipes=phase_recipes,
                        frame_operator="Gamma_U=i^(-dim(U)*mu) H_U^tensor(2mu)",
                        all_stage_translations=0, all_idle_translations=0,
                        all_terminal_port_translations=0, all_cover_translations=0)
    binding = dict(schema="selected-global-doubled-walsh-binding-v1", source_base=BASE,
                   source_archive_sha256=ARCHIVE, source_members={k: v[1] for k, v in MEMBERS.items()},
                   local_native_review_sha256=local_review_hash, doubled_native_review_sha256=doubled_review_hash,
                   local_native_payload_content_sha256=payloads,
                   parent_rank=146, live=14336, physical=14826,
                   original_scalar_streams_sha256=MEMBERS["programs"][1],
                   data_call_checkpoints=checkpoints, execution_schedule=events,
                   helper_chart_recipes=chart_recipes, helper_jobs=helper_jobs, idle_jobs=idle_jobs,
                   full_boundary=dict(pre="S_146^-1", post="i^(73*mu) S_146^-1",
                                      cover_representative="raw standard coordinates",
                                      count_per_productive_family=2),
                   local_native_lowering="Use the pinned doubled local recipe theorem, exact intrinsic endpoints, and complete Gamma residual normalizers.",
                   source_cover="{g tensor I_2: g in O(73,2)}", paid_profile=dict(sorted(paid.items())),
                   output_operator="F_(146mu) on each arbitrary productive array after the stated two boundary maps")
    args.out.mkdir(parents=True, exist_ok=True)
    phase_hash = save_gzip(args.out/"DATA-PHASES.json.gz", phase_output)
    binding["data_phase_content_sha256"] = phase_hash
    binding_hash = save_gzip(args.out/"GLOBAL-BINDING.json.gz", binding)
    receipt = dict(status="PASS_SELECTED_GLOBAL_DOUBLED_WALSH_BINDING", source_base=BASE,
                   source_archive_sha256=ARCHIVE, data_phase_content_sha256=phase_hash,
                   global_binding_content_sha256=binding_hash, source_member_sha256={k: v[1] for k, v in MEMBERS.items()},
                   local_native_review_sha256=local_review_hash, doubled_native_review_sha256=doubled_review_hash,
                   local_native_payload_content_sha256=payloads,
                   checked_counts=dict(counts), exact_data_charts=1008,
                   distinct_helper_chart_keys=len(chart_recipes), productive_endpoint_operators=14336,
                   scalar_controller_matrix=identity, paid_profile=dict(sorted(paid.items())),
                   paid_rank=2082816, productive_rank=2093056, rank_deficit=10240,
                   final_virtual_frames={"X": FULL ^ 1, "Y": FULL},
                   initial_virtual_frames={"X": 1, "Y": 0},
                   controls=dict(wrong_bridge_sign="changes the exact scalar endpoint",
                                 stale_terminal_translation=dict(port=0, old_q=q, witness_input=input_bit,
                                                                 doubled_translation=[double_vector(q,c) for c in (0,1)]),
                                 stale_cover_translation=dict(old_delta=delta, witness_input=delta & -delta),
                                 helper_route_direction=direction_witness),
                   scope="Exact global chart, frame, scalar-controller, owner-job, idle, and boundary binding for the unchanged selected scalar word.",
                   not_checked=["A flattened global instruction tape or an all-size execution engine",
                                "The independent finite invoice and analytic supplier admission",
                                "A changed centre-free controller or a new kappa value"])
    (args.out/"GLOBAL-CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(receipt["status"])
    print(json.dumps({"calls":counts["local_cover_sweep"], "owner_jobs":counts["helper_jobs"],
                      "idle_remainders":counts["idle_remainders"], "paid_rank":receipt["paid_rank"],
                      "old_C_phase_maps_retained":0}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=PACKAGE.parents[1])
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--out", type=Path, default=PACKAGE/"evidence")
    args = parser.parse_args()
    if args.evidence is None:
        args.evidence = args.out
    emit(args)
