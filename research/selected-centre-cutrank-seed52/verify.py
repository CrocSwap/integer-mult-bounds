#!/usr/bin/env python3
"""Replay the selected #1094 centre block against the scalar cut-rank bound."""
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
WORD_MEMBER = "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz"
PROGRAM_MEMBER = "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
WORD_GZ_SHA256 = "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"
PROGRAM_GZ_SHA256 = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"


class AuditError(ValueError):
    pass


def require(test, message):
    if not test:
        raise AuditError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def exact_rank(matrix):
    """Sparse exact Gaussian elimination over Q."""
    pivots = {}
    for source in matrix:
        row = {i: Fraction(x) for i, x in enumerate(source) if x}
        while row:
            pivot = min(row)
            base = pivots.get(pivot)
            if base is None:
                scale = row[pivot]
                pivots[pivot] = {i: x / scale for i, x in row.items()}
                break
            scale = row[pivot]
            for i, x in base.items():
                value = row.get(i, Fraction(0)) - scale * x
                if value:
                    row[i] = value
                else:
                    row.pop(i, None)
    return len(pivots)


def exact_sparse_rank(rows):
    pivots = {}
    for source in rows:
        row = {i: Fraction(x) for i, x in source.items() if x}
        while row:
            pivot = min(row)
            base = pivots.get(pivot)
            if base is None:
                scale = row[pivot]
                pivots[pivot] = {i: x / scale for i, x in row.items()}
                break
            scale = row[pivot]
            for i, x in base.items():
                value = row.get(i, Fraction(0)) - scale * x
                if value:
                    row[i] = value
                else:
                    row.pop(i, None)
    return len(pivots)


def checked_entry_rank(rows, expected):
    rank = exact_sparse_rank(rows)
    require(rank == expected, "selected source and target values are not independent at entry")
    return rank


def rank_f2(matrix):
    """Separate frame-field diagnostic; never used for the Q scatter rank."""
    if not matrix:
        return 0
    rows = [sum((int(x) & 1) << j for j, x in enumerate(row)) for row in matrix]
    rank = 0
    for col in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(rows)) if (rows[i] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> col) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def extract(archive_bytes):
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        members = {}
        for name, pin in ((WORD_MEMBER, WORD_GZ_SHA256), (PROGRAM_MEMBER, PROGRAM_GZ_SHA256)):
            member = archive.extractfile(name)
            require(member is not None, "missing selected provider member: " + name)
            raw = member.read()
            require(sha256(raw) == pin, "selected provider member hash mismatch: " + name)
            members[name] = json.loads(gzip.decompress(raw))
    return members[WORD_MEMBER], members[PROGRAM_MEMBER]["forward"]


def apply_scalar(op, rows, private):
    tag, destination = op[0], op[1]
    dkind, dindex = destination
    target = rows if dkind == "L" else private
    get_row = lambda container, index: container[index] if isinstance(container, list) else container.get(index, {})
    if tag == "clear":
        target[dindex] = {}
    elif tag == "copy":
        skind, sindex = op[2]
        source = rows if skind == "L" else private
        target[dindex] = dict(get_row(source, sindex))
    elif tag == "scale":
        factor = Fraction(op[2], op[3])
        target[dindex] = {i: x * factor for i, x in get_row(target, dindex).items() if x * factor}
    elif tag == "add":
        skind, sindex = op[2]
        source = rows if skind == "L" else private
        factor = Fraction(op[3], op[4])
        out = dict(get_row(target, dindex))
        for i, x in get_row(source, sindex).items():
            value = out.get(i, Fraction(0)) + factor * x
            if value:
                out[i] = value
            else:
                out.pop(i, None)
        target[dindex] = out
    else:
        raise AuditError("unsupported scalar operation " + repr(tag))


def event_state(op, rows, private):
    apply_scalar(op, rows, private)


def read_prefix_rows(word, program):
    """Replay the exact pre-centre scalar prefix on all 704 independent L rows."""
    version = 2 * word["v"] + word["R"]
    rows = [{i: Fraction(1)} for i in range(version)]
    private = {}
    frames = list(word["start"])
    center_index = next((i for i, e in enumerate(program) if e == ["phase", "centers"]), None)
    require(center_index is not None, "missing emitted centres phase")
    for event in program[:center_index]:
        if event[0] == "scalar":
            event_state(event[1], rows, private)
        elif event[0] == "climb":
            _, _part, register, old, new, cost = event
            require(frames[register] == old, "pre-centre frame trace has a broken edge")
            require(cost >= 0, "negative frame-transition price")
            frames[register] = new
        elif event[0] == "adapter":
            _, _kind, register, frame = event
            require(frames[register] == frame, "adapter is assigned to the wrong logical frame")
        elif event[0] == "residual_adapter":
            _, _kind, register, frame, *_ = event
            require(frames[register] == frame, "residual adapter is assigned to the wrong logical frame")
    return rows, private, frames, center_index


