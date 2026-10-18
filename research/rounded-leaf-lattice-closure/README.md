# An admitted rounded leaf need not preserve its ideal source lattice

**Exact counterexample to a proposed inference, not a defect in PR628 or
PR1848. No new kappa.** An ideal affine-lattice calculation does not certify
that a later mixed-precision inverse pair receives a source in that lattice.
The actual rounded implementation must be included in the reachability proof.

This answers one concrete part of [PR1848's open closure question](https://github.com/CrocSwap/integer-mult-bounds/pull/1848),
not its conditional theorem. That theorem explicitly excludes internally
rounded nonlinear source updates. The selected
[review, final paragraph](../../docs/research/community-batch1099-review.md)
retains precision and exact-recovery obligations; this package supplies a local
adversarial instance relevant to that boundary, not selected-supplier admission.

## Exact proposition being falsified

Use componentwise nearest rounding with ties toward positive infinity:

```
Q_b(t) = 2^-b floor(2^b t + 1/2).
```

The false shortcut is: for every admitted PR628 rounded leaf S_b with ideal
linear shear S and every affine lattice Lambda, `S(Lambda) subset Lambda`
implies `S_b(Lambda) subset Lambda`. Its inputs include the actual execution
precision, phases, immutable coefficients and fixed-grid states. Exact source
restoration and a numerical approximation guarantee do not supply the missing
image inclusion.

Here is one counterexample, with all numbers rational and exactly represented.
Use a length-one *outside* factor `b=1/4`, scale 1, phase
`phi=(3/5,4/5)`, beta `1/2`, execution precision 4 and direction `+1`.
The ideal complex increment is

```
F(x) = x / (phi - 4).
```

Put `a=-17+4i=5(phi-4)`. On the state lattice

```
Lambda = {(x,y): x=a k, y=5 j; k,j in Z},
```

the ideal shear `(x,y) -> (x,y+F(x))` maps `(a k,5 j)` to
`(a k,5(j+k))`, and therefore preserves Lambda for **all** integers k,j.
The implemented leaf, however, sends the member `x=a,y=0` to

```
x unchanged, y = 39/8 - i/16,         rather than y = 5.
```

This is an admitted generic leaf input, not an asserted occurrence in the
selected multiplier or a particular prepared prime-power kernel. It has unit
phase, coefficient norm `1/4 <= 1-beta`, fixed-grid source/target, no aliasing,
`2^-4 <= beta^2/2`, and closure denominator squared norm `205/256 >= (beta/2)^2`.
The phase array is immutable and distinct from the mutable arrays. Accepting
the nonintegral output is correct: the primitive promises approximation and
exact reversible signed updates, not lattice preservation.

## Independent derivation of the actual leaf

The pinned `dirty.py:lift` rounds its coefficient power before division. For
this one-entry case its stored quantities are exactly:

| Quantity | Value |
|---|---|
| rounded power `P=Q_4(phi/4)` | `1/8 + 3i/16` |
| denominator `1-P` | `7/8 - 3i/16` |
| unrounded seed `x/(1-P)` | `-800/41 + 16i/41` |
| rounded seed | `-39/2 + 3i/8` |
| rounded `P*seed` | `-5/2 - 29i/8` |
| `x + rounded(P*seed)` | `-39/2 + 3i/8` |
| final `Q_4(-value/4)` | **`39/8 - i/16`** |

The last imaginary value before rounding is `-3/32`, a negative halfway case;
ties upward give `-1/16`. One rounding of the ideal answer instead gives 5,
so replacing this internally rounded routine by `Q_4(F(x))` would miss the
counterexample. The verifier executes the unchanged actual leaf and compares
it with a separately written scalar formula and the exact ideal division.

## Downstream precision consequence and precise repair

Let the resulting y be held **unchanged** while a new exact-addition pair acts
on arbitrary target dirt t:

```
t += Q_0(Re y)
t -= Q_4(Re y)
```

Every ideal-lattice output has real part in `5 Z`, so the pair cancels there.
At the actual output above it leaves `t + 1/8`, since the increments are 5 and
39/8. This failure is not caused by changing the source between inverse mates.
The original leaf's own inverse, at the same execution precision and phase,
restores y exactly. Likewise both downstream pairs `(0,0)` and `(4,4)` cancel.

A sufficient repair is to certify `S_b(Lambda) subset Lambda`, but that is
stronger than necessary. The exact required downstream premise is inclusion
in `E={y:Q_w(Ay)=Q_v(Ay)}`, with the **actual** source unchanged throughout the
pair. For every dimension, real linear map A and integers `0<=w<v`, the scalar
safe set is the union, over `n in 2^-w Z`, of the half-open cells

```
[n - 2^(-v-1), n + 2^(-v-1)).
```

Indeed the fine rounded value must equal the coarse grid value n; its fine
rounding cell is contained in n's coarse cell. Apply this statement separately
to each component of Ay. It gives a direct checkable proof repair: if an ideal
source y has `Ay in (2^-w Z)^r` and **every reachable actual error** e satisfies

```
-2^(-v-1) <= (A e)_i < 2^(-v-1)   for all output coordinates i,
```

then every such actual source y+e admits the mixed-precision pair. A symmetric
bound must be strictly less than the half-width; equality on the positive
boundary is unsafe. Bounds must cover the full reachable source domain,
including dirt, rather than a finite sample. For noncentral ideal offsets,
compare the error enclosure against the translated cell endpoints instead.

For example, the same actual leaf at execution precision 8 returns
`639/128 - i/128`: it still escapes Lambda, but its real error `-1/128` is
inside the downstream `(0,4)` cell `[-1/32,1/32)`, so that pair cancels.
This is a pointwise control, **not** a universal sufficient execution-precision
bound or an implementation-cost saving.

## Reproduction and bounded evidence

From the repository root, Python 3.12 and standard library only:

```sh
python3.12 -I -O -B research/rounded-leaf-lattice-closure/verify.py --witness-only
python3.12 scripts/research_package.py --package research/rounded-leaf-lattice-closure
```

The full registered replay checks all 8,064 actual leaf invocations and their
literal inverses for eight unit phases, execution precisions 3 through 12 plus
16 and 32, source multipliers -3 through 3, both directions, both signs and
three fixed-grid dirty targets. The 4,032 Gaussian-unit-phase cases are exact
ideal-output positive controls. It also checks 3,600 sharp-cell points, source
pin corruption, negative ties, same-grid downstream pairs, the unsafe positive
cell endpoint, higher precision without lattice closure, and actual rejection
of underprecision, off-grid input, nonunit phase and aliasing. No floating point
is used. The census is supporting evidence, not an all-size implementation
proof. The all-integer ideal closure and safe-cell claims have the written
proofs above; one exact actual input suffices to falsify the shortcut.

## Sources, overlap and scope

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`;
[SOURCES.json](SOURCES.json) pins every imported file by Git blob and SHA256.
The actual PR628 head is `0768f97d06c623b8211e651543c66135796b62bf`, retained
verbatim through `dirty-prefix-precision`. No frozen file, selected record,
shared index, compiler or supplier is changed.

Closest overlaps, explicitly credited:

- Integrated `mixed-precision-inverse-boundary`: unrestricted product-grid
  criterion and a real same-source/mixed-precision PR628 counterexample. Here
  the producer precision is fixed; the new issue is ideal versus **actual
  source-lattice closure before a later pair**.
- [PR1848](https://github.com/CrocSwap/integer-mult-bounds/pull/1848), head
  `d975e19e7e931fc2b45792a4f7140ac13759a7da`: unrestricted affine-lattice
  cancellation theorem, whose explicit open question motivates this example.
- [PR1853](https://github.com/CrocSwap/integer-mult-bounds/pull/1853), head
  `43caf3d864f4328a436bda40f849d96e2bf209cb`: bounded scalar floor-sum criterion.
  Neither theorem is reimplemented or claimed new here.

The final cached overlap search covered 543 open PRs including drafts, fetched
2026-10-14T13:23:53Z, and 529 discussion records, fetched 13:25:07Z, both with
complete pagination. The offline search may miss newer records. Targeted live
queries of PR1848 and PR1853 reconfirmed the heads above, both still open with
no comments. Exact affine, rounded-closure and ideal-lattice searches were read
alongside the predecessor content. The helper excludes code diffs and arbitrary
nested files; closed work is represented through local notes and the ledger.
These are provisional coverage limits, not a novelty certificate.
Parent coordination is [discussion 1884](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884).

## Open next questions

Can a concrete caller propagate a useful actual source-error enclosure into
every later mixed-precision equality cell? Start from its exact rounded update
maps, retain dirt and phase-access hypotheses, and compare projected error
endpoints with the half-open cell. A selected reachable-domain proof and the
full cost of the precision policy remain missing. This example neither finds
such a policy nor shows that any selected caller violates its present contract.
The structured question is in [TASK.json](TASK.json).

Credit Chafik Boukhalfa/chafreaky for PR628, Gareth Davidson/bitplane for the
retained precision analysis, and woklerx for the mixed-grid, affine-lattice and
bounded-domain audits. The retained PR628 notice credits Ali Romman's PR621
and its analytic sources. Prepared for adamgall with substantial **OpenAI
Codex** assistance in the proof, implementation and prose; Apache-2.0.
No literature-priority claim, independent human review, physical tape compiler,
full selected cold replay, complete multiplication theorem or new kappa.
