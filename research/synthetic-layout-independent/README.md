# Independent verification of the synthetic transform's physical layout

**Independent finite verification; no new κ and no source defect found.**
The prescribed prefix moves, chunk transposition, named-slot butterflies and
combined monomial rounds agree exactly with an independently implemented tensor
Fourier formula. Both directions include the physical layout:

\[
 A_- = L B F^-_{\boldsymbol t},\qquad
 A_+ = F^+_{\boldsymbol t} B^{-1} L^{-1},\qquad
 A_+A_-=I/M,\quad M=\prod_i t_i.
\]

The precise audited statements are `eq:combined-twiddle`,
`lem:synthetic-transform-cost`, and its concluding operator identities in
[`upstream/build/sections/06-transforms.tex`](../../upstream/build/sections/06-transforms.tex).
The source is OpenAI's pinned `adc7f1241b42e322a6451854ab7e4b4c146bf78a`;
this contribution's repository base is
`f567884aeb8851b6e794af1184119a3bfbe1e631`. At that base, the selected conditional
κ is **0.001661634653669567**, from #799 with #589 on #555. This package does
not establish, modify or independently re-verify that bound.

## Reproduce

Python 3.10 or later; standard library only; no network, solver, compiler,
external Git objects, or numerical tolerances:

```sh
python3 -B -I -O research/synthetic-layout-independent/verify.py
python3 -B -I -O research/synthetic-layout-independent/test_verify.py
```

The verifier recomputes the complete deterministic receipt and compares it with
`EXPECTED.json`. Expected first-line result:

```text
PASS_SYNTHETIC_LAYOUT: 9486 layouts; 200434 complete addresses; 4340 ring columns; 1244 extra scalar columns; 11 negative controls
```

The second command runs six test groups, including an optimized replay of an
isolated package/source closure. `--write` explicitly regenerates this package's
receipt; it is not used by the default read-only replay. SHA-256 source pins
are checked before arithmetic. Source and receipt corruption fail closed.

## Independent methods and exact coverage

`physical.py` follows the source's operations literally: move named bits to a
prefix in order; exchange whole width-K chunks to transpose their arrangement;
execute those moves on integer record addresses; apply butterflies at the
physical positions named by the descriptor; and apply the combined signed
monomial. The opposite schedule applies each inverse monomial before its
butterflies, then reverses the charged layout movements.

`reference.py` imports neither that engine nor repository/predecessor code.
It obtains the layout directly from integer axis fields, reverses each axis's
frequency bits, and evaluates the unfactored tensor character formula. It has
no butterfly recursion or simulated bit/chunk movement. For output j and input
k, its monomial exponent is `±sum_i (2r/t_i) j_i k_i`, reduced modulo `2r`.

Both engines use integer numerators with common denominator **M**. Omitting
all butterfly factors of 1/2 contributes exactly `2^(sum_i a_i)=M`, even when
the axes have different lengths. Thus the integer composite is `M·input`,
not `M²·input`. Signed rotations preserve the negacyclic relation `y^r=-1`.

| Check | Fixed domain and completed coverage |
| --- | --- |
| Symbolic layout and coordinate bits | Every `ell=2..18`, `D=1..5`, long/short mask, and `K=1..ell-1`: **9,486 layouts**, **480,267 named-bit address comparisons**. Literal movements agree with the direct layout formula and their inverse. |
| Cartesian layer groups | **93,868 chunk rounds**. All participating bits occupy the same offset in consecutive K-bit chunks; prefix/group/suffix partition every address bit. This gives the full `[P] × [2^K]^D × [S]` address range, with its exact cardinality M. |
| Complete address permutations | `ell=2..7`, `D=1..4`, all masks/K with at most 12 total address bits: **211 layouts / 200,434 addresses**, including all four combinations of zero/nonzero remainder b and one/multiple chunk groups q. |
| Complete ring-module matrices | Every `ell=2..4`, `D=1..2`, mask and K, plus `(ell,K,long_axes)=(2,1,(false,false,true))`: **37 configurations / 4,340 columns**, counting both directions. |
| Additional coefficient columns | Every remaining coefficient column for the ell=2 configurations and both mixed two-axis ell=3,K=2 orders: **1,244 columns** across both directions. |
| Dense inputs and normalization | **74 direct-operator checks** on signed integer arrays from seed 80, plus **37 opposite/forward compositions**. |
| Written source illustration | `ell=6,K=2,(long,short)`: **16 further scalar columns**, covering records 0, 1, 80, 2047 and coefficients 0, 63 in both directions. |