def make_scatter(word, centers, targets):
    col = {register: i for i, register in enumerate(centers)}
    row = {register: i for i, register in enumerate(targets)}
    matrix = [[Fraction(0) for _ in centers] for _ in targets]
    for event in word["cut"]:
        require(event[0] == "add" and event[2] in col and event[1] in row,
                "unexpected canonical scatter event")
        matrix[row[event[1]]][col[event[2]]] += Fraction(event[3], event[4])
    return matrix


def simulate_centres(word, program, centers, targets, scatter):
    start = next(i for i, e in enumerate(program) if e == ["phase", "centers"])
    stop = next(i for i in range(start + 1, len(program)) if program[i] == ["phase", "B"])
    phase = program[start + 1:stop]
    rows = [{("L", i): Fraction(1)} for i in range(2 * word["v"] + word["R"])]
    private = {}
    center_events = [e for e in phase if e[0] == "center"]
    require(len(center_events) == len(centers), "wrong number of private centre transports")
    require(not any(e[0] == "climb" for e in phase), "unexpected ordinary-register frame change in centre interval")
    cursor = 0
    observed_mass = 0
    for k, carrier in enumerate(centers):
        frame = word["center_frames"][k]
        require(phase[cursor] == ["scalar", ["clear", ["C", k]], frame], "scratch preparation is missing or misplaced")
        event_state(phase[cursor][1], rows, private)
        cursor += 1
        require(phase[cursor] == ["scalar", ["copy", ["C", k], ["L", carrier]], frame], "carrier copy or frame is wrong")
        event_state(phase[cursor][1], rows, private)
        cursor += 1
        move = phase[cursor]
        require(move == ["center", k, frame, 0, 8], "centre scratch does not descend to the clean target frame")
        require(len(word["frames"][frame]) == 8 and len(word["frames"][0]) == 0,
                "frame heights do not match the emitted 8-to-0 move")
        observed_mass += move[4]
        cursor += 1
        seen = []
        while cursor < len(phase) and phase[cursor][0] == "scalar" and phase[cursor][1][0] == "add":
            event = phase[cursor]
            op, level = event[1], event[2]
            require(op[1][0] == "L" and op[2] == ["C", k] and level == 0,
                    "scatter edge is not a clean-frame target from this scratch")
            event_state(op, rows, private)
            seen.append((op[1][1], Fraction(op[3], op[4])))
            cursor += 1
        expected = [(e[1], Fraction(e[3], e[4])) for e in word["cut"] if e[2] == carrier]
        require(sorted(seen) == sorted(expected), "emitted rational scatter differs from the canonical selected word")
        require(len(seen) == 22 and len({r for r, _ in seen}) == 22,
                "selected carrier does not serve exactly 22 distinct targets")
        require(phase[cursor] == ["scalar", ["clear", ["C", k]], 0], "scratch is not cleared after its complete scatter")
        event_state(phase[cursor][1], rows, private)
        cursor += 1
    require(cursor == len(phase), "unaccounted operation in the centre interval")
    require(all(not row for row in private.values()), "private centre scratch is dirty at exit")
    require(observed_mass == 64, "unexpected emitted centre transport mass")
    for target_i, target in enumerate(targets):
        expected = {("L", target): Fraction(1)}
        for j, carrier in enumerate(centers):
            coefficient = scatter[target_i][j]
            if coefficient:
                expected[("L", carrier)] = coefficient
        require(rows[target] == expected, "centre phase output does not equal Y + S X")
    for carrier in centers:
        require(rows[carrier] == {("L", carrier): Fraction(1)}, "centre carrier is altered by its scatter block")
    return observed_mass, len(phase)


def analyze(word, program):
    centers = list(word["centers"])
    targets = sorted({e[1] for e in word["cut"]})
    require(len(centers) == 8 and len(set(centers)) == 8, "selected centre roster changed")
    require(len(targets) == 88 and not (set(centers) & set(targets)), "source and target boundary roles overlap")
    require(word["v"] == 112 and word["R"] == 480, "not the selected 480-helper provider")
    require(not word.get("target_levels", {}), "selected target levels are not all the zero frame")
    require(len(word["cut"]) == 176, "selected scatter no longer has 176 edges")
    for carrier in centers:
        terms = [e for e in word["cut"] if e[2] == carrier]
        require(len(terms) == 22 and len({e[1] for e in terms}) == 22, "scatter cardinality changed")
        require({Fraction(e[3], e[4]) for e in terms} <= {Fraction(-1, 4), Fraction(1, 4)},
                "unexpected rational scatter coefficient")

    prefix_rows, prefix_private, frames, _phase_start = read_prefix_rows(word, program)
    require(not prefix_private, "private scratch exists before the selected centre phase")
    complete_entry_rank = exact_sparse_rank(prefix_rows)
    require(complete_entry_rank == 2 * word["v"] + word["R"],
            "pre-centre ordinary register state is not an invertible Q-coordinate system")
    for k, carrier in enumerate(centers):
        require(frames[carrier] == word["center_frames"][k], "carrier is not at its selected source frame")
        require(len(word["frames"][frames[carrier]]) == 8, "carrier source frame is not height eight")
    for target in targets:
        require(frames[target] == 0, "target is not in the zero frame at centre-phase entry")
    entry_registers = centers + targets
    require(len(set(entry_registers)) == 96, "entry-boundary register selection overlaps")
    entry_rank = checked_entry_rank([prefix_rows[r] for r in entry_registers], 96)

    scatter = make_scatter(word, centers, targets)
    scatter_rank = exact_rank(scatter)
    require(scatter_rank == 8, "selected rational scatter does not have full column rank")
    transport_mass, phase_events = simulate_centres(word, program, centers, targets, scatter)
    q = 8
    floor = q * scatter_rank
    require(transport_mass >= floor, "emitted transport mass violates the conditional bound")
    return {
        "status": "PASS_SELECTED_CENTRE_CUTRANK_APPLICATION",
        "selected_pr1094_head": "0fc329d0bec93ca7cd288eaea1295172e8789810",
        "provider": "gauge44; 480 helpers; local forward program",
        "centres": centers,
        "targets": len(targets),
        "ordinary_entry_coordinates": 2 * word["v"] + word["R"],
        "ordinary_entry_rank_Q": complete_entry_rank,
        "entry_coordinates": len(entry_registers),
        "entry_rank_Q": entry_rank,
        "scatter_edges": len(word["cut"]),
        "scatter_rank_Q": scatter_rank,
        "carrier_height_q": q,
        "host_endpoint_term": 0,
        "conditional_transport_floor": floor,
        "observed_transport_mass": transport_mass,
        "phase_event_count_excluding_marker": phase_events,
        "scratch_registers_zero_at_both_boundaries": 8,
    }


