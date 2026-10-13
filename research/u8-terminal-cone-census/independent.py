"""Independent exact terminal-cone census, using dyadic matrix columns.

No imports from the primary census or supplier verifiers. GF(2) spaces are
enumerated as sets of all their vectors, rather than Gaussian rank tests.
Prepared with OpenAI Codex assistance for ToikY. Apache-2.0.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import time

WORD_SHA = "090fd574747fbf9628e70cb9beb792732914cfa52e1df147579fe4dbccc68c5a"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dyadic(num, den):
    need(den != 0, "zero denominator")
    if den < 0:
        num, den = -num, -den
    need(den & (den - 1) == 0, "non-dyadic coefficient")
    exponent = den.bit_length() - 1
    if num:
        factor = (abs(num) & -abs(num)).bit_length() - 1
        num >>= factor
        exponent -= factor
    return num, exponent


def fraction_pair(num, exponent):
    if not num:
        return 0, 1
    factor = (abs(num) & -abs(num)).bit_length() - 1
    num >>= factor
    exponent -= factor
    return (num << -exponent, 1) if exponent < 0 else (num, 1 << exponent)


def plus(left, right, num=1, exponent=0):
    """Column vectors are (integer dictionary, shared denominator exponent)."""
    ld, le = left
    rd, re = right
    re += exponent
    e = max(le, re)
    out = {k: a << (e - le) for k, a in ld.items()}
    for k, b in rd.items():
        a = out.get(k, 0) + num * (b << (e - re))
        if a:
            out[k] = a
        else:
            out.pop(k, None)
    return out, e


def scalar(g, inverse=False):
    n, d = g[3:5] if g[0] == "add" else g[2:4]
    if inverse:
        if g[0] == "add":
            n = -n
        else:
            n, d = d, n
    n, e = dyadic(n, d)
    need(n != 0, "zero scalar primitive")
    return n, e


def columns(gates, size, inverse=False):
    """Right-multiply elementary matrices: chronological gates go in reverse.

    For a shear t += c*s, M*G changes column s, by c times column t.
    Inverse factors are right-multiplied in original chronological order.
    """
    result = [({q: 1}, 0) for q in range(size)]
    seq = gates if inverse else reversed(gates)
    for g in seq:
        n, e = scalar(g, inverse)
        if g[0] == "add":
            t, s = g[1:3]
            need(t != s and 0 <= t < size and 0 <= s < size, "invalid shear")
            result[s] = plus(result[s], result[t], n, e)
        elif g[0] == "scale":
            q = g[1]
            vals, old_e = result[q]
            result[q] = ({k: n * a for k, a in vals.items()}, old_e + e)
        else:
            raise ValueError("unknown primitive")
    return result


def canon_columns(matrix):
    return [{q: fraction_pair(n, e) for q, n in col.items()} for col, e in matrix]


def matrix_sha(matrix):
    return hashlib.sha256(json.dumps(canon_columns(matrix), sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=None)
def space(generators):
    members = {0}
    for g in generators:
        need(isinstance(g, int) and 0 <= g < 512, "GF2 vector out of range")
        members |= {x ^ g for x in members}
    return frozenset(members)


@lru_cache(maxsize=None)
def basis(members):
    # The smallest vector of each leading-bit class is its reduced pivot.
    return tuple(min(x for x in members if x.bit_length() == b)
                 for b in range(9, 0, -1)
                 if any(x.bit_length() == b for x in members))


def dimension(members):
    need(len(members) & (len(members) - 1) == 0, "not a subspace cardinality")
    return len(members).bit_length() - 1


def join(spaces):
    out = space(())
    for s in spaces:
        if not s <= out:
            out = space(tuple(basis(out)) + tuple(basis(s)))
    return out


def touched(g):
    return g[1:3] if g[0] == "add" else g[1:2]


def frames(word, v, helpers):
    full = space(tuple(1 << b for b in range(9)))
    start = [space((q,)) for q in word["ports"]] + [space(())] * (v + helpers)
    for q, f in word.get("start_extra", {}).items():
        start[int(q)] = space(tuple(f))
    end = [full] * v + [frozenset(x for x in range(512)
                                if (x & port).bit_count() % 2 == 0)
                       for port in word["ports"]] + [full] * helpers
    for q, f in word.get("helper_final", {}).items():
        end[int(q)] = space(tuple(f))
    cur, paid = list(start), Counter()

    def ascend(q, f):
        need(cur[q] <= f, "nonmonotone frame")
        d = dimension(f) - dimension(cur[q])
        if d:
            paid[d] += 1
        cur[q] = f

    for section in ("A", "B"):
        if section == "B":
            levels = {int(q): space(tuple(f)) for q, f in word.get("target_levels", {}).items()}
            need(all(cur[v + q] == levels.get(q, space(())) for q in range(v)), "target boundary")
            for q, raw in zip(word["centers"], word["center_frames"]):
                f = space(tuple(raw))
                need(cur[q] == f, "center boundary")
                children = {levels.get(g[1] - v, space(())) for g in word["cut"] if g[2] == q}
                for child in sorted(children, key=lambda x: -dimension(x)):
                    need(child <= f, "non-nested center child")
                    if child != f:
                        paid[dimension(f) - dimension(child)] += 1
                    f = child
        for g in word[section]:
            for q in touched(g):
                ascend(q, space(tuple(g[-1])))
    end_b = list(cur)
    early = word.get("early_cleanup", [])
    early_ids = {i for i, _ in early}
    need(len(early_ids) == len(early), "repeated early cleanup index")
    tail = [word["cleanup"][i][:-1] + [f] for i, f in early]
    cleanup = [g for i, g in enumerate(word["cleanup"]) if i not in early_ids]
    for g in tail:
        for q in touched(g):
            ascend(q, space(tuple(g[-1])))
    for q, f in enumerate(end):
        ascend(q, f)
    need(dict(paid) == {int(k): n for k, n in word["report"]["local_profile"].items()}, "profile mismatch")
    need(all(end[q] == full for g in cleanup for q in touched(g)), "cleanup beyond endpoint")
    return start, end_b, end, tail, cleanup, paid


def reconstruct(word):
    v, h, helpers = [word["report"][k] for k in ("v", "h", "R")]
    need((v, h, helpers) == (112, 9, 504), "wrong pinned geometry")
    size = 2 * v + helpers
    core = word["A"] + word["cut"] + word["B"]
    core_m = columns(core, size)
    pre_m = columns(word["precondition"], size)
    compensation = []
    # Compose the target-only response with the precondition as matrix columns.
    for helper in range(2 * v, size):
        response = ({}, 0)
        vals, exponent = core_m[helper]
        for q, n in vals.items():
            if v <= q < 2 * v:
                response = plus(response, pre_m[q], n, exponent)
        vals, exponent = response
        need(all(v <= q < 2 * v for q in vals), "compensation left target chart")
        for q, n in vals.items():
            a, b = fraction_pair(-n, exponent)
            compensation.append(["add", q, helper, a, b, []])
    compensation.sort(key=lambda g: (g[1], g[2]))
    prefix = word["precondition"] + compensation + core
    p, inv = columns(prefix, size), columns(prefix, size, True)
    start, end_b, end, tail, cleanup, paid = frames(word, v, helpers)
    complete = canon_columns(columns(prefix + tail + cleanup, size))
    expected = [{q: (1, 1), **({v + q: (1, 1)} if q < v else {})} for q in range(size)]
    need(complete == expected, "complete endpoint not exact on arbitrary columns")
    undo = []
    for g in reversed(prefix):
        n, e = scalar(g, True)
        a, b = fraction_pair(n, e)
        undo.append(["add", g[1], g[2], a, b, []] if g[0] == "add"
                    else ["scale", g[1], a, b, []])
    need(canon_columns(columns(prefix + undo, size)) == [{q: (1, 1)} for q in range(size)],
         "exact inverse composition failed")
    inv_rows = [[] for _ in range(size)]
    p_rows = [[] for _ in range(size)]
    for k, (col, _) in enumerate(inv):
        for q in col:
            inv_rows[q].append(k)
    for k, (col, _) in enumerate(p):
        for q in col:
            p_rows[q].append(k)
    records, row_records = [], []
    for q in range(2 * v, size):
        inverse_support = inv_rows[q]
        dirty_support = sorted(k for k in p[q][0] if k != q)
        row_cone = join(end_b[k] for k in [q] + inverse_support)
        both_cone = join([row_cone] + [end_b[k] for k in dirty_support])
        need(both_cone <= end[q], "existing endpoint fails joined admission cone")
        records.append({
            "helper": q - 2 * v, "register": q,
            "start_frame": list(basis(start[q])), "end_b_frame": list(basis(end_b[q])),
            "current_terminal_frame": list(basis(end[q])),
            "minimal_necessary_terminal_frame": list(basis(both_cone)),
            "inverse_row_support": inverse_support, "dirt_column_support": dirty_support,
            "current_width": dimension(end[q]) - dimension(start[q]),
            "minimal_necessary_width": dimension(both_cone) - dimension(start[q]),
            "terminal_dimension_slack": dimension(end[q]) - dimension(both_cone),
            "full_cleanup_incidence": sum(q in touched(g) for g in cleanup),
        })
        row_records.append({"helper": q - 2 * v, "register": q,
                            "row_only_frame": list(basis(row_cone)),
                            "row_only_dimension": dimension(row_cone),
                            "row_only_terminal_gap": dimension(end[q]) - dimension(row_cone)})
    return {
        "status": "PASS_INDEPENDENT_EXACT_COLUMN_CONE_CENSUS",
        "algorithm": "Right-composed sparse integer dyadic columns; all-vector GF2 subspaces; no primary or supplier code imports",
        "helper_count": helpers, "arbitrary_input_columns": size,
        "compensation_gates": len(compensation), "prefix_gates": len(prefix),
        "compensation_sha256": hashlib.sha256(json.dumps(compensation, separators=(",", ":")).encode()).hexdigest(),
        "forward_matrix_sha256": matrix_sha(p), "inverse_matrix_sha256": matrix_sha(inv),
        "exact_full_endpoint_identity": True, "exact_prefix_inverse_identity": True,
        "local_profile": dict(sorted(paid.items())),
        "current_width_inventory": dict(sorted(Counter(r["current_width"] for r in records).items())),
        "necessary_width_inventory": dict(sorted(Counter(r["minimal_necessary_width"] for r in records).items())),
        "dimension_slack_histogram": dict(sorted(Counter(r["terminal_dimension_slack"] for r in records).items())),
        "candidates": [r["helper"] for r in records if r["terminal_dimension_slack"]],
        "row_only_gap_histogram": dict(sorted(Counter(r["row_only_terminal_gap"] for r in row_records).items())),
        "row_only_gap_helpers": [r["helper"] for r in row_records if r["row_only_terminal_gap"]],
        "records": records, "row_only_records": row_records,
        "scope": "Exact finite census. Joined cone excludes smaller endpoints under retained row/column admission contract. Row-only information-flow claim and separately argued column invariant are documented in AUDIT.md; no sufficient cleanup or exponent claim.",
    }


def controls():
    out = []
    gates = [["add", 0, 1, 1, 2, []], ["add", 0, 1, -1, 2, []]]
    exact = canon_columns(columns(gates, 2))
    need(exact == [{0: (1, 1)}, {1: (1, 1)}], "cancellation positive control")
    # A support-only union mutant retains the cancelled (row0,column1) term.
    support_mutant = [{0}, {0, 1}]
    need(support_mutant != [set(c) for c in exact], "zero-union mutant escaped")
    out.append({"name": "exact_zero_cancellation", "positive": True, "negative_rejected": True,
                "cancelled_entry": [0, 1]})
    noncommuting = [["add", 0, 1, 1, 1, []], ["add", 1, 2, 1, 1, []]]
    forward, inverse = columns(noncommuting, 3), columns(noncommuting, 3, True)
    frow = [k for k, (col, _) in enumerate(forward) if 0 in col]
    irow = [k for k, (col, _) in enumerate(inverse) if 0 in col]
    need(frow == [0, 1] and irow == [0, 1, 2], "inverse-row orientation positive control")
    need(frow != irow, "forward-row substitution escaped")
    out.append({"name": "inverse_not_forward_row", "positive": True, "negative_rejected": True,
                "forward_support": frow, "inverse_support": irow})
    f = [space((1,)), space((2,))]
    shear = columns([["add", 1, 0, 1, 1, []]], 2)
    dirty = sorted(k for k in shear[0][0] if k != 0)
    row_only = f[0]
    joined = join([row_only] + [f[k] for k in dirty])
    need(dirty == [1] and dimension(row_only) == 1 and dimension(joined) == 2,
         "dirty-column positive control")
    need(row_only != joined, "omitted dirty-column mutant escaped")
    out.append({"name": "dirty_column_not_optional_in_contract", "positive": True,
                "negative_rejected": True, "row_only_dimension": 1, "joined_dimension": 2})
    correct = join([space((1,)), space((2,)), space((3,))])
    need(correct == frozenset({0, 1, 2, 3}) and basis(correct) == (2, 1), "GF2 join positive control")
    wrong = (3, 2, 1)
    need(wrong != basis(correct), "deduplicated-generator-rank mutant escaped")
    out.append({"name": "GF2_join_is_span_not_generator_count", "positive": True,
                "negative_rejected": True, "rank": 2, "dependent_generator_count": 3})
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), "refusing overwrite of a receipt")
    started = time.monotonic()
    compressed = args.word.read_bytes()
    raw = gzip.decompress(compressed)
    need(hashlib.sha256(raw).hexdigest() == WORD_SHA, "raw word content pin mismatch")
    result = reconstruct(json.loads(raw))
    primary_raw = args.primary.read_bytes()
    primary = json.loads(primary_raw)
    fields = ["helper_count", "arbitrary_input_columns", "compensation_gates", "prefix_gates",
              "local_profile", "current_width_inventory", "necessary_width_inventory",
              "dimension_slack_histogram", "candidates", "records"]
    # JSON roundtrip normalizes integer dictionary keys for the independent result.
    normalized = json.loads(json.dumps(result))
    # Primary adds explanatory fields; compare every independently derived field.
    primary_common = dict(primary)
    primary_common["records"] = [{k: row[k] for k in expected}
                                 for row, expected in zip(primary["records"], normalized["records"])]
    need(len(primary["records"]) == len(normalized["records"]), "record count mismatch")
    mismatches = [k for k in fields if normalized[k] != primary_common[k]]
    need(not mismatches, "primary comparison mismatch: " + repr(mismatches))
    result["compared_primary_fields"] = fields
    result["all_504_records_match_primary"] = True
    result["semantic_controls"] = controls()
    changed = bytearray(raw)
    changed[-2] ^= 1
    need(hashlib.sha256(changed).hexdigest() != WORD_SHA, "source corruption control escaped")
    result["source_pin_control"] = {"one_byte_content_change_rejected_before_parse": True}
    result["pins"] = {"word_path": str(args.word.resolve()), "word_content_sha256": WORD_SHA,
                      "word_gzip_sha256": hashlib.sha256(compressed).hexdigest(),
                      "primary_path": str(args.primary.resolve()),
                      "primary_result_sha256": hashlib.sha256(primary_raw).hexdigest(),
                      "independent_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    result["recorded_utc"] = datetime.now(timezone.utc).isoformat()
    result["seconds"] = time.monotonic() - started
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("records", "row_only_records")}, indent=2))


if __name__ == "__main__":
    main()
