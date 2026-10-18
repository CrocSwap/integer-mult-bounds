# Prefix-bounded signed Horner circuits for the selected complex suppliers

**Finite circuit improvement / research note; no new κ.** Signed binary
coefficient synthesis saves another **3,090 real primitives in each JP8
orientation and 122 in each CK orientation**, beyond Sagar Thakrar's PR696
copy/unit lowering. All coefficient-work intermediate multiples stay between
zero and the original numerator, so the inherited scalar prefix bound suffices.
The extra saving is the contribution of this package; the larger saving over
the selected emitter includes PR696's credited work.

| Program | Selected emitter | Pinned PR696 | This circuit | Extra saving |
| --- | ---: | ---: | ---: | ---: |
| CK forward | 224,938 | 169,618 | 169,496 | 122 |
| CK backward | 224,986 | 169,634 | 169,512 | 122 |
| JP8 forward | 257,232 | 200,380 | 197,290 | 3,090 |
| JP8 backward | 257,280 | 200,396 | 197,306 | 3,090 |

Counts cover both real components: source copies/reads, doubling, signed
addition, halving, accumulation, clearing, and unchanged scale/center macros.
There are **no added registers, recursive children, frame changes, wrappers,
copies outside the listed circuit, or restoration operations**. The private
coefficient register is erased after each addition. Source accesses decrease
by 96 per CK real component and 1,722 per JP8 real component. The helper count,
scalar macro boundaries, native frame paths and paid child histograms stay
fixed. The selected assembly remains complex-bound at the same conditional
κ = `51110230636731/31250000000000000`; neither supplier moment changes.

## Reproduce

From the repository, using Python 3.11+ and only the standard library:

```sh
python3 -B research/complex-prefix-bounded-dyadic/verify.py
```

Expected:

```text
PASS_PREFIX_BOUNDED_DYADIC programs=4 columns=716+9 coefficients=686 extra_savings=122,122,3090,3090 controls=12
```

This is offline and makes no writes. `--json` prints the checked deterministic
certificate. The verifier binds the retained programs to the selected #626
SPEC, freshly executes all their scalar primitives on **716 native formal
input columns plus nine arbitrary private columns**, and checks the intended
forward/inverse-transpose shear with every dirty helper restored and private
column erased. Non-scalar events are retained and counted; their geometry,
phases, wrappers and analytic meaning are inherited, not independently replayed
by this command. Source pins are checked before any replay.

The [certificate](EXPECTED.json) contains every one of the **686** distinct
signed dyadic coefficients, its complete signed-digit word, multiplicity, cost
and work maximum. **282** coefficient types, occurring in **516** macros across
the four programs, improve over PR696. Exact three-input matrix checks cover
every coefficient with both lowerings. A separate forward Dijkstra search
agrees with the backward recurrence on all **8,256** `(target, bound)` pairs
with `1 <= target <= bound <= 128`.

## Circuit and bounded search class

Write a nonzero dyadic coefficient as `q = ±n / 2^d`, with `n > 0`. A signed
Horner word begins at integer 1, then appends digits in `{-1,0,+1}`. Each digit
first doubles the work register, then optionally adds or subtracts the unchanged
source. **Both** the doubled intermediate and the digit endpoint must lie in
`[1,B]`. The production circuit uses `B=n`.

Let `C_B(n)` be the minimum number of doubling/addition/subtraction primitives
in this class, excluding the initial source copy. The recurrence is:

```text
C_B(1) = 0
C_B(2a) = C_B(a) + 1
C_B(2a+1) = min(C_B(a) + 2,
                C_B(a+1) + 2 if 2a+2 <= B),       a >= 1.
```

Parity forces the last digit. Removing that digit produces exactly the displayed
predecessors; both are smaller than the target. Conversely, appending any
admitted last digit preserves the bound. Induction therefore proves the
recurrence optimal **within this signed-Horner class**. A nonempty cycle ending
at 1 has positive cost and cannot improve the base case. Binary Horner is an
admissible candidate, so this recurrence cannot cost more. Ties prefer fewer
subtractions and then lexicographic digit order; there is no random search.

For nonunit `q`, the complete per-real-component cost is
`3 + C_n(n) + d`: one copy, the digit word, `d` halvings, one signed accumulation
and one clear. Unit coefficients retain PR696's two-primitive circuit.
The selected original add costs `3 + floor(log2 n) + popcount(n) + d`;
PR696 saves the leading clear/add replacement (and a further unit operation).
The present additional saving is exactly the decrease in digit-word length.
No accounting relies on dropping the initial copy or final clear.

For example, numerator 31 has the seven-operation coefficient path
`1 → 2 → 4 → 8 → 16 → 15 → 30 → 31`, compared with eight binary operations.
The shorter unconstrained path through `32 → 31` is inadmissible. A negative
control has precisely this correct-endpoint overshoot and is rejected by the
prefix check, independently of its favorable cost.

