#!/usr/bin/env python3
"""Static checks of the p104-banked-unified-banner Lean package (standard library only; Lean is NOT run here).

Checks: file pins (MANIFEST.sha256, both directions); no sorry/admit/native_decide/axiom/opaque/unsafe/
implemented_by/extern/ofReduceBool outside comments and strings; Nov15/ equals build-order.txt, which is a
topological order of the Nov15 import graph and equals the import closure of All.lean; the excluded module
is absent; every `#print axioms` name in Check.lean is declared in the sources; the unified headline signatures
(conclusion, hypothesis-free `_disjoint`), the #7761 witness signatures and the banner constants; the #7786 caller
data (tools/callergen/app7786-caller.json) equals the lists of `consts7786`, and the generator regenerates
Nov15/BankCallerGenCert.lean byte-identical; toolchain and Mathlib pins; CHECK-axioms.txt lists exactly the
Check.lean names, each within {propext, Classical.choice, Quot.sound}; no local paths in the package.
The kernel check itself is `lean/check.sh` (needs Lean and the pinned Mathlib; see README.md).

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
"""
from fractions import Fraction
import hashlib
from pathlib import Path
import json
import re
import subprocess
import sys

PKG = Path(__file__).resolve().parent
LEAN = PKG / "lean"
STD = {"propext", "Classical.choice", "Quot.sound"}
MATHLIB_REV = "55b7917b472489c7c56a0fa6393af05cfd536599"
TOOLCHAIN = "leanprover/lean4:v4.33.0-rc1"
EXCLUDED = ["BankBannerChain"]
FORBIDDEN = ["sorry", "admit", "native_decide", "axiom", "opaque", "unsafe", "implemented_by", "extern",
             "ofReduceBool"]


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def strip_lean(src):
    """Remove (nested) block comments, line comments and string literals."""
    out, i, n, depth = [], 0, len(src), 0
    while i < n:
        if src.startswith("/-", i):
            depth += 1; i += 2; continue
        if depth:
            if src.startswith("-/", i):
                depth -= 1; i += 2
            else:
                i += 1
            continue
        if src.startswith("--", i):
            j = src.find("\n", i); i = n if j < 0 else j; continue
        if src[i] == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            out.append('""'); i = j + 1; continue
        out.append(src[i]); i += 1
    if depth:
        fail("unterminated block comment")
    return "".join(out)


