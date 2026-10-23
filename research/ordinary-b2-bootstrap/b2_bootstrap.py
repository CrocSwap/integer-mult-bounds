#!/usr/bin/env python3
"""Exact B2 pricing and source compatibility; no production machine replay.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0. Mathematical dependencies retain their authors and source scope.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
import types

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
H = {1: 381024, 2: 400416, 3: 22752, 4: 26880,
     5: 29376, 6: 17376, 7: 26784, 42: 288}
W = 28416
C = Q("0.001730980255989036959962")
A1 = Q(169711, 10**8)
COUPLING = Q(1, 577)
TARGET = Q("0.001727989140903569")
BIT_LOWER = Q("0.001733427039589844234749")
FALLBACK = Q(32 * 64**2 * sum(H.values()), 10**16)
FAST_ARCHIVE = "research/selected-bit-fast-primitives/inputs/pr2899.tar"
RETUNED_ARCHIVE = "research/retuned-ordinary-coupling/inputs/pr2899-export.tar.gz"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def checked_body(path, expected):
    need(path.is_file() and not path.is_symlink(), "regular pinned input: " + str(path))
    body = path.read_bytes()
    need(digest(body) == expected, "source SHA256: " + str(path))
    return body


def complete_members(members, manifest):
    expected = {row["path"]: row["sha256"] for row in manifest["files"]}
    need(len(expected) == len(manifest["files"]), "unique source-manifest paths")
    need(set(members) == set(expected), "complete vendored B2 source inventory")
    need(all(digest(members[name]) == sha for name, sha in expected.items()),
         "vendored B2 member SHA256")


def sources(source_root=None):
    pins = json.loads((HERE / "B2-PINS.json").read_bytes())
    need(pins["schema_version"] == 3, "B2 pin schema")
    local = {name: checked_body(HERE / name, sha)
             for name, sha in pins["local_inputs"].items()}
    bundle = pins["source_bundle"]
    manifest = json.loads(checked_body(HERE / bundle["manifest"], bundle["manifest_sha256"]))
    need(manifest["scientific_base"] == pins["scientific_base"], "B2 source base")
    need(bundle["kind"] == "declared-pinned-repository-inputs", "pinned repository transport")
    root = REPO if source_root is None else source_root
    external = {row["path"]: checked_body(root / row["path"], row["sha256"])
                for row in manifest["files"]}
    complete_members(external, manifest)
    need(all(digest(external[name]) == sha for name, sha in pins["source_inputs"].items()),
         "theorem and backend input SHA256")
    # Compile exactly the authenticated bytes, without a bytecode-cache loader.
    engine = types.ModuleType("b2_authenticated_joint_engine")
    engine.__file__ = str(HERE / "frozen/interval_engine.py")
    exec(compile(local["frozen/interval_engine.py"], engine.__file__, "exec"), engine.__dict__)
    bit = json.loads(external["research/e8-bit-p111-tuned/tune/EXPECTED.json"])["nine"]
    need({int(k): int(v) for k, v in bit["profile"].items()} == H,
         "complete selected BIT profile")
    need(bit["bit"]["live"] == W and sum(H.values()) == 904896,
         "complete selected BIT stock and child count")
    need(Q(bit["bit_lower"]) == BIT_LOWER > COUPLING, "coarse BIT headroom")
    return pins, external, engine, manifest


@lru_cache(maxsize=None)
def root_power(rank, saving=COUPLING):
    """Independent integer-only enclosure of (rank/64)^(1-saving)."""
    need(0 < rank < 64 and 0 < saving < 1, "power domain")
    numerator, denominator = (1-saving).as_integer_ratio()
    scale = 1 << 160
    target = rank**numerator * scale**denominator
    divisor = 64**numerator
    lo, hi = 0, scale
    while hi-lo > 1:
        middle = (lo+hi)//2
        if middle**denominator * divisor <= target:
            lo = middle
        else:
            hi = middle
    need(lo**denominator * divisor <= target < hi**denominator * divisor,
         "outward integer-power enclosure")
    return Q(lo, scale), Q(hi, scale)


def integer_moment(saving=COUPLING, fallback=FALLBACK):
    low = high = Q(0)
    for rank, count in H.items():
        weight = (Q(count) + (fallback if rank == 1 else 0))/W
        lo, hi = root_power(rank, saving)
        low += weight*lo
        high += weight*hi
    return low, high


def decimal_enclosure(bounds, digits=30):
    low, high = bounds
    scale = 10**digits
    return [low.numerator*scale//low.denominator,
            -(-high.numerator*scale//high.denominator), scale]


def archive_members(body):
    # No extraction or execution. The entire archive has already been pinned.
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:*") as archive:
        all_items = archive.getmembers()
        need(all((member.isfile() or member.isdir())
                 and not PurePosixPath(member.name).is_absolute()
                 and ".." not in PurePosixPath(member.name).parts
                 for member in all_items), "safe relative regular archive members")
        items = [member for member in all_items if member.isfile()]
        need(len({member.name for member in items}) == len(items),
             "unique archived regular-file names")
        return {member.name: archive.extractfile(member).read() for member in items}


def same_backend(fast, retuned):
    need(len(fast) == 23 and len(retuned) == 35 and set(fast) <= set(retuned),
         "complete ordinary backend inventories")
    need(all(fast[name] == retuned[name] for name in fast),
         "byte-identical common ordinary backend")


def legacy_ceiling(rate):
    eta = Q(1, 10**24)
    q = (1-2*eta)*rate
    return (1-eta)*q/(1+q)


def check_power_coefficient(coefficient, moment_upper):
    need(coefficient*(1-moment_upper) > 1, "complete power-moment tariff")


def check_fit(bits):
    need(bits in (19, 20), "fixed sufficient-fit comparison domain")
    need(32780*Q(17, 16)*bits < 2**bits, "whole original-width stock fits")


def wrapper_coefficient(padded_root_factor=4):
    need(padded_root_factor == 4, "two ROOT calls each require below-two volume padding")
    return (padded_root_factor*200+1
            + padded_root_factor*10**6*Q(17, 16)+32780+2+1)


def reject(name, operation):
    try:
        operation()
    except (ValueError, KeyError):
        return name
    raise ValueError("control accepted: " + name)


def certificate(source_root=None):
    pins, external, engine, manifest = sources(source_root)
    series = tuple(x+1 for x in engine.moment(H, 64, W, COUPLING, FALLBACK))
    integer = integer_moment()
    need(max(integer[0], series[0]) <= min(integer[1], series[1]),
         "independent rational moment overlap")
    expected = [999998938581682162866772413602,
                999998938581682162866772413603, 10**30]
    need(decimal_enclosure(integer) == decimal_enclosure(series) == expected,
         "matching independent outward decimal enclosures")
    upper = max(integer[1], series[1])
    lower = min(integer[0], series[0])
    check_power_coefficient(10**6, upper)
    need(lower > Q(9999, 10000), "old power tariff is unavailable")
    mu1 = (sum(Q(r*n, 64) for r, n in H.items())+FALLBACK/64)/W
    need(mu1 == Q(2874298095721977, 2890625000000000) < Q(199, 200),
         "exact complete linear moment")
    a2 = COUPLING*(1-COUPLING)+COUPLING*A1
    need(a2 == Q(57697923247, 33292900000000) > C, "B2 clears complex rate")
    gaps = {"atom": COUPLING-a2, "borrowing": 1-a2-COUPLING,
            "remainder": 1-a2-COUPLING*(1-A1), "stock": 1-COUPLING}
    need(all(x > 0 for x in gaps.values()) and min(gaps.values()) == COUPLING-a2,
         "four strict completed-bootstrap gaps")
    need(A1 < COUPLING < Q(1, 512) and 1-a2-COUPLING > Q(1, 2),
         "full wrapper power absorption")
    need(17**128 > 32*16**128, "fixed power-factor bound")
    check_fit(20)
    coefficient = wrapper_coefficient()
    need(coefficient == 4283584 < 4300000, "complete two-root and wrapper coefficient")
    eta = Q(1, 10**24)
    s = (1-eta)*C-Q(1, 10**27)
    inadequate = s*(1-s)+s*A1
    need(inadequate > TARGET > legacy_ceiling(inadequate),
         "ordinary rate alone does not pay the legacy outer loss")
    baseline = COUPLING*(1-COUPLING)
    need(baseline < C, "unpromoted retuned C0 is insufficient")
    fast = archive_members(external[FAST_ARCHIVE])
    retuned = archive_members(external[RETUNED_ARCHIVE])
    retuned = {name.removeprefix("research/physical-ordinary-interchange/"): body
               for name, body in retuned.items() if not name.startswith(".")}
    same_backend(fast, retuned)
    changed = dict(fast)
    changed["ordinary.py"] += b"\n# changed source\n"
    bad_moment = integer_moment(Q(1, 576))
    full_next = engine.moment(H, 64, W, BIT_LOWER+Q(1, 10**24), FALLBACK)
    omitted_next = engine.moment(H, 64, W, BIT_LOWER+Q(1, 10**24), Q(0))
    need(full_next[0] > 0 > omitted_next[1], "fallback changes the endpoint decision")
    controls = [
        reject("omitted_bit_fallback", lambda: need(omitted_next[0] > 0, "paid endpoint reject sign")),
        reject("old_10000_power_coefficient", lambda: check_power_coefficient(10000, upper)),
        reject("profile_only_without_C1", lambda: need(baseline > C, "completed C1 required")),
        reject("ordinary_rate_substituted_for_kappa",
               lambda: need(legacy_ceiling(inadequate) > TARGET, "legacy outer margin")),
        reject("coupling_1_over_576", lambda: need(bad_moment[0] < 1, "complete BIT moment")),
        reject("stock_cutoff_2_power_19", lambda: check_fit(19)),
        reject("missing_two_call_padding", lambda: wrapper_coefficient(2)),
        reject("changed_backend_member", lambda: same_backend(changed, retuned)),
        reject("changed_stage_source", lambda: need(
            digest(external["research/selected-bit-fast-primitives/stage.py"]+b"\n")
            == pins["source_inputs"]["research/selected-bit-fast-primitives/stage.py"],
            "stage source hash")),
        reject("missing_vendored_source", lambda: complete_members(
            {name: body for name, body in external.items() if name != FAST_ARCHIVE}, manifest)),
        reject("changed_vendored_source", lambda: complete_members(
            {**external, FAST_ARCHIVE: external[FAST_ARCHIVE]+b"\n"}, manifest)),
    ]
    return {
        "status": "PASS_B2_EXACT_ARITHMETIC_AND_BACKEND_SOURCE_COMPATIBILITY",
        "a1": str(A1), "coupling": str(COUPLING), "B2_saving": str(a2),
        "complex_lower": str(C), "B2_minus_complex": str(a2-C),
        "strict_gaps": {name: str(value) for name, value in gaps.items()},
        "full_bit_mu1": str(mu1), "full_bit_mu_decimal": expected,
        "full_bit_mu_series": list(map(str, series)),
        "full_bit_mu_integer_power": list(map(str, integer)),
        "fallback_rank_one_count": str(FALLBACK),
        "fallback_decisive_endpoint": str(BIT_LOWER+Q(1, 10**24)),
        "C1_linear_coefficient": 200, "C1_power_coefficient": 10**6,
        "B2_wrapper_coefficient": int(coefficient), "physical_fit_from": 2**20,
        "source_backend_equal_files": len(fast),
        "backend_common_member_sha256": {name: digest(body) for name, body in sorted(fast.items())},
        "source_pins_sha256": digest((HERE / "B2-PINS.json").read_bytes()),
        "source_inputs": pins["source_inputs"], "local_inputs": pins["local_inputs"],
        "source_bundle": pins["source_bundle"], "source_bundle_files": len(external),
        "complex_coupling_counterexample": {
            "a_next": str(inadequate), "legacy_outer_ceiling": str(legacy_ceiling(inadequate)),
            "target": str(TARGET), "ceiling_minus_target": str(legacy_ceiling(inadequate)-TARGET)},
        "controls_rejected": controls,
        "production_factory_executed": False, "all_size_complex_admission": False,
        "scope": "Exact B2 rates, complete tariffs and source compatibility under retained physical/source arguments; no production retuned-C1 execution or new complex/outer admission.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path,
                        help="read the same complete pinned inputs from another source root")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path, help="compare the complete deterministic receipt")
    args = parser.parse_args()
    result = certificate(args.source_root.resolve() if args.source_root else None)
    historical = json.loads((HERE / "B2-PINS.json").read_bytes())["historical_result"]
    need(set(historical["projection_omits"])
         == {"source_pins_sha256", "local_inputs", "source_bundle"},
         "only transport metadata may differ from the historical receipt")
    projection = {key: value for key, value in result.items()
                  if key not in historical["projection_omits"]}
    need(digest(json.dumps(projection, sort_keys=True, separators=(",", ":")).encode())
         == historical["mathematical_projection_sha256"],
         "complete historical mathematical receipt equality")
    if args.check:
        need(result == json.loads(args.check.read_bytes()), "complete deterministic B2 receipt")
    encoded = json.dumps(result, sort_keys=True, indent=2)+"\n"
    if args.output:
        args.output.write_text(encoded)
    elif not args.check:
        print(encoded, end="")
    print(result["status"]+" controls="+str(len(result["controls_rejected"]))+
          " production_factory_executed=false all_size_complex_admission=false")


if __name__ == "__main__":
    main()
