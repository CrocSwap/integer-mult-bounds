"""Check the complete doubled Walsh frame history from the selected archive.

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


ARCHIVE_HASH = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
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



def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return (x & y).bit_count() % 2


def apply(columns, x):
    out = 0
    while x:
        bit = x & -x
        out ^= columns[bit.bit_length()-1]
        x ^= bit
    return out


def transpose(columns):
    return [sum(((v >> i) & 1) << j for j, v in enumerate(columns)) for i in range(73)]


def basis(q):
    zero = next(i for i in range(9) if not (q >> i) & 1)
    transvection = q ^ (1 << zero)
    result = []
    for i in range(73):
        v = 1 << i
        if i == 0:
            v = 1 << zero
        elif i == zero:
            v = 1
        result.append(v ^ (transvection if dot(v, transvection) else 0))
    require(result[0] == q, "The first chart axis is the actual port")
    require(all(dot(v, w) == (i == j) for i, v in enumerate(result)
                for j, w in enumerate(result)), "The owner basis is orthogonal")
    return result


def project(axes):
    return tuple(apply(axes, sum(dot(v, 1 << i) << j for j, v in enumerate(axes)))
                 for i in range(73))


def route(v, stage, chart):
    if not stage:
        return v
    start = 9+8*(stage-1)
    out = v
    for j, b in enumerate(chart[1:9]):
        e = 1 << (start+j)
        if dot(v, b) != dot(v, e):
            out ^= b ^ e
    return out


def doubled(v, copy):
    return sum(1 << (2*i+copy) for i in range(73) if (v >> i) & 1)


def read_payload(path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw), sha256(raw).hexdigest()


def native_dependencies(out):
    reviews, review_hashes = {}, {}
    for name in ("WALSH-RETARGET-REVIEW.json", "DOUBLED-WALSH-REVIEW.json"):
        reviews[name], review_hashes[name] = read_payload(out/name)
    native = reviews["WALSH-RETARGET-REVIEW.json"]
    double = reviews["DOUBLED-WALSH-REVIEW.json"]
    require(native["status"] == "PASS_INDEPENDENT_WALSH_RETARGET_FRAMES_AND_ACTUAL_WORD_LEDGER",
            "The native arbitrary-input contract passed")
    require(double["status"] == "PASS_EXACT_DOUBLED_WALSH_NATIVE_LOWERING", "The doubled lowering passed")
    require(native["source_base"] == sources.BASE and native["source_archive_sha256"] == sources.LOCAL_ARCHIVE_SHA256,
            "Pinned local source provenance")
    for key in ("word", "programs"):
        require(native["source_member_sha256"][MEMBERS[key][0].rsplit("/", 1)[1]] == MEMBERS[key][1],
                "Local native review uses the selected word and both programs")
    for orientation in ("forward", "backward"):
        ledger = native["original_word_frame_ledgers"][orientation]
        require((ledger["arbitrary_persistent_inputs"], ledger["exact_scalar_input_columns"], ledger["private_outputs"])
                == (704, 712, "zero"), "Complete persistent and private input contract")
    require(double["source_square"] == "I for every positive lambda", "All-size involutive source phase")
    base = native["fused_native_recipe_review"]
    emitted = double["explicit_emission"]
    payloads = {
        "WALSH-RETARGET-NATIVE.json.gz": base["payload_sha256"],
        "WALSH-RETARGET-HELPER-NORMALIZATION.json": base["helper_normalization_sha256"],
        "DOUBLED-WALSH-NATIVE.json.gz": emitted["payload_sha256"],
    }
    for name, pin in payloads.items():
        _, actual = read_payload(out/name)
        require(actual == pin, "Actual reviewed native payload "+name)
    require(double["base_native_payload_sha256"] == emitted["source_native_payload_sha256"]
            == base["payload_sha256"], "Doubled native factors use the reviewed base")
    require(emitted["source_helper_normalization_sha256"] == base["helper_normalization_sha256"],
            "Doubled helper normalizers use the reviewed base")
    return native, review_hashes, payloads


def emitted_check(args, template, phases, charts, source_profiles, review_hashes, native_payloads):
    records, hashes = {}, {}
    for name in ("DATA-PHASES.json.gz", "GLOBAL-BINDING.json.gz", "GLOBAL-CHECKS.json"):
        records[name], hashes[name] = read_payload(args.out/name)
    data = records["DATA-PHASES.json.gz"]
    binding = records["GLOBAL-BINDING.json.gz"]
    checks = records["GLOBAL-CHECKS.json"]
    require(checks["status"] == "PASS_SELECTED_GLOBAL_DOUBLED_WALSH_BINDING", "Producer completion status")
    for record in (data, binding, checks):
        require(record["source_base"] == sources.BASE and record["source_archive_sha256"] == ARCHIVE_HASH,
                "Actual selected source provenance")
    require(data["m"] == binding["parent_rank"] == 146, "Emitted parent rank")
    require((binding["live"], binding["physical"]) == (14336, 14826), "Emitted stock")
    require(binding["source_members"] == {k: v[1] for k, v in MEMBERS.items()}, "All binding source hashes")
    for record in (binding, checks):
        require(record["local_native_review_sha256"] == review_hashes["WALSH-RETARGET-REVIEW.json"] and
                record["doubled_native_review_sha256"] == review_hashes["DOUBLED-WALSH-REVIEW.json"],
                "Both exact local native contracts")
        require(record["local_native_payload_content_sha256"] == native_payloads, "All actual native payloads")
        require(record["data_phase_content_sha256"] == hashes["DATA-PHASES.json.gz"], "Literal phase binding")
    require(checks["global_binding_content_sha256"] == hashes["GLOBAL-BINDING.json.gz"], "Literal global binding")
    require(binding["original_scalar_streams_sha256"] == MEMBERS["programs"][1], "Unchanged scalar streams")
    require(len(data["recipes"]) == 112, "Every emitted port")
    for p, chart in enumerate(charts):
        recipe = data["recipes"][p]
        require(recipe["port"] == p and recipe["q_plane"] == [doubled(chart[0], c) for c in range(2)],
                "Both source-plane vectors")
        require(recipe["orthogonal_chart_columns"] == [doubled(v, c) for v in chart for c in range(2)],
                "Complete doubled port chart")
        require(len(recipe["stages"]) == 9 and recipe["terminal_Y_translation"] == 0, "Every stage and terminal")
        for s, item in enumerate(recipe["stages"]):
            expected = dict(stage=s, matrix_columns=[doubled(route(1 << i, s, chart), c)
                                                    for i in range(73) for c in range(2)],
                            cover_owner="d*rho", entry_translation=0, exit_translation=0,
                            global_unit_exponent=0, local_background_axes=list(range(18, 18+16*s)),
                            source_rank=2, local_rank=18, hole_rank=16)
            require(item == expected, "Every literal stage matrix and exact phase")
        expected_idle = []
        for i, old in enumerate(phases["recipes"][p]["idle_children"]):
            indices = [chart.index(v) for v in old["orthogonal_axes"]]
            expected_idle.append(dict(child=i, rank=2*len(indices), chart_axis_indices=[2*j+c for j in indices for c in range(2)],
                                      translation_after=0, global_unit_exponent=0))
        require(recipe["idle_children"] == expected_idle, "Every emitted complete idle chart")
    for field in ("all_cover_translations", "all_idle_translations", "all_stage_translations", "all_terminal_port_translations"):
        require(data[field] == 0, "No stale complex-frame translation")
    rows = template["hosting"]["pooled_slots"]
    require(len(binding["helper_jobs"]) == len(rows), "Every emitted helper job")
    expected_charts = {}
    for i, (row, job) in enumerate(zip(rows, binding["helper_jobs"])):
        p, child, off, width = (row[k] for k in ("port", "child", "offset", "width"))
        name = ":".join(map(str, (p, child, off, width)))
        pending = phases["recipes"][p]["idle_children"][child]["orthogonal_axes"]
        occupied = [charts[p].index(v) for v in pending[off:off+width]]
        spectators = [j for j in range(73) if j not in occupied][:9-width]
        order = occupied+spectators+[j for j in range(73) if j not in occupied+spectators]
        expected_charts[name] = dict(port=p, old_axis_order=order, doubled_axis_order=[2*j+c for j in order for c in range(2)],
                                    matrix_columns="orthogonal_chart_columns[doubled_axis_order]",
                                    inverse_matrix_rows="orthogonal_chart_columns[doubled_axis_order]",
                                    cover_owner="d*sigma^-1", invocation_class="g*sigma", rank=2*width)
        require(job == dict(source_role=i, time=row["time"], helper=row["helper"], family=row["family"], chart=name,
                            rank=2*width, child=child, pending_offset=2*off, operator="Gamma", translation_after=0),
                "Every emitted helper index, rank, route, and phase")
    require(binding["helper_chart_recipes"] == expected_charts, "Complete literal helper charts")
    require(len(binding["idle_jobs"]) == len(template["idle_children"]), "Every emitted idle suffix")
    for i, (old, job) in enumerate(zip(template["idle_children"], binding["idle_jobs"])):
        p, child, off = (old[k] for k in ("port", "child", "pending_offset"))
        axes = phases["recipes"][p]["idle_children"][child]["orthogonal_axes"][off:]
        require(job == dict(source_remainder=i, family=old["family"], port=p, child=child, pending_offset=2*off,
                            rank=2*old["rank"], operator="Gamma", chart_axis_indices=[2*charts[p].index(v)+c for v in axes for c in range(2)],
                            translation_after=0), "Every emitted idle operator")
    expected_events, checkpoints = [], []
    for i, original in enumerate(template["execution_schedule"]):
        event, kind = dict(original), original["kind"]
        if kind == "local_cover_sweep":
            event.update(entry_exit_phase_adapters="DATA-PHASES: identity", native_provider="normalized_doubled_walsh")
            s = original["stage"]
            checkpoints.append(dict(position=i, replica=original["replica"], stage=s,
                                    entry_masks=[(1 << (8*s+1))-1, (1 << (8*s+1))-2],
                                    exit_masks=[(1 << (8*s+9))-1, (1 << (8*s+9))-2]))
        elif kind == "idle_cover_sweep":
            event["translation_after"] = 0
        elif kind == "bridge":
            dst, src, c = (original[k] for k in ("dst", "src", "coefficient"))
            event["scalar_word"] = [["add_X", dst, src, c], ["add_Y", src, dst, -c]]
        elif kind == "terminal":
            event["scalar_word"] = ["X=Y", "Y=-old_X"]
        elif kind == "terminal_Y_translations":
            event = dict(kind="identity_phase_checkpoint", replica=original["replica"], time=original["time"],
                         source_event=original["source_event"], old_kind=kind, reason="Q_q^2=I")
        elif kind == "translate_every_live_family":
            event = dict(kind="identity_phase_checkpoint", source_event=original["source_event"], old_kind=kind,
                         reason="Exact orthogonal Walsh covariance")
        expected_events.append(event)
    require(binding["execution_schedule"] == expected_events, "Every emitted event, sign, and correction")
    require(binding["data_call_checkpoints"] == checkpoints, "Every emitted global frame checkpoint")
    require(binding["full_boundary"] == dict(pre="S_146^-1", post="i^(73*mu) S_146^-1",
                                             cover_representative="raw standard coordinates", count_per_productive_family=2),
            "Exact literal F boundary")
    paid = Counter()
    for call in template["calls"]:
        for r, n in source_profiles[call["orientation"]]["child_profile"].items():
            paid[2*int(r)] += n
    paid.update(2*x["rank"] for x in template["idle_children"])
    require(binding["paid_profile"] == {str(k): v for k, v in sorted(paid.items())}, "Emitted complete paid profile")
    require(checks["paid_profile"] == binding["paid_profile"] and
            checks["paid_rank"] == sum(r*n for r, n in paid.items()) == 2082816, "Complete receipt rank mass")
    return len(expected_charts), hashes


def main(args):
    pins = {name: pin for name, pin in MEMBERS.values()}
    raw = sources.archive_members(args.repo, sources.SELECTED_ARCHIVE, ARCHIVE_HASH, pins)
    source = {key: sources.decode_json(raw[name], name) for key, (name, _) in MEMBERS.items()}
    template, phases, word = (source[k] for k in ("template", "phases", "word"))
    native, review_hashes, native_payloads = native_dependencies(args.out)
    ports = word["ports"]
    require(ports == [r["q"] for r in phases["recipes"]], "Every actual source label")
    charts = [basis(q) for q in ports]
    require(len(ports) == 112 and template["live"] == 14336 and template["m"] == 73,
            "Selected dimensions")
    route_checks = 0
    for p, chart in enumerate(charts):
        q = chart[0]
        for stage in range(9):
            rho = [route(1 << i, stage, chart) for i in range(73)]
            require(all(apply(rho, v) == 1 << i for i, v in enumerate(rho)), "Data route involution")
            require(apply(rho, q) == q, "Data route fixes the source line")
            require(all(dot(v, w) == (i == j) for i, v in enumerate(rho)
                        for j, w in enumerate(rho)), "Data route is orthogonal")
            outside = [1 << i for i in range(9, 9+8*stage)]
            before = chart[1:1+8*stage]
            after = chart[1:1+8*(stage+1)]
            require(project([apply(rho, v) for v in before]) == project(outside), "Target entry frame")
            require(project([apply(rho, v) for v in [q]+before]) == project([q]+outside),
                    "Source entry frame")
            full = [1 << i for i in range(9)]+outside
            require(project([apply(rho, v) for v in [q]+after]) == project(full), "Source exit frame")
            require(project([apply(rho, v) for v in after]) == project(chart[1:9]+outside),
                    "Target exit frame")
            route_checks += 1

    rows_by_time, idle_by_key = defaultdict(list), defaultdict(list)
    for row in template["hosting"]["pooled_slots"]:
        rows_by_time[row["time"]].append(row)
    for child in template["idle_children"]:
        idle_by_key[child["replica"], child["child"]].append(child)
    native_charts = set()
    jobs = {}
    for time, rows in rows_by_time.items():
        call = template["calls"][time]
        require(len(rows) == 480 and len({o[0] for o in call["owners"]}) == 704,
                "Complete distinct owner set")
        for row in rows:
            p, child, off, width = (row[k] for k in ("port", "child", "offset", "width"))
            pending = phases["recipes"][p]["idle_children"][child]["orthogonal_axes"]
            axes = pending[off:off+width]
            require(len(axes) == width and row["family"] % 112 == p, "Complete pending slice")
            chart = charts[p]
            occupied = [chart.index(v) for v in axes]
            spectators = [i for i in range(73) if i not in occupied][:9-width]
            order = occupied+spectators+[i for i in range(73) if i not in occupied+spectators]
            sigma = tuple(chart[i] for i in order)
            native_charts.add(sigma)
            expected = [3, child, off] if width == 9 else [4, child, off, width, spectators]
            require(call["owners"][224+row["helper"]] == [row["family"], expected],
                    "Literal helper route and family")
            jobs[time, row["helper"]] = (row["family"], frozenset(axes))
    for sigma in native_charts:
        inverse = transpose(sigma)
        require(all(apply(inverse, v) == 1 << i for i, v in enumerate(sigma)),
                "Both helper chart directions are exact")
    counts = Counter()

    def replay(skip_job=None):
        frames = [{ports[f % 112]} if (f//112) % 2 == 0 else set() for f in range(14336)]
        scalar = [[[int(i == j) for j in range(8)] for i in range(8)] for _ in range(16)]
        observed = Counter()
        for event in template["execution_schedule"]:
            kind = event["kind"]
            replica = event.get("replica")
            if kind == "local_cover_sweep":
                time, stage = event["time"], event["stage"]
                call = template["calls"][time]
                pair = call["pair"]
                for side in range(2):
                    for p, chart in enumerate(charts):
                        f = replica*896+pair*224+side*112+p
                        before = set(chart[1:1+8*stage]) | ({chart[0]} if not side else set())
                        require(frames[f] == before, "Complete active entrance frame")
                        require(call["owners"][side*112+p] == [f, [1, stage, p]], "Literal data owner")
                        frames[f].update(chart[1+8*stage:1+8*(stage+1)])
                        observed["active_family_updates"] += 1
                for row in rows_by_time[time]:
                    address = time, row["helper"]
                    if address == skip_job:
                        continue
                    f, axes = jobs[address]
                    require(not frames[f] & axes, "A helper advances only unused orthogonal axes")
                    frames[f].update(axes)
                    observed["helper_jobs"] += 1
                    observed["helper_rank"] += len(axes)
                matrix = scalar[replica]
                x, y = 2*pair, 2*pair+1
                if call["orientation"] == "forward":
                    matrix[y] = [a+b for a, b in zip(matrix[y], matrix[x])]
                else:
                    require(call["orientation"] == "backward", "Actual local orientation")
                    matrix[x] = [a-b for a, b in zip(matrix[x], matrix[y])]
            elif kind == "idle_cover_sweep":
                for child in event["child_indices"]:
                    for item in idle_by_key[replica, child]:
                        f, p, off, rank = (item[k] for k in ("family", "port", "pending_offset", "rank"))
                        pending = phases["recipes"][p]["idle_children"][child]["orthogonal_axes"]
                        axes = set(pending[off:])
                        require(len(axes) == rank and not frames[f] & axes, "Exact unused idle suffix")
                        frames[f].update(axes)
                        observed["idle_remainders"] += 1
            elif kind == "bridge":
                src, dst, c = (event[k] for k in ("src", "dst", "coefficient"))
                for side in range(2):
                    for p in range(112):
                        a, b = (replica*896+pair*224+side*112+p for pair in (src, dst))
                        require(frames[a] == frames[b], "Exact common bridge frames")
                        observed["bridge_accesses"] += 1
                matrix = scalar[replica]
                matrix[2*dst] = [a+c*b for a, b in zip(matrix[2*dst], matrix[2*src])]
                matrix[2*src+1] = [a-c*b for a, b in zip(matrix[2*src+1], matrix[2*dst+1])]
            elif kind == "terminal":
                matrix = scalar[replica]
                for pair in range(4):
                    for p in range(112):
                        x = replica*896+pair*224+p
                        frames[x], frames[x+112] = frames[x+112], frames[x]
                    x, y = 2*pair, 2*pair+1
                    matrix[x], matrix[y] = matrix[y], [-a for a in matrix[x]]
            elif kind == "bank_padding_cover_sweep":
                require(template["bank_padding"]["children"] == [], "No unexamined bank padding")
            else:
                require(kind in ("terminal_Y_translations", "translate_every_live_family"),
                        "Every source event has a new meaning")
                observed["old_correction_events_replaced_by_identity"] += 1
        require(all(matrix == [[int(i == j) for j in range(8)] for i in range(8)] for matrix in scalar),
                "Full signed scalar controller is the identity")
        for f, frame in enumerate(frames):
            chart = charts[f % 112]
            expected = set(chart[1:] if (f//112) % 2 == 0 else chart)
            require(frame == expected, "Final frame times inverse initial frame is full Gamma")
        return observed

    counts.update(replay())
    require((counts["helper_jobs"], counts["idle_remainders"]) == (69120, 7526), "All productive advances")
    negative = []
    try:
        replay(skip_job=(0, 0))
    except ValueError as error:
        negative.append({"control": "omit_one_complete_helper_job", "rejection": str(error)})
    else:
        raise ValueError("The omitted helper job was not detected")
    emitted_charts, emitted_hashes = emitted_check(
        args, template, phases, charts, native["original_word_frame_ledgers"], review_hashes, native_payloads)
    result = {
        "status": "PASS_INDEPENDENT_SELECTED_GLOBAL_WALSH_HISTORY",
        "source_archive_sha256": ARCHIVE_HASH,
        "source_members": {k: {"path": v[0], "sha256": v[1]} for k, v in MEMBERS.items()},
        "source_base": sources.BASE,
        "emitted_artifact_content_sha256": emitted_hashes,
        "local_native_review_sha256": review_hashes,
        "local_native_payload_content_sha256": native_payloads,
        "emitted_helper_chart_keys": emitted_charts,
        "data_port_stage_charts": route_checks,
        "distinct_helper_maps_and_inverses": len(native_charts),
        "physical_productive_families": 14336,
        "source_events": len(template["execution_schedule"]),
        "counts": dict(sorted(counts.items())),
        "negative_controls": negative,
        "exact_phase_rule": "Gamma is the real normalized Walsh kernel on each nondegenerate axis subspace. Orthogonal covariance and disjoint product identities have scalar +1.",
        "helper_route_rule": "If sigma maps coordinate child axes to owner axes, d=g sigma and owner g=d sigma^-1. Both chart directions are verified.",
        "endpoint_rule": "X input type Q and Y input type I; after signed exchange X type Gamma_full Q and Y type Gamma_full. Q^2=I gives physical Gamma_full on all arbitrary inputs.",
        "scope": "Global data and productive owner histories for the unchanged selected scalar word. The reviewed local arbitrary-input doubled-Walsh contract and full finite invoice are separate dependencies. No phase-gap controller or new kappa is admitted."
    }
    (args.out/"GLOBAL-WALSH-REVIEW.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"])
    print("families=14336 events=482 helpers=69120 idle_remainders=7526")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=PACKAGE.parents[1])
    parser.add_argument("--out", type=Path, default=PACKAGE/"evidence")
    main(parser.parse_args())