def check_manifest():
    rows = {}
    for line in (PKG / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        rows[name] = digest
    present = {p.relative_to(PKG).as_posix() for p in LEAN.rglob("*")
               if p.is_file() and ".lake" not in p.parts and "logs" not in p.parts
               and p.name != "logs-Check.txt" and "__pycache__" not in p.parts}
    present.add("CHECK-axioms.txt")
    if set(rows) != present:
        fail("MANIFEST.sha256 file set differs: missing %s, extra %s"
             % (sorted(present - set(rows))[:5], sorted(set(rows) - present)[:5]))
    for name, digest in rows.items():
        if hashlib.sha256((PKG / name).read_bytes()).hexdigest() != digest:
            fail("sha256 mismatch: " + name)
    return len(rows)


def main():
    nfiles = check_manifest()
    mods = sorted(p.stem for p in (LEAN / "Nov15").glob("*.lean"))
    order = (LEAN / "build-order.txt").read_text(encoding="utf-8").split()
    if sorted(order) != mods or len(set(order)) != len(order):
        fail("Nov15/ differs from build-order.txt")
    for x in EXCLUDED:
        if x in mods:
            fail("excluded module present: " + x)
    imp = re.compile(r"^\s*import\s+Nov15\.(\S+)", re.M)
    stripped, seen, decls = {}, set(), set()
    for m in order:
        src = (LEAN / "Nov15" / (m + ".lean")).read_text(encoding="utf-8")
        code = strip_lean(src)
        stripped[m] = code
        for d in imp.findall(code):
            if d not in seen:
                fail("build-order.txt is not topological: %s imports %s" % (m, d))
        seen.add(m)
        for tok in FORBIDDEN:
            if re.search(r"(?<![\w.'])" + re.escape(tok) + r"(?![\w'])", code):
                fail("forbidden token %r outside comments in %s" % (tok, m))
        for name in re.findall(r"(?:theorem|lemma|def|abbrev|structure|inductive|instance|noncomputable def)"
                               r"\s+([^\s(:{\[]+)", code):
            decls.add(name)
    for f in ("All.lean", "Check.lean"):
        code = strip_lean((LEAN / f).read_text(encoding="utf-8"))
        for tok in FORBIDDEN:
            if re.search(r"(?<![\w.'])" + re.escape(tok) + r"(?![\w'])", code):
                fail("forbidden token %r in %s" % (tok, f))
    roots = imp.findall((LEAN / "All.lean").read_text(encoding="utf-8"))
    closure, stack = set(), list(roots)
    while stack:
        m = stack.pop()
        if m in closure:
            continue
        if m not in stripped:
            fail("All.lean closure needs missing module " + m)
        closure.add(m); stack.extend(imp.findall(stripped[m]))
    if closure != set(order):
        fail("import closure of All.lean (%d) differs from build-order.txt (%d)" % (len(closure), len(order)))
    names = re.findall(r"^#print axioms (\S+)", (LEAN / "Check.lean").read_text(encoding="utf-8"), re.M)
    for full in names:
        parts = full.split(".")
        if not any(".".join(parts[k:]) in decls for k in range(len(parts))):
            fail("Check.lean name not declared in sources: " + full)
    head = stripped["BankBannerHead"]
    m = re.search(r"theorem bank_kappa_lt_banner_head(.*?):=", head, re.S)
    if not m or not m.group(1).rstrip().endswith("κ < 2381707 / 250000000"):
        fail("headline BankBannerHead.bank_kappa_lt_banner_head statement changed")
    w = re.search(r"theorem kappa7761_lt_banner_head(.*?):=", stripped["Bridge7761T4"], re.S)
    binders = re.findall(r"\((\w+)\s*:", w.group(1)) if w else []
    if not w or binders != ["κ", "hκ0", "hκ1", "hV"] or not w.group(1).rstrip().endswith("κ < 2381707 / 250000000"):
        fail("#7761 witness signature changed (expected binders κ, hκ0, hκ1, hV only)")
    if Fraction(2381707, 250000000) != Fraction("0.009526828"):
        fail("banner constant")
    lakefile = (LEAN / "lakefile.toml").read_text(encoding="utf-8")
    manifest = (LEAN / "lake-manifest.json").read_text(encoding="utf-8")
    if ('rev = "%s"' % MATHLIB_REV) not in lakefile or ('"rev": "%s"' % MATHLIB_REV) not in manifest:
        fail("Mathlib pin")
    if (LEAN / "lean-toolchain").read_text(encoding="utf-8").strip() != TOOLCHAIN:
        fail("toolchain pin")
    printed = []
    for line in (PKG / "CHECK-axioms.txt").read_text(encoding="utf-8").splitlines():
        a = re.fullmatch(r"'(\S+)' depends on axioms: \[(.*)\]", line)
        b = re.fullmatch(r"'(\S+)' does not depend on any axioms", line)
        if a:
            axs = {x.strip() for x in a.group(2).split(",")}
            if not axs <= STD:
                fail("axioms outside the standard three: " + line)
            printed.append(a.group(1))
        elif b:
            printed.append(b.group(1))
    if printed != names:
        fail("CHECK-axioms.txt (%d) does not list exactly the %d Check.lean names" % (len(printed), len(names)))
    for p in PKG.rglob("*"):
        if p.is_file() and ".lake" not in p.parts and p.suffix in (".md", ".lean", ".py", ".sh", ".txt", ".json", ".toml"):
            t = p.read_text(encoding="utf-8", errors="replace")
            if ("/" + "Users/") in t or ("/" + "home/") in t:
                fail("local path in " + p.relative_to(PKG).as_posix())
    check_unified(stripped)
    check_caller7786(stripped)
    print("pins: %d files; modules: %d (topological, = All.lean closure); headlines in Check.lean: %d, all declared"
          % (nfiles, len(order), len(names)))
    print("unified headline + #7761 instances: signatures OK; #7786 caller data = consts7786; certificate regenerated")
    print("PASS p104-banked-unified-banner static checks (Lean not run; kernel check = lean/check.sh)")


def theorem_sig(code, name):
    m = re.search(r"theorem " + re.escape(name) + r"\b(.*?):=", code, re.S)
    if not m:
        fail("theorem %s not found" % name)
    return m.group(1)


def check_unified(stripped):
    if Fraction(952721, 100000000) != Fraction("0.00952721"):
        fail("unified banner constant")
    ub = stripped["BankUnifyB"]
    for name in ("bank_kappa_lt_unified", "bank_kappa_lt_unified_fam", "bank_kappa_lt_unified_disjoint"):
        sig = theorem_sig(ub, name)
        if not sig.rstrip().endswith("κ < 952721 / 100000000"):
            fail("%s conclusion changed" % name)
        for h in ("hc : ∀ i, HSContract", "hC : ∀ i, ComputesS", "hin : ∀ i p", "hout : ∀ i s", "hF : ∀ i",
                  "hW : ∀ i, 0 ≤", "hV : Valid c"):
            if h not in sig:
                fail("%s: premise %r missing" % (name, h))
    dis = theorem_sig(ub, "bank_kappa_lt_unified_disjoint")
    if "OTIComp" in dis or "Disch" in dis:
        fail("bank_kappa_lt_unified_disjoint must not take an OTI hypothesis")
    for name in ("kappa7761_lt_unified", "kappa7761_lt_unified_W1"):
        sig = theorem_sig(ub, name)
        binders = re.findall(r"\((\w+)\s*:", sig)
        if binders != ["κ", "hκ0", "hκ1", "hV"] or not sig.rstrip().endswith("κ < 952721 / 100000000"):
            fail("#7761 unified witness %s signature changed (expected binders κ, hκ0, hκ1, hV only)" % name)


def check_caller7786(stripped):
    gdir = LEAN / "tools" / "callergen"
    data = json.loads((gdir / "app7786-caller.json").read_text(encoding="utf-8"))
    if data.get("source_sha256") != "88486d49f2ba1fc0e6c9f4a7402c82e91c44026cf90cd1387d1e5c45cf5e88d3":
        fail("caller data source sha256")
    c = data["caller"]
    tb = [(int(r), int(v)) for r, v in c["fixed_root_targets"].items()]
    pb = [(int(r), int(v)) for r, v in c["fixed_caller_paid"].items()]
    lst = lambda l: "[%s]" % ", ".join("(%d, %d)" % x for x in l)
    m = re.search(r"theorem consts7786\s*:(.*?):=", stripped["BankCallerGen"], re.S)
    if not m or ("TB = " + lst(tb)) not in " ".join(m.group(1).split()) or ("PB = " + lst(pb)) not in " ".join(
            m.group(1).split()) or c["calls"] != 48:
        fail("consts7786 does not match the #7786 caller data")
    out = subprocess.run([sys.executable, "-I", "-B", str(gdir / "gen_callergencert.py"), "112", "952721/100000000",
                          "9527", "BankCallerGenCert", "1000000", "HS", "BankCallerGenCert",
                          str(gdir / "app7786-caller.json")], capture_output=True, timeout=60)
    if out.returncode != 0:
        fail("certificate generator failed")
    if out.stdout != (LEAN / "Nov15" / "BankCallerGenCert.lean").read_bytes():
        fail("generator output differs from Nov15/BankCallerGenCert.lean")


if __name__ == "__main__":
    main()
