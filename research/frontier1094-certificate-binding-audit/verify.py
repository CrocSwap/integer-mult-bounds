#!/usr/bin/env python3
"""Selected #1094 certificate: invoice/outer recheck and certificate-to-replay binding audit.

Adversarial audit (supplier-boundary-audit). Standard library and git only.
Audited code is loaded as exact Git objects at BASE, so later repairs of the
audited scripts do not silently change what this package checked.

  1. Apply the unchanged frontier1042-invoice-audit-seed81 recheck (profile,
     per-vertex envelope, nine finite guards, 7+7 bootstrap levels, 47+47 outer
     slacks, 15 mutation controls) to the committed #1094 certificate and its
     pinned receipts, bound directly to the certificate bytes rather than the
     moving selected pointer. Reproduce seed81's own #1042 result as a control.
  2. Exact field-level delta of the #1094 receipts against #1042.
  3. Equality of the #1094 complex profile across five artifacts.
  4. A well-formed mutant certificate: complex endpoint + 1e-24 (the next grid
     point, rejected by the exact moment), with bootstrap, outer slacks and moment
     records recomputed so every arithmetic identity holds and kappa is unchanged.
     It is tested against each check on the reproduce path.
  5. The proposed one-line binding (replay ASSEMBLY sha == certificate_sha256),
     evaluated on the published replay output.

Prepared for rtyu193-rgb with Claude Code (Claude Opus 5.5). Apache-2.0.
"""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import types
from fractions import Fraction as Q

if not __debug__:
    raise SystemExit("checks use assert; run without -O")

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
BASE = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
CODE = {  # audited code as exact Git blobs at BASE
    "seed81": ("research/frontier1042-invoice-audit-seed81/verify.py", "8ee1d7a01473e1b5674710165566e4e9761f7c65"),
    "de": ("research/selected-suppliers-de-diagnostic/verify.py", "f9a9d5e5103b6ccbadb3f50fea34e25ccfce7ff1"),
    "selected": ("scripts/verify_selected_result.py", "c755b76e0d44ba4917aa94440ebe54daefce5b2a"),
    "replay": ("scripts/verify_frontier1094.py", "96e6c1386bd052b9bcaf136d934406f3f0c3f777"),
    "candidate": ("research/complex-t16-rare-pattern-exchanges/verify.py", "9d471cf90835bc91d32bb0216c2bb867011a7420"),
}
A1094, P1094 = "research/community-frontier1094-audit", "candidate/strict"
A1042, P1042 = "research/community-frontier1042-audit", "t16"
CERT1094_SHA = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"
GRID = Q(1, 10 ** 24)
ETA = BETA = Q(1, 10 ** 24)
EXPECTED_DELTA = {
    "invoice": ["/controller_audit_sha256", "/owner_audit_sha256", "/template_sha256"],
    "owners": ["/actual_73column_sigmas", "/controller_audit_sha256", "/cross_replica_helper_roles",
               "/explicit_idle_remainder_children", "/paid_profile/1", "/paid_profile/16", "/paid_profile/2",
               "/paid_profile/3", "/paid_profile/48", "/paid_profile/7", "/template_sha256"],
}


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def git_blob(b):
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def git_show(path):
    return subprocess.run(["git", "-C", str(ROOT), "show", BASE + ":" + path],
                          capture_output=True, check=True).stdout


def load_module(key):
    path, blob = CODE[key]
    src = git_show(path)
    assert git_blob(src) == blob, f"audited code blob differs: {path}"
    mod = types.ModuleType("audited_" + key)
    mod.__file__ = str(ROOT / path)
    exec(compile(src, str(ROOT / path), "exec"), mod.__dict__)
    return mod


