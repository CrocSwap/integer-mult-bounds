# Every nonzero ambient quotient loses the retained local rank advantage

**Scoped geometric proof and finite certificate; no new kappa.** Selecting only
the complex ports that survive a quotient cannot preserve the source's local
unpaid-rank advantage while retaining its eight center transports. This covers
every nonzero binary kernel, of every dimension, rather than just kernel 153 or
the 32 directions passing the earlier logical replay. It does not exclude
changed center words, nonquotient constructions, or all possible moment gains.

The question arose while trying to repair DaysSky's #4629/#4633 quotient by
dropping incompatible ports and charging only surviving output contracts.
The preceding endpoint audits establish that keeping the old full-port invoice
is invalid. This package asks whether selecting a smaller valid port set saves
the quotient's local rank budget. The answer is no under the retained recipe.

## Exact result

Let V=F2^9. The source has 112 hyperplanes H_p complementary to its 112
entrance lines P_p, and eight center hyperplanes C_i. The verifier extracts
their unique nonzero annihilators directly from the pinned canonical word.
Their disjoint union S is exactly the 120 vectors of Hamming weight 3 or 7.

For any kernel K, a port retains a nonzero complementary entrance line after
quotienting exactly when K is contained in H_p. Write v(K) for the number of
such ports, and charge all eight retained center transports by their actual
image dimensions:

    c(K) = sum_i dim(image(C_i)).

Then

    K = 0:             v(K) - c(K) = 112 - 64 = 48;
    every nonzero K:   v(K) - c(K) <= 0.

For one-dimensional kernels the complete balance distribution is 255 cases at
0, 255 at -8, and one at -64. Kernel 153 has 56 compatible ports, center charge
64 and balance -8. The seven directions with 64 compatible ports all retain
center charge 64. Re-padding unrelated helpers cannot alter this geometry.
Choosing fewer compatible ports can only lower the displayed balance.

## Proof for every kernel dimension

Let L=K-perp and r=dim L. A hyperplane with nonzero normal n contains K exactly
when n lies in L. Its image dimension is r-1 in that case and r otherwise.
Consequently

    v(K)-c(K) = |S intersect L| - 8r.

It remains to bound |S intersect L| for r<=8.

* For r=8 the exact 511-hyperplane census gives 255 intersections of size 64,
  255 of size 56 and one empty intersection. Thus the maximum is 8r.
* For r=7, L lies in exactly three hyperplanes. Each point of S inside L is
  counted three times, and every point outside L once. Therefore
  120+2|S intersect L| <= 3*64, giving |S intersect L|<=36<56.
* For 1<=r<=6, S consists of odd-weight vectors. The parity functional on L
  is either zero, giving an empty intersection, or takes value one on exactly
  2^(r-1) vectors. In this range 2^(r-1)<=8r.
* For r=0 both counts vanish.

This is a dimension-uniform proof, not an assertion that enumerating line
kernels enumerates every higher-dimensional subspace. The coarse bounds for
r<=7 are not claimed sharp. [RESULT.json](RESULT.json) gives them explicitly.

## Meaning for the controller

The incumbent accounting lever is the number of unpaid central port directions
minus the center rank spend. Its value is 48 before quotienting. The repaired
selective-port version has a nonpositive value even before charging dropped-port
conversion, native normalizers, changed warps, boundary work and ordinary/outer
admission. Those costs are not assumed solved by this certificate.

This rank statement is **not** a theorem that every concave target/paid moment
fails: a rank-mass comparison by itself is insufficient for that conclusion.
No full quotient program, scalar-field lift, replacement controller, new
ordinary supplier, or improved exponent is claimed. A changed circuit would
need its complete moment and physical contract checked separately. The result
identifies the center recipe as a premise that must change to recover a
positive local rank advantage, rather than declaring a universal barrier.

Concurrent #4654 constructs an exact mixed type-A/type-B quotient interface.
Its type-B ports are not the retained complementary ports counted here. A
controller that consumes those changed interfaces escapes this selective-port
scope and remains a constructive next route; this result does not refute it.

## Reproduce

From the repository root, standard-library CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/selective-quotient-port-budget
python3.12 -I -O -B research/selective-quotient-port-budget/verify.py
```

The independent verifier authenticates the input, checks all 112 source splits,
extracts the 120 normals, computes all 511 line cases and verifies the numerical
bounds used in the written proof. Four geometry mutations are rejected; a
simultaneous change of frame bases preserves the complete result. It imports no
predecessor evaluator. Native circuit replay, phases, precision, compiler,
selected cold replay and human/formal review are outside its coverage.

The optional current baseline command fails at this base with `KeyError:
'bit_lower'` because its expected certificate schema differs from the selected
record. It is not reported as a successful replay; this package uses the actual
selected record only as provenance and does not modify that unrelated helper.
The selected conditional saving is 0.00302015 at base
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`.

## Open next questions

Can a changed center construction preserve valid native port maps while making
their count exceed its paid rank spend? First specify its exact center operator,
arbitrary-input restoration and a complete local invoice. The obstruction above
does not apply when that recipe changes. A larger kernel scan with the same
eight transports cannot reopen the rank question. See [TASK.json](TASK.json).

## Credit

Prepared by Cinna Davis with substantial OpenAI Codex assistance; Apache-2.0.
Credit DaysSky for the quotient experiments (#4596/#4629/#4633), Nick Petalas
for the kernel census (#4627), pinterbanget and Rohan Arun for endpoint checks,
and the preceding #4636 and local PR4633 repair audits. The source is zxv's
native construction with the retained E8/scalar/Clifford authors, Cinna Davis's
#4440/#4441/#4447/#4470 controller lineage, and Jacob Alan Sussman's mixed-target
recursion. No frozen source or selected-frontier file is changed.
