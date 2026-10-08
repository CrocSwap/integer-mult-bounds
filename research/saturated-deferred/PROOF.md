# Integrated saturated deferred witness

## 1. Inputs and exact change

The physical networks and interfaces are Zhihao Chen's PR97 at
`f5f9c56e637463cac1e300d1589ccf42838f688a`, based on Swapnil Jain's
`741e7aa078392553815df7926ee17ac5e25a8c38` round-seven/round-six sources.
The selected saturation is djsmanchanda's PR99 at
`0622dcce6a897567e4eb6bdfedc7def66ab21346`. The exact refinement and balanced
transfer follow Rohan Arun's PR100 at
`3dbe4e18a6a20f8115eb2f9a34a46254357d7791`.

Only the bit schedule's 22 selected readout spaces and resulting sorted
readout order change from the PR97 input. The source witness, scalar gates,
retained totals, V leaves, lifted gate frames, late copies and complex
network are unchanged. Every other schedule field is compared exactly.
The selected spaces are explicit integer bases. Each contains its previous
space, lies inside the actual entrance frame and every affected target
hyperplane, and has nonsingular Gram form for `G = I − J/9`.

The PR99 reverse sweep saturates each space inside its admissible cap to the
exact rank of that cap's Gram matrix. This qualification includes the actual
subsequent target spaces. All target chains are checked again after sorting;
dimension order alone would not prove nesting. The independent changed-frame
audit and the full rational/generic-pivot audit both run on the selected file.

## 2. Whole-word applicability

The phase-one closure and untouched-slot conditions are inherited unchanged
and replayed. A deferred role still contains its arbitrary original dirty
value when read. All subsequent gates and inverse operations retain their
scalar action. The complete forward bit word and its complemented,
bank-exchanged time reflection are replayed on every ordinary and dirty basis
column. The stable fan ordering from PR97 is retained and checked against the
new frame paths. Copied-center operations remain explicit copies; they do not
erase an unknown scratch register.

For an idempotent A, write `D_A = [[I−A,A],[A,I−A]]`. Let P,Q be the triple
line projectors, σ an auxiliary entrance projector of rank f, and r = h−f.
PR97's stage-one exterior is

`E1 = I − I⊗Q + σ⊗Q = I − (I−σ)⊗Q`.

Stage two has exterior `E2 = (I−P)⊗I + P⊗σ`. Both have rank `m−r`.
The complementary endpoint gauges preserve the completed address swap, and
their residuals have the large block `m−2r` plus the retained inner profile.
These identities depend on the projector conditions and exact chains already
checked for the enlarged σ; they do not depend on its original dimension.
Both data connectors and the rank-one bit correction remain charged.

The complex network and correction are identical to PR97. Its actual signed
readout satisfies `AMV = I`; inverse gates reverse order and negate their
coefficients. The pre-translation by `P_U 1`, inverse rank-one child and sign
wrapper remove the complex phase residual. The exact full complex identity,
actual geometric ledger and small complete Fourier-address controls are
rerun. Omitting the translation or replacing the inverse by a forward child
is rejected. No characteristic-two cancellation is used for this argument.

The common-basis applicability follows the preserved finite nonzero-minor
witnesses and the inherited finite-family rational existence argument.
The full saturation check verifies all added high-rank steps under both
conjugations at the same witness point. The unchanged staircase check verifies
its symbolic cut bounds and nonzero lower witnesses. These finite facts
retain the original all-size framed compiler and transfer hypotheses.

## 3. Complete paid recurrence

For h = 23, v = 1771 and R = 28866:

- `m = 529`, `N = v² = 3136441`, `W = 2N + 2vR = 108516254`.
- `L = 2vh(h−1) = 1792252`.
- `s = Wm−N+L = 57403754177` and `N−L = 1344189`.

The independently rebuilt histogram delta from PR97 is:

| Child width | Multiplicity change |
|---|---:|
| 1 | −177100 |
| 507 | −31878 |
| 509 | −24794 |
| 511 | +56672 |

Its weighted rank sum is zero. For example, replacing `[507,1,1]` with
`[509]` decreases the recursive moment at every exponent between zero and
one. The acceptance gate also reconstructs the entire histogram from the
fresh literal auxiliary/data/center rank counts and selected σ dimensions.
Thus the final certificate does not depend only on this small delta.

The complete complex rank remains 119453132304 at `m = 576`,
`W = 207387136`. The independent checker rebuilds its internal transitions,
exteriors, both connectors and rank-one corrections separately.

## 4. Bridge and exact assembly

The actual maxima are 527 and 552. Their least halving degrees and wire
bitlengths determine the product row coefficient 5417 and row degree 12000.
The complex literal scalar count is 374340 per one-axis word. The retained
conservative scalar charge G, semantic allowance
`E = 64(W+m+G+1)³`, `B = s+E`, and `C0 = 32mB²` are regenerated from the
actual ledger. Literal-charge, induction and row-stock gaps are all checked.
The old degree-17 bit bridge is invalid here and is a negative control.

The balanced transfer is PR100's application of the preserved common
positional layout and paid routing argument: complete low-coordinate FFT
groups supply prefix work margin `1−ε`. Its separate geometric constraint
`1−ε(1+c)` remains positive. The original prefix-cost interpretation is
explicitly tested and rejected at the new parameters. The original precision,
fixed alphabet, tape, padding, prime packing and recovery assumptions persist.

Two distinct rational log/exponential enclosures accept bit saving

`a_b = 31993457448237/500000000000000000`

and reject its next `10^-18` grid point. The complex saving used for transfer
is `a_c = 36926111/500000000000`; its complete moment is checked independently.
At `β = 1/10` and assembly backoff `10^-12`, all 47 strict constraints and
seven margins pass for

`κ = 6398282083297/100000000000000000`.

The next assembly grid point is rejected. The resulting statement is
conditional `T(n) = O(n (log n)^(1−κ))` under the same inherited analytic and
all-size implementation hypotheses. Arithmetic acceptance alone would not
establish those hypotheses or the physical lemmas above.

## 5. Attribution and verification boundary

- **Swapnil Jain**, with the original Claude assistance disclosure: the
  deferred readouts, V leaves, lifted frames, late copies, h24 complex
  producer, common flag/staircase basis and frozen finite witnesses.
- **Zhihao Chen / jacklightChen**, with Codex assistance: reflected ledgers,
  commuting fan order, nonzero endpoint gauges, signed complex correction,
  literal bridge and retained-main-assembly integration in PR97.
- **djsmanchanda**, with Codex assistance: nondegenerate readout saturation,
  the selected 22 changed spaces and exact independent delta audit in PR99.
- **Rohan Arun**, with Codex assistance: exact moment refinement and the
  balanced transfer of the signed networks in PR100.
- **Aurel Prosz / Paureel**, **Avi Eisenberg / ikeboy**, **RaD / hipotures**,
  **icekylinx**, **James Chang**, **Dominik Scholz**, and all predecessor
  contributors retain the credits recorded in the preserved NOTICE files.
  **Douglas Colkitt / CrocSwap** supplies the community framework; the
  **OpenAI** manuscript and inherited analytic results remain credited.

This combined reproduction and source closure were prepared for Thomas
DiFiore with substantial OpenAI Codex assistance. The original authors retain
credit for their constructions. These checks are not independent human peer
review, a formalization of the full theorem, or a global optimality claim.
