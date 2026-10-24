# Verified conditional exponent from the four-alias construction

The completed strict global admission and modern outer replay give

```
kappa = 0.0016972105695892372197269999999999999999999998999999999999999999999999
```

Equivalently, with the exact accepted complex endpoint
`C = 0.001697210569589237219727`, this is `C - 10^-46 - 10^-70`.
The resulting conditional bound is `T(n) = O(n (log n)^(1-kappa))`.
It exceeds PR2374's exact constructed claim at
`5449da65da12bdfd94675dccc38731eaa91e93b6` by approximately
`1.5618687466793133e-8`, or `0.000920264785%`. This is an incremental
improvement. PR2374 is a pinned comparison, not a claim about maintainer
selection or universal optimality.

Base commit: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`; OS assignment
seed39. The words continue PR2226, PR2269 and PR2339. This directory
preserves actual output bytes from
`/home/zoe/MP/maths/mult/seed39-four-outer-20261015T0914Z`.
`ARCHIVE-VALIDATION.json` hashes every archived receipt and log.

## Reproduction and acceptance

From the repository root, with NumPy, SciPy and SymPy1.14.0 available:

```
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/verify_global.py --out /fresh/absolute/output
```

The expected final status is `PASS_FOUR428_CONDITIONAL_BOUND`, followed by
the exact decimal above. This command replays the global admission and
outer checks using explicitly hash-bound archived native outputs. A separate
`replay_native.py` command regenerates those local native artifacts. Receipt
reuse is not described as fresh native compilation.

The completed outer stage is also reproducible independently from an actual
completed strict candidate directory:

```
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/global-admission/outer-screen/run_outer_admission.py --strict /absolute/strict --out /fresh/outer
```

Expected: `PASS_STRICT_CANDIDATE_FINITE_AND_OUTER_ARITHMETIC_CONDITIONAL_BOUND`.
The runner rejects discovery receipts. It binds the exact endpoints/profile
to the finite invoice and strict supplier output, checks all strict stage
log hashes, and requires114 admission controls,12 bit controls,21 controller
controls,6 buffer controls,6 geometry controls and8 independent owner controls.
The old unused SPEC metadata `mutations_rejected:15` is not the evidence:
the runner checks the actual21-element controller receipt.

The modern outer verifies63 strict inequalities and17 rejecting variants,
plus native endpoint rejection, the independent balance derivation,
fresh deterministic ledger regeneration, both sparse-union simulations,
the retained structured-boundary check, corrected gauge-free checks,
finite source-prime/underflow controls and19 supplier-independent evidence
replays. The main route uses explicit Strassen `tau=45/16`; the retained
structured-boundary alternative is not used for this exponent.

## Finite costs and inherited assumptions

The scalar/compiler invoice includes all76 private zero fields: physical
stock is `66304 + 428 + 8 + 2 + 76 = 66818`. Each invocation pays152
explicit CLEAR macros,304 real-component CLEAR operations and the112
warp routing reserve. Across666 invocations, the CLEAR charge is202464
real-component operations. The charged local adapter formula includes
both the warp events and all76 private fields; the global nonlocal reserve
adds `2*666*76` items.

The actual invoice passes all9 finite guards. Its maximum local primitive
bound is9222250044912, below2^48. Global prefix1442 fits the charged2048;
the physical row coefficient19545 is below20161. Router7993 bits,
literal35288 bits and required C0 exponent200012 fit their respective
30000,100000 and210000 limits.

Ordinary work is handled by those complete finite/compiler reserves. The
recursive moment uses the exact global rank profile. The retained PR559
native complex recurrence selects the unsurcharged moment only after the
conservative surcharged assembly also succeeds; the bit surcharge remains.
Both independent rational engines certify the native endpoint bracket
`[0.001697210569589237219727, 0.001697210569589237219728]`
and conservative bracket
`[0.001697210566704226823872, 0.001697210566704226823873]`.
Both reject the next endpoint. An additional global rank-one child fails
the proposed rate, demonstrating why complete recursive accounting matters.

The exact carried-cutoff bootstrap uses endpoint_digits24, grid_digits19,
margin_digits29 and12 steps; its47 supplier-assembly inequalities and
uncarried-cutoff rejection controls pass. The final capped-phase outer
then uses `b=C-10^-104`, `q=C-2*10^-104` and
`epsilon=1-(1025/1024)*10^-104`; both implementations verify the exact
fixed-grid identity `kappa=C-10^-46-10^-70`.

This remains conditional on the inherited all-size compiler,
common-label/mutable-source realization, whole-call hosting,
precision/tape, exact recovery, PR559 recurrence correction, PR589 bit
H1–H5, prime theorem, written gauge-free/locality lemmas and outer transfer.
Finite replay does not formally prove those theorems. The native endpoint,
physical accounting and finite inequalities are checked evidence within
those interfaces.

The genuine completed PR1297 receipt, all16 stage logs and its96-file
immutable source manifest are preserved in `../retained-pr1297/`.
The earlier failed PR2269 aggregate remains failed. This contribution uses
the original admitted PR1297 parent and a fresh complete candidate global
replay, rather than asserting success for that failed aggregate.

## Attribution

Tekalign (@tekuuu), with substantial OpenAI Codex assistance; Apache-2.0.
Credit Cinna Davis/PR2226 for anticipatory borrowing, Jeremy Kothe/PR2269
for the source words and native/global framework, and Sagar Thakrar/PR2339
for the predecessor low-alias construction. The physical stock accounting
follows the obligations identified by Dugongue/PR2309 and Sagar Thakrar/PR2315.
PR1956 (Josie Elliston) supplies the carried-cutoff repair. The final outer
continues PR1673 (Vlado Vojdanovski), PR1758 (IdeaOuter and contributors),
PR1786 (Chafik Boukhalfa, using Tim Trudgian's prime theorem),
PR2161/2180 and PR2168/2184 (dataisfire), and the corrected PR2374
implementation (Jeremy Kothe and contributors). LeverRank supplies the
independent union simulation. The source packages retain the full earlier
attribution and license notices.
