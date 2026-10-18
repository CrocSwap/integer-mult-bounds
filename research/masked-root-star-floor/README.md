# Masked root-star floor on P112: complete trimmed-star census (no new kappa)

**Scoped negative / method-obstruction result; no new kappa, no supplier.** In CrocSwap/integer-mult-bounds#717's B14
decoder model on the pinned P112 label set, masked E-graph identity (CrocSwap/integer-mult-bounds#717 D1(a): exactness
only on the 6720 even-pair entries, the 5824 odd entries fixed by cost-0 singleton terms),
this package answers one bounded question: can root-star decoders with **trimmed** supports
`N(alpha)` (pairing rank 7 atoms — the mixed-beta class CrocSwap/integer-mult-bounds#717 D1 leaves open) improve on
the coordinate decoder's copy cost `cst = 64`, with any number of terms?

**Answer: not by the frame-substitution argument, and the argument's exact limit is
recorded.** A complete census of all 240 root-star supports and all 57,600 ordered support
pairs (exact pairing ranks, exact frame-hit counts over the 1260 E-graph 8-cliques) gives:

- the covering bound over the whole family is exactly **784/13 ≈ 60.31**
  (`cst >= 10080 * min(beta/hit)`, `min(beta/hit) = 7/1170`);
- the hoped-for 64 bound is **falsified**: beta-7 trimmed atoms exist that meet **1170** of
  the 1260 frames (the task card's threshold for the bound to hold was 1102), so nine or
  more cheap trimmed stars at total cost 63–64 are not excluded by frame counting;
- over atoms of pairing rank at least 8 the bound is **exactly 64**, sharp at the eight
  coordinate stars, so all the slack sits in the **7,616** beta-7 atoms (the eight best are
  recorded in `RESULTS.json` as leads for an assembly search).

The covering lemma, the reduction lemma, the falsification record and the exact scope are
in [PROOF.md](PROOF.md). The result extends the star floor of
[PR968](https://github.com/CrocSwap/integer-mult-bounds/pull/968) and CrocSwap/integer-mult-bounds#717 D1(b)/(c) from
eight-term all-pairs statements to arbitrary term counts under the masked identity inside
this family, and it isolates the remaining window `[784/13, 64]` as an assembly problem.
No construction below 64 is claimed; the paid moment is unchanged.

## Reproduce

From the repository root, Python 3.10+, standard library only:

```text
python research/masked-root-star-floor/verify.py
```

Expected final lines include:

```text
PASS C.bound-beta-ge-8-is-64 | bound over beta>=8 atoms = 64
PASS C.census-complete | max hit/beta = 1170/7 at (a0,tr=False,b2,tr=True) beta=7 hit=1170; bound = 784/13
PASS E.coordinate-cst-64 | cst = 64
FAILS: none
```

The run rebuilds the 120-line E8 model, the 1260 frames and the full 57,600-pair census,
and compares every field of the recomputed receipt with the committed `RESULTS.json`
(mutation-detecting: altered ranks, hit counts, frames or model facts fail the comparison).
`--write /new/file.json` writes a fresh receipt; `--check PATH` compares against another.

## Files

`verify.py` (checker, exact integer/F2), `RESULTS.json` (receipt), `PROOF.md` (statement and
argument), `SOURCES.json` (pins), `CLAIM.md` (task card), `NOTICE.md` (attribution). The E8
line enumeration is adapted from `research/complex-frame-pair-decoders/verify.py` (CrocSwap/integer-mult-bounds#968
package, Apache-2.0) with attribution; nothing is imported and no predecessor file changes.

## Scope and inherited obligations

Covered: the masked identity on P112, root-star supports (untrimmed `C(alpha)`,
self-trimmed `N(alpha)`), arbitrary real coefficients, any term count. Not covered: deeper
trims and unions, non-star supports (CrocSwap/integer-mult-bounds#717 D3's P111/P104 hits are non-star and beat 64 off
P112), general supports (CrocSwap/integer-mult-bounds#717 D1(e)'s sampled 43.8 bound), other punctures, and any
assembly of the recorded beta-7 leads. Finite replay is not a formal proof of the
multiplication theorem. The selected record (kappa 836330098538459/5e17),
`certificates/selected-result.json`, `upstream/` and all frozen pins are unchanged; all
all-size/compiler, common-label/mutable-source, hosting, precision/tape and analytic
obligations of the selected construction remain inherited and unchecked here.

## Credit and overlap

- **DreamingOfClouds** ([PR717](https://github.com/CrocSwap/integer-mult-bounds/pull/717),
  [PR595](https://github.com/CrocSwap/integer-mult-bounds/pull/595),
  [PR604](https://github.com/CrocSwap/integer-mult-bounds/pull/604)): the B14 model, the
  masked reduction D1(a), the mixed-beta open problem and the sampled covering bound D1(e).
- **themilkman216** ([PR968](https://github.com/CrocSwap/integer-mult-bounds/pull/968),
  with Anthropic Claude assistance): the eight-term all-pairs floor, and **woklerx**
  ([PR1077](https://github.com/CrocSwap/integer-mult-bounds/pull/1077), with OpenAI Codex
  assistance): its complex extension; both defer masked E-graph identities.
- **seed48 package** (`research/root-pair-first-drop-seed48/`): second deferral of masked
  identities; **Joel Pulikkan / GamingPuzzled**
  ([PR620](https://github.com/CrocSwap/integer-mult-bounds/pull/620)): star floors and the
  complex frame decoder of cost 64; **Mihir Srivastava**
  ([PR845](https://github.com/CrocSwap/integer-mult-bounds/pull/845)): the fixed-reader
  ninth total, whose scope excludes masked completions.
- The open star-decoder PRs
  ([#631](https://github.com/CrocSwap/integer-mult-bounds/pull/631),
  [#669](https://github.com/CrocSwap/integer-mult-bounds/pull/669),
  [#725](https://github.com/CrocSwap/integer-mult-bounds/pull/725),
  [#732](https://github.com/CrocSwap/integer-mult-bounds/pull/732),
  [CrocSwap/integer-mult-bounds#1171](https://github.com/CrocSwap/integer-mult-bounds/pull/1171)) concern the bit-side
  label-code star model and puncture ratios; this result is on the complex B14 side and does
  not import their claims.
- **Concurrent masked-model results (found in the final overlap refresh).**
  [CrocSwap/integer-mult-bounds#1212](https://github.com/CrocSwap/integer-mult-bounds/pull/1212) proves the E-graph
  eight-term floor via rank-8 gauge rigidity, and
  [CrocSwap/integer-mult-bounds#1213](https://github.com/CrocSwap/integer-mult-bounds/pull/1213) classifies the masked
  coordinate component for eight terms (cost 64 along continuous paths from the coordinate
  decoder); both explicitly leave nine or more terms open. [CrocSwap/integer-mult-bounds#1191](https://github.com/CrocSwap/integer-mult-bounds/pull/1191)
  proves one-sided root-linear masked rigidity at arbitrary term count — one factor in the
  root-coordinate space forces all-pairs exactness. This package is complementary to all
  three: it covers **arbitrary term counts with root-star support patterns and unrestricted
  (non-root-linear) coefficients on both factors**, the setting where the trimmed beta-7
  atoms live; no predecessor census covers those atoms. Coordination claim:
  [discussion CrocSwap/integer-mult-bounds#1210](https://github.com/CrocSwap/integer-mult-bounds/discussions/1210)
  (which [CrocSwap/integer-mult-bounds#1213](https://github.com/CrocSwap/integer-mult-bounds/pull/1213) cites as the
  announced scope of this census).

Prepared by **Navinor** with help from opencode. New contributions are under the
repository's Apache-2.0 license.
