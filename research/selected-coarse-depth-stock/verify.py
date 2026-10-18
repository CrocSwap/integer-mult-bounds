#!/usr/bin/env python3
"""Exact selected coarse-depth audit, Sricharan Vagvala / OpenAI Codex, Apache-2.0."""
import argparse
import ast
import bisect
import copy
from fractions import Fraction as Q
import hashlib
import io
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SEED, LIMIT = 64, 100_000
INVOICE = "candidate/strict/global/audit/PREFIX-AND-INVOICE.json"
OWNERS = "candidate/strict/global/audit/OWNERS-AND-PROFILE.json"
ASSEMBLY = "candidate/strict/ASSEMBLY.json"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pairs(items):
    result = {}
    for k, v in items:
        require(k not in result, "duplicate JSON key")
        result[k] = v
    return result


def parse(data):
    return json.loads(data, object_pairs_hook=pairs)


def same_receipt(left, right):
    # Preserve JSON types: Python considers True==1 and False==0.
    canonical = lambda x: json.dumps(x, sort_keys=True, separators=(",", ":"))
    return canonical(left) == canonical(right)


def sources():
    manifest = parse((PACKAGE / "SOURCES.json").read_bytes())
    inputs, members = {}, {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            require(sha(data) == row["sha256"], "source pin: " + row["path"])
            inputs[row["path"]] = data
    for archive in sorted({r["path"] for r in manifest["archive_members"]}):
        with tarfile.open(fileobj=io.BytesIO(inputs[archive])) as stream:
            for row in manifest["archive_members"]:
                if row["path"] == archive:
                    entry = stream.getmember(row["member"])
                    require(entry.isfile(), "regular archive member")
                    data = stream.extractfile(entry).read()
                    require(sha(data) == row["sha256"], "archive member pin")
                    members[row["member"]] = data
    return inputs, members


def inspect_code(code):
    tree = ast.parse(code)
    for expression in ("m*m>2*max(h)**2", "73*73>2*48*48",
                       "2*stock.bit_length()+9909+252+1024"):
        wanted = ast.dump(ast.parse(expression, mode="eval").body)
        require(any(ast.dump(n) == wanted for n in ast.walk(tree)), "source guard/formula")
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Name) and n.func.id == "check_moment"
             and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value == "complex"]
    require(len(calls) == 1 and isinstance(calls[0].args[2], ast.Constant), "complex call")
    return calls[0].args[2].value


def validate(selected, assembly, invoice, owner, owner_bytes, archived, code):
    require(selected["certificate"] == "research/community-frontier1094-audit/ASSEMBLY.json",
            "selected certificate")
    require(selected["kappa"] == assembly["kappa"], "selected saving")
    require(sha(archived) == selected["certificate_sha256"] and parse(archived) == assembly,
            "archive/committed assembly")
    require(invoice["owner_audit_sha256"] == sha(owner_bytes) and owner == parse(owner_bytes),
            "invoice owner reference")
    require(owner["status"] == "PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE", "owner status")
    require(invoice["status"] == "PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE",
            "invoice status")
    require(owner["paid_profile"] == assembly["complex_profile"], "complete paid profile")
    m = inspect_code(code)
    profile = {int(r): count for r, count in assembly["complex_profile"].items()}
    require(all(type(c) is int and c > 0 and 0 < r < m for r, c in profile.items()), "profile domain")
    require(m == 73 and max(profile) == 48, "selected depth parameters")
    require(sum(r*c for r, c in profile.items()) == owner["rank_mass"], "rank mass")
    require(m*owner["live"] - owner["rank_mass"] == owner["deficit"] == 5120, "deficit")
    require(owner["live"] == invoice["live"] and owner["physical"] == invoice["physical"], "stock link")
    require(invoice["finite"]["halving_integer_inequality"] == [m*m, 2*48*48], "finite guard")
    group = 2**(36*36)
    for j in range(1, 37):
        group *= 2**(2*j) - 1
    require(sum(invoice["physical_stock_identity"].values()) == invoice["physical"], "all work families")
    bits = (group*invoice["physical"]).bit_length()
    require(bits == invoice["finite"]["physical_stock_bits"] == 2642, "finite stock bits")
    require(invoice["row_prefix_extra"] == 1024, "row precision charge")
    other = 9909 + 252 + 1024
    require(2*bits + other == invoice["finite"]["physical_row_coefficient"] == 16469, "row ledger")
    require(invoice["finite"]["retained_row_coefficient"] == 20161, "retained row cap")
    return m, profile, bits, other


