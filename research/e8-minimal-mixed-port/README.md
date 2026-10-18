# The minimal E8 mixed-port extension is saturated

**Scoped negative result.** Delete at most 14 of the 120 E8 root lines and
retain their inherited nine-dimensional binary labels. If a compatible
non-root port can be added, exactly 14 lines were deleted. Up to Weyl symmetry,
they are the integer root lines involving coordinate eight. There is exactly
one compatible non-root port type. After adding it, no further nonzero port
of any direction can be added with these labels.

The resulting 107-port unit has star copy cost **72**, not the root-only
puncture's cost 64. Every nonzero reader now spans all eight physical
dimensions. Its ratio `72/107` is worse than both the full-root unit's `72/120`
and the known punctured-star benchmark `63/111`.

This adds an equality classification and simultaneous-port obstruction to
Chi Zhao's [#631](https://github.com/CrocSwap/integer-mult-bounds/pull/631).
GamingPuzzled's #620 already computed the coordinate-axis example's roughly
0.67 ratio. That numerical example is predecessor evidence, not a new result
claimed here. The new statement covers every minimum-deletion mixed extension
in the stated model, including arbitrarily many proposed added ports.

No new supplier word, exponent or kappa is claimed.

## Model and exact scope

Let `L` contain the 120 E8 root-line representatives in doubled standard
coordinates, of squared norm eight. Integer lines are `2e_i +/- 2e_j`;
the other 64 representatives have first coordinate one and an even number
of minus signs. Put `G_st = L_s dot L_t / 4` and `B = (J + G) mod 2`.
The rank-nine binary form gives inherited labels `u_t` with
`u_s dot u_t = B_st`.

A new port consists of a **nonzero rational vector** `n` in eight-dimensional
Euclidean space and a label `z` in the **same nine-dimensional binary space**.
Compatibility requires odd self-pairing `z dot z = 1`, and, for distinct ports,

    physical inner product nonzero => binary label pairing zero.

Thus all surviving roots in the reader `R(z) = {t : z dot u_t = 1}` must lie
in `n`'s orthogonal hyperplane. New ports must satisfy the same condition
against each other. "Non-root" means that `n` is not proportional to any of
the original E8 root lines. Rational rescaling of a nonzero port is immaterial.

The theorem fixes surviving root labels. It permits no added binary label
dimensions, zero physical vectors, relabelling of old ports, or different
ambient form. It makes no assertion for more than 14 punctures or for other
decoder families.

## Why every equality case is D7

Use the simple E8 system explicitly listed in `verify.py`. Move an arbitrary
normal into its closed fundamental Weyl chamber. A positive root is a
nonnegative integral combination of simple roots, so its pairing with this
normal vanishes exactly when it uses only vanishing simple roots. Its root
section therefore lies in a standard parabolic section.

The eight maximal sections have the following reader-deletion minima. Each
minimum is over all 511 nonzero label functionals, so allowing an even label
in this lower bound cannot invalidate it for the required odd labels.

| Root lines in section | 63 | 42 | 37 | 28 | 23 | 22 | 16 | 14 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Minimum deletions | 1 | 14 | 27 | 28 | 33 | 35 | 40 | 43 |

These minima reproduce #631's table independently. Only the 63-line E7
section has a root normal. If a chamber normal has just that omitted simple
root with positive pairing, it is a root normal and is excluded. Otherwise
choose a positive-pairing simple root whose omission gives one of the other
seven maximal sections. The actual root section is contained in that section.
At most 14 punctures therefore forces the 42-line D7 section and its unique
minimizing reader.

That reader consists of all 56 integer root lines. The 14 outside D7 are
exactly `2e_i +/- 2e_8`, for `i=1,...,7`, and all must be deleted. The other
42 span the D7 hyperplane. Since the actual normal annihilates these 42 roots,
it is proportional to `e_8`. This last rank argument rules out a proper
subsection of D7 attaining equality. It also proves that the puncture and
reader are forced, rather than merely exhibiting one 14-deletion example.

The checker verifies integral common-sign simple coordinates, all eight
simple-reflection permutations, and preservation of the binary Gram form.
Weyl permutations consequently preserve its row space, induced nondegenerate
label pairing and odd self-pairing. Transporting the enumeration through these
permutations preserves every compatibility and rank statement used here.
The chamber reduction is a written mathematical argument; enumerating eight
sections alone is not advertised as a formal proof of it.

## All compatible ports at equality

For that fixed puncture, the exact rational ranks of all 511 reader spans are

    15 readers of rank 7; 496 readers of rank 8.

All 15 deficient readers have odd self-pairing. Fourteen are precisely the
labels of the deleted roots, with those roots as their unique normal lines.
The remaining reader, denoted `z`, selects all integer roots and has unique
normal line `e_8`. No reader has smaller rank. Therefore the only possible
non-root port is `(e_8, z)`, up to nonzero rational rescaling.

Two copies of this type cannot coexist. Their geometric inner product is
nonzero, but their binary pairing is `z dot z = 1`.