The direct-operator comparisons check **12,479,696 individual coefficients**,
including zeros. Per-configuration matrix digests and aggregate layout evidence
are retained in `EXPECTED.json`. `DOMAIN.json` specifies the finite domain and
stopping rule; there is no adaptive supplier search.

For each tested configuration, both exact operators are linear over
`R_r=C[y]/(y^r+1)`: record permutations, addition/subtraction, and multiplication
by monomials are R-linear. Equality on all M ring-module basis columns therefore
determines the operator on arbitrary complex polynomial payloads for that
configuration. The additional scalar columns and dense inputs provide separate
implementation diagnostics. This finite linear-algebra argument is not a
proof-assistant formalization or proof of an all-size theorem.

## Failure detection

Eleven controls each preserve a concrete differing coefficient, with its exact
numerator and denominator, in the receipt:

- Omit the long-axis leading round; include the new branch bit in k; read lower
  **physical** bits instead of lower **named** slots.
- Replace negacyclic signed rotations by ordinary cyclic rotations.
- Use the wrong opposite twiddle sign; apply the opposite twiddle after the
  butterfly; omit final layout restoration.
- Omit the chunk transposition; omit prefix extraction; reverse L's direction.
- Mistake the normalized opposite for an unscaled inverse.

The direction control uses two short axes followed by one long axis at
`ell=2,K=1`. Its slot permutation is `[2,0,1,3]`, a nontrivial three-cycle.
Tests restricted to involutive layouts cannot detect substituting L^-1 for L.
For this control the first differing coefficient is at record 2/coefficient 0:
`-256/16` instead of `-128/16`. These are intentionally wrong implementations,
not counterexamples to the source lemma.

The harness separately checks signed monomials across positive and negative
wraps, changed/missing source files, deleted receipt coverage, altered witnesses,
optimized Python, and execution outside the repository in a minimal closure.

## Scope, dependencies, and related work

K is varied freely through its positional range to exercise layout branches.
These are **not claims of 9,486 asymptotically admissible theorem instances**:
we do not validate `K=floor(d^c)`, the cutoff p1, comparison bands, disk/grid
formats, finite precision, or the asymptotic cost. Dense signed inputs exercise
the exact algebraic counterpart and need not lie in the unit disk.

The polynomial suffix is preserved as a whole record by the modeled layout.
This Python indexed-address implementation does not discharge the fixed-tape
stream-movement or chunk-interchange lemmas, the simultaneous layer's physical
realization/cleanup/precision, source access or recursive hosting, the claimed
runtime, Q_p truncation, convolution recovery, or inherited analytic hypotheses.
The existing movement invoices remain: O(dK) prefix moves, at most Dq−1 chunk
exchanges, and the same charged inverse. Checking their finite counts does not
prove the fixed-tape costs per operation or improve them.

Credit OpenAI for the retained proof and Douglas Colkitt for the repository's
original dependency audit. The synthetic-transform lineage in the source credits
Nussbaumer–Quandalle and Harvey–van der Hoeven. No novelty or literature-priority
claim is made for the transform or its layout.

**@androolloyd's [PR673](https://github.com/CrocSwap/integer-mult-bounds/pull/673)**,
inspected at `0b4f514c60d9bc7786415d7cbc24754f24d6dc3b`, already provides independent
synthetic-transform arithmetic, bit-reversed frequency order, signed monomials,
convolution, and Boolean chunk interchange in a dirty-echo integration. Its
`research/dirty-echo-integration/transform.py` returns `BF-` and `F+B^-1` in
axis-major coordinates. This package instead checks the **complete prescribed L**:
prefix extraction, chunk transposition, physical Cartesian round groups, and
final L^-1 restoration, with the above independent bounded matrix coverage.
No PR673 code or result is imported. Its negative supplier-cost result is not
reopened; no replacement supplier is proposed. Related #702/#712 cold-wrapper
and #874 X4 audits motivated rejecting duplicate candidate tasks.

`CLAIM.json` records the OS-random assignment seed **80**, candidate choices,
local coordination claim, and completed handoff. There was no pinned sprint
issue. Source hashes and exact dependency/context pins are in `SOURCES.json`;
validation evidence is in `VALIDATION.json`.

Prepared by **Philipp (@mightyOil)** with substantial **OpenAI Codex assistance**
in selection, implementation, mathematical explanation, testing and scoped
review, including a separately delegated direct-character implementation and
read-only AI review. This is independent implementation evidence, **not
independent human peer review**. New files are Apache-2.0; the unchanged upstream
source retains its CC0 license. No existing generator, selected certificate,
source artifact, or file under `upstream/` is modified.
