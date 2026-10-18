# Native residual and private endpoint for one V45 helper

PR2979's helper 249 has a phase-exact rank-seven native residual. Its six
chronological climbs, with ranks `1,1,1,1,2,1`, each satisfy their native
chart identity on all 512 columns. A separate reverse-covector checker gives
exact endpoint rows `e249` and `e953` for the restored helper and its private
buffer, in both final providers and both orientations.

This takes the native-residual/private-endpoint handoff from [PR2993][2993].
It adds one bounded native and algebraic check to that frame audit and
[PR2987's packing audit][2987]. It does not independently admit PR2979's
complete physical supplier or its claimed kappa. The selected result is unchanged.

## Native identity and literal path

The source is [PR2979][2979], exact head
`be191346391661f4d35fc0d1508d0a6029572576`. In both final words, helper 249
starts at ZERO, is not a warp lender, and ends at the literal ordered basis

```text
W = [256,128,64,35,16,11,5].
```

Its frame changes occur at zero-based gates `A[2036]`, `A[2046]`, `B[459]`,
`B[461]`, `B[470]` and `restore[124]`. All other gates touching it preserve
its current frame. The checker reads every such gate and checks nestedness
and containment in W. It does not substitute an arbitrary basis of the same
span, since the canonical native operator depends on that basis.

Write `T_U` for the retained canonical frame operator. For each actual climb
`A -> B`, the retained native compiler generates a serialized recipe
`L F_r R`. The separately implemented exact kernel checks

```text
L F_r R = T_B T_A^-1,       r = dim(B) - dim(A).
```

There are six distinct climb recipes and one additional residual recipe.
Every identity is checked on all 512 columns, including global phase, and
again after inverse transpose. The checker also verifies the wrapped residual

```text
L^-1 T_W R^-1 = F7.
```

Thus the residual has width seven in this local native model, with identity
on the two unused address axes. `RESULT.json` stores every generated recipe.
The residual's right monomial has phase 2. Phase and input-character mutations
are rejected for all seven recipes.

All these native operators are unitary. Inverse transpose is therefore entrywise
complex conjugation, implemented without reversing the chronological gate list.
The test suite checks that this differs from the adjoint on this actual W.
This distinction is needed for the inverse-transpose supplier orientation.

The compiler and independent kernel are reused and credited, not presented as
new implementations. Their exact source bytes are authenticated before either
executes. The kernel compares exact packed Gaussian integer columns with its
proved radix bound; it uses no floating-point tolerance. Normal replay writes
nothing and needs no Git checkout or network connection.

## Arbitrary-input endpoint check

`endpoints.py` is a new reverse-covector implementation. It imports no producer
or predecessor replay code. It reconstructs all 17,575 chronological gates from
initial corrections, wrappers, the complete A/cut/B/restore word, the positioned
warps and the supplied cleanup. The word has 632 live original inputs and 91
private names. Every original source, target and dirty helper remains an
independent formal input.

An endpoint covector is pulled through the reversed gate list. For forward
`target += c * source`, add `c` times the target coefficient to the source
coefficient. A warp right-multiplies its coefficient's operator word. For an
initial correction with operator word `K1 ... Kk`, right-multiply in that order.
Only adjacent inverse symbols cancel; no commutation relation is assumed.

For inverse-transpose execution, a shear swaps source and target and negates
its scalar. A scale is inverted. Use distinct formal symbols `D_i = K_i^-T`
for warps. A correction's transpose contributes the inverse word
`D_k^-1 ... D_1^-1` with a negated scalar. Small noncommuting examples test
these rules against literal expected coefficients.

For each provider and orientation, the two complete output covectors are
exactly `e249` and `e953` over all 723 formal input names. In particular,
helper 249 returns its own normalized dirty input, and private 953 returns
zero when its private entrance is zero. This checks two output rows, not the
complete scalar map. It does not say that the helper's physical array is
unchanged: its forward chart residual is `T_W` and its dual residual is
`T_W^-T`.

A meaningful failure control removes only cleanup gate 72,
`62 += private953`. With all private entrances zero, the altered word still
has zero original-input response in private953 in the forward orientation.
In the inverse-transpose orientation its private953 row instead has coefficient
`-1/2` on original input 11. Setting only that input to an address basis vector
therefore gives a nonzero normalized private output. The valid words contain
the gate and pass both orientations. The complete corrupted rows are retained
in `RESULT.json`; this is a verifier control, not a defect in PR2979.

## Reproduce and scope

From the repository root, Python 3.12 or later, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/rank7-v45-native-endpoint
python3.14 -I -O -Werror -B research/rank7-v45-native-endpoint/verify.py
python3.14 -I -O -Werror -B research/rank7-v45-native-endpoint/test_verify.py
```

`verify.py --emit` reconstructs the complete deterministic receipt. The hook
runs the verifier and eight behavioral test groups. These include actual CLI
replay, noncommuting words, reciprocal scales, the omitted cleanup, changed
frames, transpose-versus-adjoint semantics, a Git-free export, corrupted-source
rejection before execution, duplicate JSON keys and Boolean/frame confusion.
A separate internal read-only implementation corroborated the two endpoint
rows and the rank-seven residual. Evidence is locally checked, without
independent human or formal-kernel review. Hosted CI is separate.

The native path/residual and formal endpoint results are separate finite
statements. Joining them into a literal physical execution requires all other
used native transitions, warp recipes, wrappers and emitted events to obey their
common-chart contracts. This package does not bind those full event streams,
check every output row, rederive owner/storage costs, certify rounding or tape,
replay the outer release, or discharge inherited all-size/compiler hypotheses.
The search-time integer tariff in PR2979 is not repriced or admitted here.
Neither a new supplier nor a new exponent follows from these checks.

## Open next questions

Bind the exact emitted events for helper249/private953 to the checked recipe
inventory and the matched inverse operations, then join the result to PR2987's
owner evidence and the actual physical storage/precision bill. This matters
because separate native and formal identities do not certify the complete
caller. The first step is one independently reconstructed event inventory,
including all dependencies that reach the private endpoint. Full native/warp
bindings, physical storage and precision remain blockers. Do not launch another
lowering census from this local positive result. Structured scope, sources and
the handoff are in `TASK.json` and `SOURCES.json`.

## Credit and engineering constraints

Nick Petalas. Apache-2.0. Substantial automated assistance in analysis,
implementation, internal review and writing. No independent human review is claimed.

Credit Marius-Paul Dumitrean/PR2979/PR2942 for the words and joint mechanism;
Jeremy Kothe for native/frame/cleanup and rewrite lineage; Mason Hale/PR2917
and Jeremy Diviney/PR2908 for paired extraction; icekylinx for the native
Clifford compiler and prior free-algebra auditor; Sagar Thakrar for the
independent phase-exact kernel; and Ross Richardson/PR2960/PR2974/PR2987 for
algebra, invoice and packing audits. PR2993 supplies the explicit native handoff.
Retain Yiyang Lu, Dugongue, Tekalign, DreamingOfClouds, Cinna Davis and the
geometry, owner and compiler lineage credited in the source packages.
No predecessor theorem or compiler is claimed as new here.

Build the Lever changed the deliverable to a rerunnable covector/native checker.
Prove It Works required serialized-recipe decoding and the actual dirty-input
cleanup control. Test Behavior, Not Implementation required a forward-passing,
dual-failing control alongside exact positive endpoint rows. Unslop shaped prose.

Power of Ten inspection covers the three new Python files. Functions remain
under 60 physical lines. Loops are bounded by 20,000 gates, 1,408 role names,
4,096 terms per role, 16,384 total covector terms, 64 symbols per word, nine
binary generators or 512 columns. Four authenticated inputs are at most 2 MB
each; decoded words are at most 8 MB. Tests use 30-second subprocess deadlines.
Checks use explicit exceptions and survive optimized Python.

Rule 3 deviation: Python allocates managed objects. The fixed domains and term
caps bound live state; a resident service would need fixed-capacity storage.
Rules 8/9 deviation: three named modules are loaded from source, two from
SHA256-authenticated retained inputs and the package's own covector module.
No bytecode is loaded for them. The native compiler is an unmodified research
input; its candidate output is independently decoded and checked. Source
corruption tests cover that execution boundary. Duplicate-key parsing uses one
fixed callback. A broader or untrusted-input service would need a static API
and a new capacity audit. Warning-as-error replay, source compilation and Ruff
cover the touched code; no shared configuration or frozen input changes.

[2979]: https://github.com/CrocSwap/integer-mult-bounds/pull/2979
[2987]: https://github.com/CrocSwap/integer-mult-bounds/pull/2987
[2993]: https://github.com/CrocSwap/integer-mult-bounds/pull/2993
