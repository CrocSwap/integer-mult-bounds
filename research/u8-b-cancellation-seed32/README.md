# Four exact U8 B-stage shear rewrites

**Finite complex-supplier construction; no new kappa.** Four three-add fragments in
the selected PR942 U8 local word admit the exact rewrite

`x += a*s; y += q*x; x -= a*s` -> `y += q*x; y += (q*a)*s`.

The B stage drops from 1,918 to 1,914 scalar operations. Under the unchanged selected
binary-Horner invoice, each orientation saves 52 real-component primitives:
193,306 -> 193,254 forward and 193,354 -> 193,302 backward. All 728 arbitrary
columns and the paid rank profile are unchanged.

## Reproduce

From repository root, using Python 3.10+ and the standard library:

```sh
python3 -I -B research/u8-b-cancellation-seed32/verify.py
python3 -I -B research/u8-b-cancellation-seed32/test_package.py
```

Expected:

```text
PASS_U8_B_SHEAR_REWRITE_SEED32 rewrites=4 B=1918->1914 primitives=193306->193254/193354->193302 columns=728 controls=9 no_new_kappa
PASS_U8_B_SHEAR_PACKAGE deterministic_result=1
PASS_U8_B_SHEAR_PACKAGE_CLOSURE normal_and_optimized=PASS relocated=PASS controls=4
```

## Evidence and scope

`verify.py` pins the accepted `t37-replay.tar.gz` and canonical-word payload, applies
the four literal rewrites, compares complete exact sparse-rational B-stage matrices,
checks each symbolic three-register identity separately, reproduces baseline receipts,
and rejects nine controls: four single deletions, four wrong cross terms and one
intervening dependency touch.

`SOURCES.json` declares the complete immutable input closure: the already committed
`research/community-frontier942-audit/t37-replay.tar.gz` and the hashes of its
canonical word, baseline emitted programs, and baseline local receipts. The checker
reads only these pinned regular members, never extracts the archive, imports no
construction code, and needs no network access. It regenerates both complete baseline
programs, checks them against the archived programs and receipts, and replays the
candidate in both orientations using exact rational arithmetic. The generated result
must match the original committed `RESULT.json` byte for byte.

The package test runs normal and optimized isolated Python processes, then repeats
them in a relocated fixture containing only this package and its declared archive.
It also requires rejection of missing source pins, changed archive bytes, a wrong
canonical-word member pin, and changed result bytes. All checks use explicit failures
and remain active with `-O`.

The unchanged `hpe_emit_local.py` and `hpe_audit_local.py` additionally passed on the
candidate during validation: 728 columns in each orientation, unchanged paid profile,
25 inherited frame/wrapper controls rejected, and prefix bounds of 55/72 bits under
the retained 192-bit allowance. These validation commands are source-bound to the
original base and recorded with exact source digests in `VALIDATION.json`; they are
not needed by the one-command independent replay. To reproduce this additional
validation, create an empty directory and run (POSIX shell example):

```sh
replay=$(mktemp -d)
python3 -I -B research/u8-b-cancellation-seed32/verify.py --write-candidate "$replay/CANONICAL-WORD.json.gz"
python3 -I -B research/complex-sw4-frame8/local/hpe_emit_local.py "$replay"
python3 -I -B research/complex-sw4-frame8/local/hpe_audit_local.py "$replay"
```

The restored verifier and committed source pins address the maintainer's review of
the incomplete submitted head `c9d2523a3d30b8f6b16cf038bf723a191342ff20`.

No global owner map, complete complex-supplier invoice or outer 47-inequality assembly
was rebuilt, so no kappa change is claimed. All-size/compiler, common-label and
mutable-source realization, whole-call hosting, physical routing, precision/tape,
exact recovery and analytic transfer remain inherited. Finite replay is not a formal
proof of the multiplication theorem.

Base commit: `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`. OS-random assignment seed:
32 (complex-supplier track). The selected PR942 certificate remains unchanged.