def load_record(audit, prefix, cert_sha):
    """Certificate and receipts, each bound by hash; no moving pointer is read."""
    cert = (ROOT / audit / "ASSEMBLY.json").read_bytes()
    assert sha256(cert) == cert_sha, audit + " certificate bytes"
    asm = json.loads(cert)
    with tarfile.open(ROOT / audit / "selected-replay.tar.gz") as tar:
        get = lambda n: tar.extractfile(prefix + "/" + n).read()
        owner, invoice, archived = (get("global/audit/OWNERS-AND-PROFILE.json"),
                                    get("global/audit/PREFIX-AND-INVOICE.json"), get("ASSEMBLY.json"))
    assert archived == cert, audit + " archived replay assembly differs from committed certificate"
    assert sha256(owner) == asm["input_sha256"]["owner_audit"], audit + " owner receipt pin"
    assert sha256(invoice) == asm["input_sha256"]["fresh_invoice"], audit + " invoice receipt pin"
    bit = (ROOT / asm["bit_supplier"]["path"]).read_bytes()
    assert git_blob(bit) == asm["bit_supplier"]["git_blob_sha1"], "PR589 blob pin"
    return dict(asm=asm, owner=json.loads(owner), invoice=json.loads(invoice), bit=json.loads(bit)), cert


def delta(x, y, path=""):
    if isinstance(x, dict) and isinstance(y, dict):
        out = []
        for k in sorted(set(x) | set(y), key=str):
            out += [f"{path}/{k}"] if (k in x) != (k in y) else delta(x[k], y[k], f"{path}/{k}")
        return out
    if isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        return [p for i, (u, v) in enumerate(zip(x, y)) for p in delta(u, v, f"{path}[{i}]")]
    return [] if x == y else [path]


def profile(d):
    return {int(k): int(v) for k, v in d.items() if int(v)}


def exact_decimal(x, digits=24):
    n = x * 10 ** digits
    assert n.denominator == 1
    s = str(n.numerator).rjust(digits + 1, "0")
    return s[:-digits] + "." + s[-digits:]


def make_mutant(asm, s81, shift=GRID):
    """Arithmetic-consistent certificate claiming acceptance at complex endpoint + shift."""
    b, c = Q(asm["complex_lower"]) + shift, Q(asm["bit_lower"])
    a, cuts = s81.bootstrap(b, c, ETA, BETA)
    k = s81.kappa_from(a, ETA)
    slacks, _ = s81.assembly_slacks(a, b, k, ETA, BETA)
    m = copy.deepcopy(asm)
    m["complex_lower"], m["complex_decimal"] = str(b), exact_decimal(b)
    m["bootstrap"] = [dict(exponent=str(x["exponent"]), gap=str(x["gap"]), cutoff_log2=str(x["cutoff_log2"]))
                      for x in cuts]
    m["outer"] = {n: str(slacks[n]) for n in asm["outer"]}
    for e in m["moments"]:
        if e["side"] == "complex":
            e["endpoint"] = str(Q(e["endpoint"]) + shift)
    return m, k