This exhausts the recurrence for all selected coefficients, whose absolute
numerators are at most **67,108,862**. It does not assert shortest unrestricted
addition chains, multi-register circuits, target borrowing, interleaved halving
or globally optimal suppliers. The finite graph comparison is a check of the
implementation, not a formal proof of the full multiplication theorem.

## Prefix and substitution argument

At a macro entrance let the target and source rows be `T` and `S`. After the
initial copy every work row is exactly `c S`, with `0 <= c <= n`, including
halvings. The source remains `S`; the target stays `T` until its single signed
accumulation, then becomes `T + q S`. Hence an existing bound `N_T, N_S` still
gives work bound `n N_S` and target bound `N_T + |q| N_S`. These are exactly
the quantities charged by the retained local auditor and finite invoice.
Arbitrary initial private values are independent formal columns and are erased;
their entry states were already present in the reference program.

The proof uses coefficient bounds; the new intermediate rows need not literally
occur in the binary trace. The verifier checks the weighted row coefficients,
not just a clean-input evaluation or the endpoint. All primitives stay within
the macro's existing common frame. Each addition has the same three-register
boundary map `(T,S,W) -> (T+qS,S,0)`, so substitution preserves arbitrary
correlated inputs and composes across the fixed program. Both orientations
are nevertheless executed separately by an exact sparse rational interpreter.

Twelve adverse controls cover missing copy/halving/clearing, wrong signed digits,
cost inflation, a correct-endpoint prefix overshoot, source growth followed by
restoration, uncleared unit work, nondyadic and zero coefficients, and aliasing.
See [validation](VALIDATION.md) for the checks actually run.

## Provenance, overlap and limits

Exact base: **`66849e1475c930fd7732b1a0067ffee7e1e95f60`**. The selected source
is #626 at `660de893d27bb7abd1d5b01b1640207528a5c851`, on #622 at
`f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`, with the unchanged #543 bit source.
[SOURCES.json](SOURCES.json) pins all consumed repository artifacts and the
verbatim PR696 lowering at `5a3f983715027c4fd83f50bc9001d4b18463bed1`.
Compressed inputs are bound by their decompressed bytes, and program semantic
hashes are also checked against the selected SPEC. [NOTICE.md](NOTICE.md)
credits the construction and verification lineage.

OS assignment seed **23** selected the complex-supplier track and the third
of three recorded candidate tasks. It prioritized JP8 backward for the initial
screen; final coverage includes both providers and both orientations. There
was no pinned coordination issue, so [CLAIM.json](CLAIM.json) records the scope,
overlap checks, stopping rule and handoff. The time budget was 40 minutes,
with at least the final quarter reserved for verification and handoff.

Rohan Arun's archived [signed-digit negative result](../experiment-log/campaign-100/algebraic-word-construction.md#38-signed-digit-coefficients)
concerns rank-zero coefficient-3 rewrites and no paid-climb gain. This work
agrees with that conclusion and studies scalar primitive cost for the later
selected coefficients. PR696 is an explicit predecessor and comparison;
PR681 changes a factory map's implementation, PR687 changes read order, and
PR698 studies fixed-boundary frame assignments. None supplies this bounded
signed-Horner construction. Their open PR titles are not accepted-frontier
claims.

**Concurrent overlap discovered during final verification:** Sagar Thakrar's
[PR723](https://github.com/CrocSwap/integer-mult-bounds/pull/723), at
`d3bc41b87fc7d23f50d064a0f06f1a89e3ab02a7`, independently uses signed digits for
JP8 and reports 3,276 saved primitives per orientation. It permits numerator
overshoot by one and increases the exact forward prefix envelope by
`34078712/34078711`. This contribution retains the old envelope **at every
macro**. Its recoding component saves 186 fewer primitives per JP8 orientation
(the PR696 copy/unit saving is accounted separately), also covers CK,
and gives a proved recurrence with an independent finite graph comparison for
the restricted class. Signed recoding itself is therefore concurrent work,
not an exclusive discovery here. Its PR description and file inventory were
inspected; its implementation and receipts are not independently verified by
this package.

[PR722](https://github.com/CrocSwap/integer-mult-bounds/pull/722), by @ellipsi2 at
`a0766ab0fab379e1997fadc3ca157578d57986c1`, instead shares preparation across JP8
cleanup macros and changes the private-clear boundary. This package retains
per-macro clearing. No composition with #722 or #723 is claimed. The final
overlap snapshot is recorded in [OVERLAP.json](OVERLAP.json).

This package does **not** replace the selected emitter or issue a new global
invoice/admission certificate. The uniform compiler, common-label/mutable-basis
realization, hosting, precision/tape/recovery, analytic transfer and bit-supplier
assumptions remain inherited. No practical runtime speedup, unconditional
multiplication result, Lean proof or remote CI result is claimed. All existing
repository files, `upstream/`, and the selected frontier remain unchanged.

Prepared by **Chris Pagolu (@AllStars101-sudo)** with substantial **OpenAI Codex
assistance** in research, implementation, verification and writing, under the
repository's Apache-2.0 license.