def rejected(name, action):
    try:
        action()
    except (AuditError, KeyError, IndexError, ZeroDivisionError):
        return name
    raise AuditError("negative control escaped: " + name)


def run_controls(word, program):
    names = []

    def missing_scatter_edge():
        bad = deepcopy(word)
        bad["cut"].pop()
        analyze(bad, program)

    names.append(rejected("missing_scatter_edge", missing_scatter_edge))

    def wrong_source_frame():
        bad = deepcopy(word)
        bad["center_frames"][0] = 0
        analyze(bad, program)

    names.append(rejected("wrong_source_frame", wrong_source_frame))

    def nonzero_target_level():
        bad = deepcopy(word)
        target = next(e[1] for e in bad["cut"])
        bad["target_levels"] = {str(target - bad["v"]): 1}
        analyze(bad, program)

    names.append(rejected("nonzero_target_level", nonzero_target_level))

    def missing_scratch_clear():
        bad = deepcopy(program)
        start = next(i for i, e in enumerate(bad) if e == ["phase", "centers"])
        stop = next(i for i in range(start + 1, len(bad)) if bad[i] == ["phase", "B"])
        clear = next(i for i in range(stop - 1, start, -1)
                     if bad[i][0] == "scalar" and bad[i][1][0] == "clear")
        del bad[clear]
        analyze(word, bad)

    names.append(rejected("missing_scratch_clear", missing_scratch_clear))

    def omitted_carrier_column():
        bad = deepcopy(word)
        carrier = bad["centers"][0]
        bad["cut"] = [e for e in bad["cut"] if e[2] != carrier]
        matrix = make_scatter(bad, bad["centers"], sorted({e[1] for e in bad["cut"]}))
        require(exact_rank(matrix) == 7, "omitting a complete source column did not lower Q rank")
        analyze(bad, program)

    names.append(rejected("omitted_carrier_column", omitted_carrier_column))

    dependent = [{i: Fraction(1)} for i in range(96)]
    dependent[-1] = dict(dependent[-2])
    names.append(rejected("dependent_entry_rejected", lambda: checked_entry_rank(dependent, 96)))

    field_witness = [[1, 1], [1, -1]]
    require(exact_rank(field_witness) == 2 and rank_f2(field_witness) == 1,
            "field-separation control failed")
    names.append("Q_rank_not_inferred_from_F2")
    return names


def main():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    archive_path = ROOT / ARCHIVE
    archive_bytes = archive_path.read_bytes()
    pinned_archive = next(x["sha256"] for x in sources["files"] if x["path"] == ARCHIVE)
    require(sha256(archive_bytes) == pinned_archive, "selected replay archive differs from base pin")
    word, program = extract(archive_bytes)
    result = analyze(word, program)
    result["selected_archive_sha256"] = sha256(archive_bytes)
    result["canonical_word_gzip_sha256"] = WORD_GZ_SHA256
    result["local_programs_gzip_sha256"] = PROGRAM_GZ_SHA256
    result["negative_controls"] = run_controls(word, program)
    expected = json.loads((PACKAGE / "EXPECTED.json").read_text(encoding="utf-8"))
    require(result == expected, "computed application differs from the committed exact receipt")
    print("PASS_SELECTED_CENTRE_CUTRANK_APPLICATION "
          f"centres={len(result['centres'])} targets={result['targets']} "
          f"entry_rank_Q={result['entry_rank_Q']} rank_Q={result['scatter_rank_Q']} "
          f"floor={result['conditional_transport_floor']} transport={result['observed_transport_mass']} "
          f"controls={len(result['negative_controls'])}")


if __name__ == "__main__":
    main()
