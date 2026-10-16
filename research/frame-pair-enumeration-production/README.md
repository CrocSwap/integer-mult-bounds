# Production neighborhood enumeration for PR968 frame-pair decoders

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`research/complex-frame-pair-decoders/verify.py:frame_pair_solutions` still
rebuilt partner lists with nested list comprehensions on every mask. woklerx’s
opt-in adapter `research/frame-pair-enumeration-fast-seed93/` (incorporated
[#1099](https://github.com/CrocSwap/integer-mult-bounds/pull/1099)) already
proved exact eight-bit neighborhood masks with identical ordered solution
streams. This package wires that equivalent rewrite into the **production**
PR968 verifier.

Dependent VERIFY packages that previously live-pinned the production path
demote that pin to provenance. `selected-p104-port-adapter`,
`p104-nullpair-compensated-shear-seed318bd5`, and `p104-term-shear-seed8be7`
retarget their live pairwise model pins to this package’s
[`baseline.py`](baseline.py). Legacy WT-hash loaders
`p104-asynchronous-carrier-bound`, `root-pair-first-drop-seed48`,
`complex-decoder-field-extension-seed44`, and
`e8-factor-linear-overcomplete47` likewise load the vendored baseline instead
of the rewritten production `verify.py`.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/frame-pair-enumeration-production/verify.py
python3.12 -I -O -B research/frame-pair-enumeration-production/verify.py
python3.12 -B scripts/research_package.py --package research/frame-pair-enumeration-production
taskset -c 0 python3.12 -I -B research/frame-pair-enumeration-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_FRAME_PAIR_ENUMERATION_PRODUCTION frames=1260 decoders=7168 term_ranks=57344 corruption=… certs=0 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/frame-pair-enumeration-production outcome=completed
PASS_IDENTICAL_FRAME_PAIR_ENUMERATION_PRODUCTION_RECEIPTS
```

Default verify is read-only. Scope is PR968 sections D/E/H (complete frame-pair
census, attaining chain, controls). Section G binds the selected kappa record
and is outside this tooling change. Temp-copy omission foil rejects via
assertion failure or receipt divergence. Package gates under `-O` still compile
loaded checkers with `optimize=0`. Full `make verify`, selected cold replay,
Lean, and multiplication-theorem obligations were not rerun.

## Result

On Linux / CPython 3.12.3 with `taskset -c 0`, five alternating fresh-process
pairs gave median complete D/E/H wall time **13.642 → 4.421 s (3.09×)**.
Details are in [`RESULT.json`](RESULT.json). Timing is host-descriptive and is
not a correctness gate. Every ordered solution stream and term-rank receipt
matches between baseline and production (7,168 decoders; 57,344 term ranks).

## Why the neighborhood masks are equivalent

For a fixed selected subset S of the first frame, a second-frame member g is a
permitted partner of f in S exactly when its nonzero neighbors inside S are the
singleton {f}. Encoding those neighbors as an eight-bit integer turns this into
`hit != 0 and hit & (hit - 1) == 0`. Iterating g in frame order appends the same
partner lists in the same order. The reverse-neighborhood masks handle the
complementary half. Injectivity guards are retained. See
`research/frame-pair-enumeration-fast-seed93/PROOF.md`.

## Overlap and credit

Closest priors:

- `research/frame-pair-enumeration-fast-seed93/` / [#1099](https://github.com/CrocSwap/integer-mult-bounds/pull/1099)
  — opt-in neighborhood adapter; this is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2039/#2054
  shared-point, #2100 ternary, #2117 DisjointTensor, #2150 mixed-point,
  #2194/#2210/#2231/#2239/#2257/#2263/#2276/#2320/#2329/#2348/#2357 production
  rewrites; #1076 quadratic-affine) was not reopened. Fresh overlap refresh
  found no competing production rewrite of `frame_pair_solutions`.

Credit themilkman216 and woklerx. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should section G be repinned to the current selected kappa
   record in a separate package?
   **Why it matters:** At this base the full verifier fails only
   `G.selected-record`.
   **First step:** Dedicated selected-record refresh for section G only.
   **Blocked by:** Outside this identical-receipt tooling stop rule.

2. **Question:** Should packages that only cite the frame-pair floor in prose
   drop their provenance pin entirely?
   **Why it matters:** Several packages keep historical verify.py provenance
   after demotion.
   **First step:** Maintainer preference on provenance retention.
   **Blocked by:** Attribution/navigation policy.
