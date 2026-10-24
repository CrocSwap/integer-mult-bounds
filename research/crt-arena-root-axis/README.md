# One root axis on a shared Beneš arena

**Scoped counting proof. No new κ.** The selected conditional exponent stays
`60403/20000000 = 0.00302015`.

## Scope and evidence

Original card: `uniform-transfer-audit`, refined to one open question of the
uniform CRT evaluator. That package proves

```text
E(p, ell) <= 2^{4 ell} (p+2)^{16}
```

for per-table scans, with constant `C = 1`, and asks whether one root-axis
query still fits the same allowance when every logical access scans a single
shared arena, as in PR #4192, after the CRT offset is included.

[PROOF.md](PROOF.md) answers that question for one axis. The axis pays the
pinned one-axis CRT bill, writes four rotation tables, and compiles each
table on the PR #4192 arena, including one protected bit query per network.
Every arena tape action may also pay one schoolbook product of two `w`-bit
words, `w = 4(p+2)`. For every integer `p >= 2` and `1 <= h <= ell <= p`,
the sum is at most `2^{4 ell} (p+2)^{16}`.

The same charge on all `8(p+2)` axes exceeds the allowance at `p = 2`,
`ell = 2`, `h = 2`: `1241895956864 > 1099511627776`. The per-table proof
already covers that batch by a different schedule. This package does not move
that constant onto the simultaneous arena batch.

At that same one-axis point the bill is `38809248652` against
`1099511627776`, and `28 U <= E < 29 U`.

Reservoir placement, the ordinary callee, sparse repair, native execution and
the outer theorem are not proved. The arena simulator and the retained Beneš
compiler are not executed. The bit-step count is the counting argument.

Source commits, Git blobs and SHA256 pins are in [SOURCES.json](SOURCES.json).
The selected record and catalogue are historical provenance. The PR #4192
proof is not an ancestor of canonical main, so its bytes are the unmodified
vendor file
[vendor/pr4192-crt-benes-scan-PROOF.md](vendor/pr4192-crt-benes-scan-PROOF.md),
commit `519d811cc48693ad9969d6d7994bef3940167005`, SHA256
`c3eb4e14dc5ee0102cbf77c4a0e61db9989c2b8a0eaf7f0659a6e39373197474`.
See [vendor/NOTICE.md](vendor/NOTICE.md).

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/crt-arena-root-axis --check-only
python3.12 -B research/crt-arena-root-axis/verify.py
```

The verifier prints `PASS_CRT_ARENA_ROOT_AXIS`.

## Open next questions

1. Does a word-level scalar inventory, with a fixed number of `w`-bit
   operations per arena record, bring all `8(p+2)` axes inside the same
   allowance? The schoolbook-per-tape-action majorant does not: at `p = 2`,
   `ell = 2` the 32-axis bill is `1241895956864`, above
   `1099511627776`. The first step is to replace `8 w^2` per tape action by
   the record comparisons named in PR #4192 §2 and repeat that comparison.
   It is blocked here because that tighter inventory is not the theorem.
2. With one axis inside `E`, do the reservoir and the ordinary interchange
   callee of `CRT.md` §3–§4 still fit their stated bills? The first step is
   the `H >= G` comparison already named by `research/crt-uniform-evaluator`.
   Placement geometry remains PR #4174 and is not an input here.

## Credit

Cinna Davis supplies the CRT construction and the shape of `E(p, ell)` in
PR #4100. `research/crt-uniform-evaluator` supplies the one-axis
reconstruction bill, the rotation-table tariff and the open question; that
package was prepared by unpaidmoon with Cursor Grok assistance. ToikY's
PR #4192 supplies the arena census, the tape invoice and the `O(w^2)` scalar
shape. The vendored proof is unmodified. The coverage map in PR #4311 records
the evaluator row this question continues.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review or proof-assistant acceptance is claimed.
