# Joint rank-two child boundary for paired frame climbs

**New conditional local interface mechanism. No new κ is claimed.** On the selected width-73 local word, 753 pairs of rank-one frame transitions can be described as tagged two-register rank-two boundaries. The native word is unchanged. If one recursive rank-two call can serve each such direct-sum boundary at the usual rank-two price, the local profile's exact fixed-word ceiling rises by at least **5.241623654%**. The proposed child contract has not been admitted or physically hosted, so this is a costed mechanism candidate, not an improved multiplication bound.

## Mechanism

For a register transition from frame `U` to frame `F`, the child boundary is the quotient `F/U`. A selected pair consists of two distinct register lanes, each with a one-dimensional quotient. Their tagged direct sum has dimension two:

\[
  (F_1/U_1) \oplus (F_2/U_2), \qquad \dim=1+1=2.
\]

The new interface contract `J2` asks one rank-two recursive child to accept and return this tagged product. It keeps the lanes separate; it does not identify their basis vectors or drop either lane's dirt.

There are three exact classes in the pinned word:

1. **574 A/B gate pairs.** In one `add` gate, both participating registers grow by one into the same frame `F`. On the two register lanes the gate is the rational shear
   `T_c(x,y) = (x + c y, y)`, where `c` is the exact recorded numerator divided by denominator. Its inverse is `T_{-c}`. Both old frames lie in `F`, so the full dirty input maps inside `F × F`; the two-lane boundary has codimension two.
2. **16 scheduled early-cleanup pairs.** The cleanup gate's two participants both grow by one into its scheduled frame. The same exact shear argument applies.
3. **163 terminal pairs.** There are 326 rank-one terminal transitions. Pairing them by increasing register id yields 163 direct-sum terminal boundaries. Their map is the identity on the tagged product; no register values are identified.

The finite scan covers all 3,451 A gates, 1,846 B gates, 116 scheduled early-cleanup entries, and 704 terminal registers. As one gate example, A[1291] adds register 232 into register 228 with coefficient `+1`. Register 228 grows from `span{454}` to `span{454,30}`; register 232 grows from `span{472}` to the same target because `472 = 454 xor 30`. The tagged quotient basis is `((228,30),(232,454))`, and the gate map is `[[1,1],[0,1]]` with inverse `[[1,-1],[0,1]]`. Both lanes remain distinct; their joint quotient dimension is exactly two.

The pairs partition 1,506 rank-one child calls into 753 rank-two calls. The resulting virtual per-call profile is

`{1:906, 2:1171, 3:432, 4:142, 5:82, 8:8}`,

with the same rank mass, 5,586. Under the retained selected-word model, the idle mass remains 1,646, `m=73`, `W=896/9`, the centre charge is 64, and the halving guard gives idle-rank cap 51.

For `0 < a < 1`, the optimistic cost change per pair is strictly favorable:

\[
2(1/73)^{1-a}-(2/73)^{1-a}
=73^{a-1}\left(2-2^{1-a}\right)>0.
\]

The exact ceiling calculation prices the whole resulting histogram, including the fixed idle remainder and centre charge; it does not assume that this local inequality by itself supplies a recursive multiplier.

## Exact screening and full charge ledger

`verify.py` calls the repository's outward-rounded rational ceiling routine with a `10^-12` grid. The baseline fixed-word ceiling is bracketed by `0.001690054109` and `0.001690054110`. The paired profile is bracketed by `0.001778640386` and `0.001778640387`. Even comparing the candidate's lower endpoint with the baseline's upper endpoint, the ideal gain is at least `5.241623654%`. The candidate's relaxed moment at `a=1/99` is strictly greater than one (lower bound about `1.0232932528`), so the mechanism does not reach the target-scale budget.

The 5% threshold is tight against extra child work. At `a = 1.05 × 0.001690054110`, the candidate has headroom for at most **11 extra rank-one children per local call** if each is charged by removing the same amount of fractional rank-51 idle mass. Twelve such children already miss the 5% threshold. This is only the child-moment budget; it does not pay for the joint boundary's source adapters, copies, phase/precision conversion, or hosting. In particular, one extra rank-one adapter for each of the 753 pairs would overwhelm the available headroom.

