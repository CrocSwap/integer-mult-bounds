# Restored target basis and its complete bound

Fix the selected PR589 word and the exact sources in SOURCES.json. Let K be
the 111×439 binary matrix of the old D helper reads, with target rows 0..110
and helper columns 0..438. Physical targets are 111..221 and helpers 222..660.
The 111 source registers are untouched throughout D.

## F2 prefix substitution

For d≠s, let T(d,s) be the elementary target transvection adding coordinate s
to d. It is its own inverse over F2. For a sequence T₁,…,Tₘ in chronological
order, let E=Tₘ⋯T₁ and compute R=EK by the identical sequence of row XORs.
The emitted prefix performs:

1. T₁,…,Tₘ on the actual arbitrary target vector y;
2. all helper-to-target additions specified by R;
3. Tₘ,…,T₁ on the actual targets.

Its output is `E⁻¹(Ey+EKs)=y+Ks`, and every source and helper stays unchanged.
The entrance cannot be omitted just because helpers are the quantities being
compensated: without it, the output would be `E⁻¹y+Ks`. The explicit control
in verify.py passes all helper columns after this omission but fails target
columns. The inverse order is necessary because successive shears overlap.

Every emitted gate is at frame zero, and reads/writes only targets and helpers
which start there. No MOVE, COPY, private register or recursive child is added.
The state and frames at the entrance to A equal the original state and frames.
Every non-D field is verified identical, so the unchanged remainder receives
identical inputs. This proves prefix substitution into the original interface
under its inherited common-label realization assumptions.

Literal H2 originally allowed only helper donors in D. Target transvections
therefore fail H2, and direct extraction of K from D's helper lists is invalid.
The semantic replacement is the complete frame-zero boundary map above, checked
independently on all 661 input columns. The old predicates remain unchanged
and explicitly false for the candidate. This is the same semantic substitution
framework credited to PR686 and the target-side PR713/716/794 lineage.

## Search cost

Suppose the current row supports of R are Sᵢ. A new target shear d←s changes
only row d to `S_d Δ S_s` and adds one entrance and one restoration gate.
Its exact gain is

```
|S_d| - |S_d Δ S_s| - 2.
```

Only strictly positive gains are accepted. The 306 accepted shears leave
6,376 helper injections. Thus D costs 306+6,376+306=6,988, against 18,085.
The other 6,220 local additions remain byte-for-byte in the original fields,
giving 13,208 native ADDs and 11,097 saved. The candidate is fully specified by
the literal recipe, not by a rank-only or optimistic operation estimate.

All paid resources are unchanged: 439 helpers, nine copied totals of rank
seven, rank mass 5,129 and histogram
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`. The native harness checks each
register's complete MOVE path and every COPY/ERASE record. At 5/9/11 stages,
unchanged bridge costs are 666/1,998/2,664 and fresh-copy counts 45/81/99.
The corresponding ADD savings are 55,485/99,873/122,067.

## Exact positive update used by nomination

This argument and its use as an admission guard follow PR794. Replace each
XOR by nonnegative integer addition. Let P be the positive entrance matrix
and Q the positive reverse-order restoration matrix. They generally are not
integer inverses. For incoming nonnegative target bounds a and fixed helper
bounds h, the output bound is `Q(Pa+Rh)`, where R is the current binary read
matrix, interpreted as a 0/1 integer matrix.

Append a shear d←s, with positive matrix G=I+e_d e_sᵀ. Then P′=GP,
Q′=QG, and row d of the binary R′ is S_d Δ S_s. The new bound is
`QG(GPa+R′h)`. Using `G²=I+2e_d e_sᵀ` and expanding row d gives exactly

```
new_bound - old_bound
  = 2 Q[:,d] ((Pa)[s] + sum(h[j] for j in S_s minus S_d)).
```

All factors are nonnegative. Updating Q only requires adding its column d to
column s. The builder maintains this formula for the actual forward and reverse
entry bounds. The independent verifier does not use this update to accept
steps: it reconstructs and literally executes each of the 306 complete partial
words in both orientations, including fresh-center copies and erasures.

Within D every positive target coordinate is monotone, so its maximum occurs
at the D endpoint. The unchanged remainder never reads a target as an ADD
source; its target increments can therefore be precomputed independently of
D. The forward maximum is the larger of the unchanged source/helper maximum
and the new D target endpoint plus the fixed tail increment. In reverse order,
the unchanged reversed tail fixes D's input bound vector; D comes last. These
observations justify the exact incremental full-word admission tests.

## Precision guards and limits

The guard fixes F≤49,347. It sets B≤16,913,320, the smaller of the exact integer
cutoffs from

```
64 F^3 B^2 < 2^104,
2^18 F^5 B^4 < 2^192.
```

The second expression is the pinned source template's
`2^nb F^(K+1) B^K` at K=4, with nb=6(K−1)=18 bridges. The verifier binds the
expression and bridge relation to the source AST and checks that the baseline
reproduces its recorded 177-bit bound and 192-bit charge.

Literal native replay yields F=49,347 and B=9,534,616. The local payload bound
is 699,147,249,763,640,764,132,165,496,832 (100 bits). The nine-stage bound is
633,952,218,342,189,222,305,933,054,575,935,669,674,977,721,489,175,871,488
(189 bits). Both fit the stated existing ceilings. The reverse bound is
larger than the baseline and is charged explicitly. No candidate was rejected
by either guard during this particular nomination.

The verified bound concerns the signed lift's finite cancellation-free
prefix estimate. It does not establish unchanged unrounded invoice coefficients,
all other charged allocations, a full hosted reconstruction, or a new exponent.
The other assumptions of the selected construction remain those recorded in
its maintainer review. This prefix estimate alone does not justify a complete
machine implementation or the analytic multiplication bound.

## Completed domain

All 12,210 ordered pairs are scored at each of 307 iterations, including the
terminal iteration: 3,748,470 scores. Seed 10 fixes tie priority. The declared
1,000-step cap is not reached. The final matrix has maximum next-shear net gain
zero, verified independently on all pairs. This certifies termination for the
specified one-step improvement rule. Zero-gain detours, non-greedy histories,
simultaneous row/column changes and global circuit optimality are outside scope.