def strings_in(src):
    return [n.value for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def rejects(fn):
    try:
        fn()
    except Exception as exc:          # the audited checkers raise ValueError / Fail / AssertionError
        return type(exc).__name__ + ": " + str(exc)[:120]
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="regenerate RESULT.json")
    args = ap.parse_args()
    s81, de, sel = load_module("seed81"), load_module("de"), load_module("selected")
    out = {}

    # 1. Invoice/outer recheck of the committed #1094 certificate; #1042 reproduction as control.
    record_base = json.loads(git_show("certificates/selected-result.json"))
    assert record_base["certificate"] == A1094 + "/ASSEMBLY.json"
    assert record_base["certificate_sha256"] == CERT1094_SHA
    d1094, cert1094 = load_record(A1094, P1094, CERT1094_SHA)
    chk1042 = json.loads((ROOT / "certificates/checkpoints/frontier1042.json").read_bytes())
    assert chk1042["certificate"] == A1042 + "/ASSEMBLY.json"
    d1042, _ = load_record(A1042, P1042, chk1042["certificate_sha256"])
    r1042 = s81.run_all(d1042)
    published = json.loads(git_show("research/frontier1042-invoice-audit-seed81/RESULT.json"))
    for key in ("profile", "envelope", "guards", "native", "conservative"):
        assert json.loads(json.dumps(r1042[key], sort_keys=True)) == published[key],             "seed81 #1042 result not reproduced: " + key
    r1094 = s81.run_all(d1094)
    ctl = s81.controls(d1094)
    assert len(ctl) == 15
    out["recheck_1094"] = dict(status="PASS", controls_rejected=sorted(ctl), **{
        k: r1094[k] for k in ("profile", "envelope", "guards")},
        native=dict(kappa=r1094["native"]["kappa"], min_slack_names=r1094["native"]["min_slack_names"]),
        conservative=dict(kappa=r1094["conservative"]["kappa"]))
    out["recheck_1094"]["same_as_1042"] = {k: r1094[k] == r1042[k] for k in ("envelope", "guards")}
    # seed81's own entry point binds the moving pointer; at BASE it targets a non-selected record.
    out["seed81_binding"] = dict(audit_constant=s81.AUDIT, selected_at_base=record_base["certificate"],
                                 stale=s81.AUDIT + "/ASSEMBLY.json" != record_base["certificate"])

    # 2. Exact receipt delta against #1042.
    got = dict(invoice=delta(d1042["invoice"], d1094["invoice"]), owners=delta(d1042["owner"], d1094["owner"]))
    assert got == EXPECTED_DELTA, got
    out["receipt_delta_vs_1042"] = got

    # 3. Profile binding across five artifacts.
    P = "research/complex-t16-rare-pattern-exchanges/"
    ind = json.loads((ROOT / A1094 / "INDEPENDENT1094.json").read_bytes())
    copies = {
        "certificate complex_profile": profile(d1094["asm"]["complex_profile"]),
        "archived OWNERS-AND-PROFILE paid_profile": profile(d1094["owner"]["paid_profile"]),
        "package PROFILE.json": profile(json.loads((ROOT / P / "PROFILE.json").read_bytes())),
        "package data/PLAN.json profile": profile(json.loads((ROOT / P / "data/PLAN.json").read_bytes())["profile"]),
        "INDEPENDENT1094 owner-audited profile": profile(ind["owner"]["profile"]),
    }
    ref = copies["certificate complex_profile"]
    assert all(v == ref for v in copies.values()), "profile copies disagree"
    out["profile_binding"] = dict(artifacts=sorted(copies), equal=True, profile=dict(sorted(ref.items())))

    # 4. The mutant certificate against each layer of the reproduce path.
    asm = d1094["asm"]
    mutant, k_mut = make_mutant(asm, s81)
    assert k_mut == Q(asm["kappa"]) and mutant["kappa"] == asm["kappa"], "mutant must keep kappa"
    layers = {}
    layers["seed81_invoice_outer_arithmetic"] = rejects(lambda: s81.run_all(dict(d1094, asm=mutant)))
    mbytes = (json.dumps(mutant, indent=2) + "\n").encode()
    with tempfile.TemporaryDirectory(dir=PKG) as tmp:
        rel = Path(tmp).relative_to(ROOT).as_posix() + "/ASSEMBLY.json"
        (ROOT / rel).write_bytes(mbytes)
        rec = dict(record_base, certificate=rel, certificate_sha256=sha256(mbytes))
        layers["verify_selected_result_check"] = rejects(lambda: sel.check(rec, ROOT))
        assert sel.check(record_base, ROOT) == Q(asm["kappa"])
        # Control: the same layer does bind kappa itself.
        bad = dict(mutant, kappa=str(Q(asm["kappa"]) + Q(1, 10 ** 18)))
        bbytes = json.dumps(bad).encode()
        (ROOT / rel).write_bytes(bbytes)
        kappa_control = rejects(lambda: sel.check(dict(rec, certificate_sha256=sha256(bbytes)), ROOT))
    assert kappa_control is not None, "kappa edit must be rejected"
    replay_src = git_show(CODE["replay"][0]).decode()
    cert_strings = sorted(s for s in strings_in(replay_src) if "certificate" in s or "selected" in s)
    refs = [s for s in cert_strings if any(t in s for t in ("frontier1094-audit", "selected-result",
                                                             "certificate_sha256"))]
    makefile = git_show("Makefile").decode().splitlines()
    i = makefile.index("frontier1094-verify: selected-record-check")
    recipe = [line.strip() for line in makefile[i + 1:i + 3]]
    assert recipe[-1] == 'python3 -B scripts/verify_frontier1094.py --work "$$work/replay"', recipe
    layers["verify_frontier1094_reads_committed_certificate"] = bool(refs)
    assert not refs, refs
    # The candidate stage it runs binds only status, kappa and the profile (to package PROFILE.json).
    cand_src = git_show(CODE["candidate"][0])
    assert git_blob(cand_src) == CODE["candidate"][1]
    cand_strings = set(strings_in(cand_src.decode()))
    assert {"kappa_decimal", "complex_profile", "PROFILE.json"} <= cand_strings
    cand_unbound = sorted(f for f in ("complex_lower", "bootstrap", "outer", "moments", "conservative_outer",
                                      "frontier1094-audit") if f not in cand_strings)
    assert len(cand_unbound) == 6, cand_unbound
    # Exact moment (code-disjoint enclosure of the endpoint package) at both endpoints.
    bill, _ = de.complex_ledger(asm, ind)
    lo, hi = bill.residual(Q(asm["complex_lower"]))
    mlo, mhi = bill.residual(Q(mutant["complex_lower"]))
    assert hi < 0 < mlo, "moment must accept the certified endpoint and reject the mutant"
    layers["exact_moment_at_mutant_endpoint"] = "rejects: residual lower bound > 0"
    assert layers["seed81_invoice_outer_arithmetic"] is None and layers["verify_selected_result_check"] is None
    out["mutant"] = dict(
        change="complex_lower + 1e-24 with bootstrap, 47 outer slacks, complex moment endpoints recomputed",
        complex_lower=mutant["complex_lower"], kappa_unchanged=mutant["kappa"],
        layers=dict(seed81_invoice_outer_arithmetic="accepts",
                    verify_selected_result_check="accepts after repinning certificate_sha256",
                    verify_frontier1094="never reads the committed certificate; replay binds only kappa and profile",
                    exact_moment="rejects"),
        moment_residual_upper_at_certified=f"{float(hi):.6e}", moment_residual_lower_at_mutant=f"{float(mlo):.6e}",
        kappa_edit_control=kappa_control, frontier1094_verify_recipe=recipe,
        verify_frontier1094_certificate_strings=cert_strings,
        candidate_stage_binds=["status", "kappa_decimal", "complex_profile == package PROFILE.json"],
        candidate_stage_never_names=cand_unbound)

    # 5. Proposed binding: replay output bytes must equal the selected certificate.
    with tarfile.open(ROOT / A1094 / "selected-replay.tar.gz") as tar:
        replay_out = tar.extractfile(P1094 + "/ASSEMBLY.json").read()
    published_result = json.loads((ROOT / A1094 / "RESULT.json").read_bytes())
    proposed = lambda replay_bytes, record: sha256(replay_bytes) == record["certificate_sha256"]
    assert proposed(replay_out, record_base) and published_result["assembly_sha256"] == CERT1094_SHA
    assert not proposed(replay_out, dict(record_base, certificate_sha256=sha256(mbytes)))
    out["proposed_binding"] = dict(
        check="require(sha(work/'candidate/strict/ASSEMBLY.json') == selected['certificate_sha256'])",
        published_replay_output_matches=True, published_result_assembly_sha256_matches=True,
        rejects_mutant=True)

    out["status"] = "PASS_FRONTIER1094_CERTIFICATE_BINDING_AUDIT"
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    target = PKG / "RESULT.json"
    if args.write:
        target.write_text(text, encoding="utf-8", newline="\n")
        print("WROTE", target.relative_to(ROOT).as_posix())
    else:
        assert target.read_text(encoding="utf-8") == text, "RESULT.json differs from regenerated result"
    print(f"{out['status']} invoice_outer=PASS controls=15 receipt_delta=14 profile_copies=5 "
          f"mutant_accepted_by=arithmetic,selected_check mutant_rejected_by=exact_moment no_new_kappa")


if __name__ == "__main__":
    main()