There is a stronger saturation certificate. Each of the 14 root-normal
readers pairs to one with `z`, and `e_8` lies outside its hyperplane. The
reader `z` itself also reads the added port, because it is odd, and `e_8`
lies outside D7. Adding the port raises all 15 ranks from seven to eight.
The other 496 ranks were already eight. A further nonzero port would need
to annihilate an eight-dimensional reader span, which is impossible.

The live label rank remains nine. In the star label-decoder model, the
functionals must span the dual label space; a minimum-weight basis gives
the optimum, since extra nonnegative-cost totals cannot improve on a contained
basis. Before augmentation the 15 rank-seven functionals span dimension eight,
giving `8*7 + 8 = 64`. Afterwards all 511 nonzero functionals cost eight,
so the exact optimum is `9*8 = 72`.

This already fails the optimistic copy-cost comparison. No circuit search
was launched. Helper preparation, source access, frame changes, restoration,
recursive calls, hosting and assembly have not been implemented or priced.
The ratio result excludes this proposed improvement to copied information;
it does not exclude a separate helper-saving tradeoff at a worse copy ratio.

## Reproduce and verification boundary

From the repository root, with Python 3.9 or later and no third-party packages:

```sh
python3 -B research/e8-minimal-mixed-port/verify.py
```

Expected output:

```text
PASS: 8 maximal flats; 511 readers before and after augmentation; one non-root candidate; 5 negative-control categories
star costs: 64 on 106 ports; 72 on 107 ports
```

Every run regenerates the census and compares its full deterministic JSON
encoding with `results.json`. `--print-receipt` also prints that encoding.
All validations remain active under `python3 -O`; the checker uses explicit
exceptions, not removable assertions.

The independent implementation works directly in a basis of rows of `B`,
rather than constructing #620's orthonormal label factor. If the chosen root
indices are `I` and a functional has basis coefficients `a`, its support is
`a * B[I,:]`. Its pairing with `b` is `a * B[I,I] * b^T`. This avoids assuming
that ordinary bitwise dot products are valid in a nonorthonormal basis.
Rational spans use integer elimination with content reduction; normal
vectors and simple-root coordinates use exact fractions.

The five negative-control categories reject two identical non-root ports,
an even added label, restoration of each of the 14 deleted roots while
retaining the new port, a rank-eight input to the normal calculation, and a
malformed simple-root system. The domain is exhaustive for eight maximal
sections and all 511 readers before and after this forced augmentation.
There is no annealing, heuristic stopping condition, or claim based on a failed
search. The finite arithmetic supports the stated proof and does not prove
the full multiplication theorem.

Validation on 2026-10-13 passed with Python 3.14.8 and Python 3.11.15, the
latter with `-O`. A separate AI-assisted check generated all 240 signed roots,
quotiented signs in a different order, chose a different binary basis, and
computed reader ranks over GF(3). It confirmed all 511 augmented spans have
rank eight. For the 15 deficient original readers, exact integer annihilators
give rank-at-most-seven certificates and the modular ranks give the matching
lower bounds. Their binary span has dimension eight. The selected-record
binding check, source hashes and staged whitespace check also passed.
The expensive repository-wide supplier replays were not repeated because
no supplier, assembly, generator or existing file changes.

## Sprint record, source pins and credit

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The selected conditional
result there is #626 on #622/#623 with #543,
`kappa = 51110230636731/31250000000000000`. It is unchanged. Its all-size,
physical realization, restoration, precision and analytic obligations remain.

The OS-random assignment seed was **40**, selecting structural decoder
research. It also selects root row 40 as the start of the cyclic row ordering
for the independent binary Gram basis. Three candidates were considered:
deeper star punctures beyond 35, pairing-rank decoders on another nine-line
puncture, and simultaneous non-root additions at the sharp 14-puncture
threshold. The last addresses an explicit omission from #631's scope.

The local claim was recorded at 04:29 UTC on 2026-10-13 with an expected
finish of 05:01 UTC. There was no pinned sprint issue; the only open issue
was #650. Related #620, #631 and #669 were checked before claiming.
#669 treats paired hypercubes, not this E8 geometry. See `SOURCES.json` for
immutable predecessor pins and content hashes. No external package or PR
checkout is needed to run the checker.

The final overlap scan at 04:38 UTC covered 528 open PRs through #709.
#620 and #631 retained the recorded heads. New #703 concerns ten quaternionic
lines and asymmetric copy accounting; it does not cover this real E8
minimum-puncture equality case.

Credit to Joel Pulikkan / GamingPuzzled for #620's mixed-port model and
coordinate-axis experiment; Chi Zhao for #631's exact threshold and chamber
argument; DreamingOfClouds and artuskg for the format-limit work; eumemic
for the E8 suppliers; and the upstream OpenAI #109 framework and cumulative
community work. The selected frontier also retains the construction and
allocation credit recorded in its maintainer review.

Prepared by **Sagar Thakrar / @thakrarsagar**, with substantial **OpenAI Codex
assistance** in research, implementation, proof review and documentation.
Apache-2.0, following the repository license. No archived source was changed.