| Cost | Optimistic charge used for the screen | Evidence or remaining obligation |
|---|---|---|
| Source access | No extra scalar reads are added to the recorded word | The new call must still receive both lanes. Whether a joint call avoids an extra copy or adapter is unproved. |
| Native helper operations | Zero additional scalar gates | The word is pinned and unchanged. |
| Recursive children | Replace two rank-one calls by one rank-two `J2` call for each of 753 pairs | Exact virtual profile and moment are checked. The `J2` recursion supplier is unproved. |
| Frame changes | Zero | The original frame chains remain byte-for-byte unchanged. |
| Copied information | Zero in the tagged direct-sum model | A physical layout showing no added copies is not supplied. |
| Hosting | No added local rank mass; 753 fewer recursive call boundaries | Whole-call ownership and the physical width inventory are not rebuilt for `J2`. |
| Restoration | Zero additional local gates | The gate shear has an exact inverse; the shared child's terminal restoration interface is unproved. |
| Precision and phases | Assumed unchanged | The joint boundary's phase and precision transfer are not admitted. |
| Interface transitions | Not priced; at most 11 extra rank-one child costs per call fit while preserving the 5% margin | This is the central open cost: prove the rank-two boundary is a legal single child, and price all adapters, copies, hosting, and restoration it needs. |

The zero-overhead assumptions make this a deliberately favorable screen. They do not establish that the new contract is realizable. The reported `a/(1+a)` value is only a complex-side profile cap under the retained transfer; it is not a new κ. The selected bit supplier, global owner map, all-size construction, analytic transfer, and full assembly are unchanged and not replayed here.

## Reproduction

From the repository root:

```sh
python3 -B research/complex-joint-child-seed0d762/build.py
python3 -B research/complex-joint-child-seed0d762/verify.py
python3.12 -B scripts/research_package.py --package research/complex-joint-child-seed0d762
```

Expected verification output includes:

```text
PASS_JOINT_CHILD_INTERFACE_CANDIDATE pairs=753 gain=5.241623654%
PASS_NEGATIVE_CONTROLS missing_pair,duplicate_pair,changed_gate_map,bad_quotient_vector
LIMIT no supplier admission, physical cost, global assembly, or new kappa
```

The recipe pins the decompressed source word SHA256 `c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`; the verifier also checks that the selected slot output pin has the same digest. The verifier independently reconstructs all A/B, scheduled cleanup, and terminal frame changes using exact F2 subspaces, validates the integer shear and inverse, recomputes the full rank bill, and rejects four mutated recipes. It uses only the Python standard library plus the pinned repository ceiling routine.

In this worktree, direct replay passed under Python 3.14.7 both normally and with `-I -O`. Python 3.12 is not installed locally, so the registered `research_package.py --package` mathematical replay was not run here. `--check-only` passed its metadata and source-pin checks; it is not a mathematical acceptance check.

## Review status

Draft review is at [PR #1764](https://github.com/CrocSwap/integer-mult-bounds/pull/1764); the result handoff is [Discussion #1765](https://github.com/CrocSwap/integer-mult-bounds/discussions/1765). The draft status reflects the unproved physical `J2` supplier and its overheads.

## Scope and predecessors

The selected word comes from `research/gauge44-slots` and is the word selected by the current result. Earlier frame coalescing changes the dimension jump within one register. This mechanism instead joins quotient calls across two register lanes at a shared gate or a common terminal boundary. It leaves the source frames, scalar word, fixed coverage identity, and owner map unchanged. The frozen provider mixture bound in `research/heterogeneous-owner-assembly` does not include this joint boundary contract. PR #1348 changes coverage thresholds, which is also a different mechanism.

The result is conditional on admitting `J2`. It does not show that an arbitrary product of two scalar children can be supplied by an existing rank-two multiplication recurrence. Supplier construction, actual source access, physical copies, host assignment, restoration, phase/precision transfer, and full assembly remain open. This package preserves the original selected record and all frozen sources.

## Open next questions

- Can an existing complex recursive supplier implement `J2` on arbitrary tagged one-dimensional quotients without extra source copies?
- What minimum adapter, restoration, precision, and whole-call hosting charge does a physical `J2` implementation require, and does the 5.24% ideal headroom survive it?
- Can the joint contract be integrated into the selected supplier while preserving every arbitrary-dirt column and terminal frame?

## Credit

This is a new local interface proposal and exact profile screen prepared by Cinna Davis with substantial OpenAI Codex assistance. It reuses the selected word, the fixed-word ceiling, and their credited upstream work without modifying or claiming those constructions. The contribution is licensed under Apache-2.0.