def depth(n, m=73, rank=48):
    require(type(n) is int and n >= 0 and 0 < rank < m, "depth domain")
    d = 0
    while n >= m:
        n = rank*(n//m)
        d += 1
    return d


def thresholds(stop, m=73, rank=48):
    result = [m]
    while result[-1] <= stop:
        result.append(m*((result[-1] + rank - 1)//rank))
    return result


def blocks(m=73, rank=48, cap=64):
    tested = passing = 0
    candidates = []
    for p in range(1, cap + 1):
        for q in range(1, p + 1):
            tested += 1
            if m**p > 2**q*rank**p:
                passing += 1
                candidates.append((Q(p, q), p, q))
    return min(candidates)[1:], tested, passing


def independent_block(m=73, rank=48, cap=64):
    candidates = []
    for p in range(1, cap + 1):
        q = ((m**p - 1)//rank**p).bit_length() - 1
        if q >= 1:
            candidates.append((Q(p, q), p, q))
    return min(candidates)[1:]


def rejected(name, action):
    try:
        action()
    except ValueError:
        return name
    raise ValueError("negative control accepted: " + name)


def run():
    inputs, members = sources()
    selected = parse(inputs["certificates/selected-result.json"])
    assembly = parse(inputs["research/community-frontier1094-audit/ASSEMBLY.json"])
    invoice, owner = parse(members[INVOICE]), parse(members[OWNERS])
    args = (selected, assembly, invoice, owner, members[OWNERS], members[ASSEMBLY], members["code/assemble.py"])
    m, profile, bits, other = validate(*args)
    # Keep the two selected suppliers distinct. Concurrent PR2084 prompted
    # this source check; its code/proof is not an implementation dependency.
    bit_record = parse(members["inputs/PR589-EXPECTED.json"])["nine"]
    bit_m, bit_rank = 64, max(map(int, bit_record["profile"]))
    wanted = ast.dump(ast.parse("BIT_M==64", mode="eval").body)
    require(any(ast.dump(n) == wanted for n in ast.walk(ast.parse(members["code/assemble.py"]))),
            "distinct BIT width source")
    require(bit_rank == bit_record["bit"]["maxchild"] == 42, "BIT rank source")
    require(bit_record["bit_lower"] == assembly["bit_lower"], "selected BIT endpoint")
    (p, q), tested, passing = blocks(m, max(profile), SEED)
    require((p, q) == independent_block(m, max(profile), SEED) == (43, 26), "block agreement")
    # Independent DP maximizes over every paid rank, including rank-one fallback.
    dp = [0]*m
    for n in range(m, LIMIT + 1):
        dp.append(1 + max(dp[r*(n//m)] for r in sorted(set(profile) | {1})))
    first = thresholds(10**15)[:SEED]
    large = {v + offset for v in first for offset in (-1, 0, 1)}
    for exponent in range(513):
        for v in (2**exponent, m*2**exponent):
            large.update(max(0, v + offset) for offset in (-1, 0, 1))
    inverse = thresholds(max(large))
    all_n = list(range(LIMIT + 1)) + sorted(n for n in large if n > LIMIT)
    digest = hashlib.sha256()
    stock_charge = (p*bits + q - 1)//q
    for n in all_n:
        d = depth(n)
        require(d == bisect.bisect_right(inverse, n), "inverse threshold depth")
        if n <= LIMIT:
            require(d == dp[n], "all-child DP")
        require(max(2, n)**p > 2**(q*d), "integer logarithmic bound")
        require(d*bits <= stock_charge*(max(2, n) - 1).bit_length(), "depth stock bound")
        digest.update(f"{n}:{d}\n".encode("ascii"))
    controls = []
    changed = copy.deepcopy(assembly)
    changed["complex_profile"]["48"] -= 1
    controls.append(rejected("omit_rank48_child", lambda: validate(
        selected, changed, *args[2:])))
    changed = copy.deepcopy(invoice)
    changed["physical_stock_identity"].pop("private_centres")
    controls.append(rejected("omit_private_centre_stock", lambda: validate(
        selected, assembly, changed, *args[3:])))
    controls.append(rejected("detach_owner_reference", lambda: validate(
        selected, assembly, {**invoice, "owner_audit_sha256": "0"*64}, *args[3:])))
    controls.append(rejected("weaken_source_rank_guard", lambda: inspect_code(
        members["code/assemble.py"].replace(b"m*m>2*max(h)**2", b"m*m>max(h)**2"))))
    controls.append(rejected("one_level_halving", lambda: require(48*(219//73) <= 219//2, "n=219")))
    controls.append(rejected("ceil_child_rule", lambda: require(48*((74+72)//73) < 74, "n=74")))
    controls.append(rejected("terminal_width_is_free", lambda: require(depth(73) == 0, "n=73")))
    controls.append(rejected("threshold_off_by_one", lambda: require(depth(first[10]-1) == 11, "boundary")))
    controls.append(rejected("invalid_block_3_over_2", lambda: require(73**3 > 4*48**3, "bad block")))
    controls.append(rejected("floor_sufficient_charge", lambda: require((p*bits//q)*q >= p*bits, "ceiling")))
    controls.append(rejected("boolean_width", lambda: depth(True)))
    controls.append(rejected("identify_complex_as_bit_producer", lambda: require(
        (m,max(profile)) == (bit_m,bit_rank), "distinct producer identity")))
    s = min(Q(assembly["bit_lower"]), (1-Q(1,10**24))*Q(assembly["complex_lower"]))-Q(1,10**27)
    stage, a = 1 + SEED % 7, Q(384599,10**10)
    for _ in range(stage):
        a = (1-s)*s+s*a
    require(str(a) == assembly["bootstrap"][stage-1]["exponent"], "seed-selected stage")
    return dict(status="PASS_SELECTED_COARSE_DEPTH_STOCK", assignment_seed=SEED,
        selected_kappa=selected["kappa"], ambient_width=m, paid_profile=assembly["complex_profile"],
        maximum_rank=48, conservative_fallback_maximum_rank=1,
        depth_model="D(n)=0 for n<73; otherwise 1+D(48*floor(n/73))",
        first_64_depth_thresholds=first,
        block_search=dict(p_domain=[1,64], q_domain="1..p", tested=tested, passing=passing,
                          best_p=p, best_q=q, strict_integer_gap=str(73**p-2**q*48**p),
                          global_block_optimum_claimed=False),
        finite_coverage=dict(dense_widths=[0,LIMIT], dense_count=LIMIT+1,
                             power_exponents=[0,512], distinct_widths=len(all_n),
                             depth_pairs_sha256=digest.hexdigest()),
        finite_source_stock=dict(physical_families=invoice["physical"], bits=bits),
        conditional_depth_component=dict(old_coefficient=2*bits, certified_new_coefficient=stock_charge,
            other_ledger_terms=other, retained_row_ledger=2*bits+other,
            conditional_row_ledger=stock_charge+other, difference=2*bits-stock_charge,
            retained_row_cap=20161, adoption_claimed=False),
        stage_parameter_comparison=dict(index=stage, s=str(s), atom_width_law="w=ceil(e^s), n<=floor(e/w)",
                          log_width_coefficient=str(Q(p,q)*(1-s)), complete_stock_coefficient_known=False),
        producer_boundary=dict(complex_width=m, complex_maximum_rank=48,
            ordinary_bit_width=bit_m, ordinary_bit_maximum_rank=bit_rank,
            complex_depth_is_ordinary_bootstrap_depth=False),
        controls_rejected=controls,
        scope="All-integer depth proof under the inherited floor-child/terminal contract. Per-level divisor, leaf reserve, whole-producer admission and full multiplication theorem remain open.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="Create an external receipt; never overwrite")
    options = parser.parse_args()
    result = run()
    if options.write_result:
        with options.write_result.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    else:
        require(same_receipt(result, parse((PACKAGE/"RESULT.json").read_bytes())), "stored exact receipt")
    print("PASS_SELECTED_COARSE_DEPTH_STOCK block=43/26 widths="
          + str(result["finite_coverage"]["distinct_widths"])
          + " conditional_row=16469->15555 controls=" + str(len(result["controls_rejected"]))
          + " no_new_kappa")


if __name__ == "__main__":
    main()
