# A physical-stream counterexample to the current idle-star overlay

Audited: Rohan Arun/PR3184 at `ffab383a5f78eb1a4ad4c7c7259a4f32b86f9481`,
using Jeremy Diviney/PR3148 at `f2927a4b8afcf0701a6b945e14f30de1d94f5176`.
The unchanged completed local-invocation contract is assumed throughout.
This concerns composition of that contract, not a new native-word audit.

## Operator convention and equality criterion

The pinned `INHERITED-COMPLEX-GEOMETRY.txt` defines

```
X_v f(x) = f(x+v),
C_v = ((1+i)I + (1-i)X_v)/2.
```

On `chi_u(x)=(-1)^(u dot x)`, `C_v` has multiplier `i^(u dot v)` and
translation has multiplier `(-1)^(u dot v)`. Translations keep the Fourier
character fixed. Each physical stream has its own multiplier.

For a single-axis transfer, let `P_s,P_d` be donor/receiver coordinate
projectors, `E_s=I+(i-1)P_s`, `E_d=I+(i-1)P_d`, and `M` the unchanged invertible
operator between phase positions at an active character. The transfer
preserves the operator exactly when

```
E_d M = M E_s,
equivalently M P_s M^(-1) = P_d.
```

Cancel the common invertible prefix and suffix to obtain the first equation;
subtract `M` and divide by `i-1` to obtain the second. Inactive characters
impose no condition. A complete transfer needs equality at every character
and cover, accounting for other moves. `algebra.intertwines` checks this
finite matrix equation. Endpoint orthogonality and preservation of a combined
axis multiset do not imply it. Gareth Davidson/PR1387 already established this
obstruction on PR1094; here it is bound to the new candidate's literal inputs.

## The committed witness

At replica zero, port zero, the committed STAR-MOVES payload contains exactly

```
child 10 -> child 12: [16,32,64]
child 10 -> child 13: [128,256,4096].
```

The current PLAN maps these children to `Y3`, `X0`, `Y0`. The actual PR3148 fill
leaves bins 8,10,12,13 unhosted at rank 48. The checker derives this from owner
rows. It checks each moved axis against the original receiver axes, all stage
entry/exit X and Y translations, terminal Y and both endpoint translations.
Final axes are orthonormal, the combined multiset is unchanged, and ranks stay
at most 51. Thus the candidate's stated structural conditions accept this group.

At cover identity and `u=16`, exactly axis 16 of these six axes is active.
The overlay removes one factor `i` from Y3's child-10 event and inserts it on
X0's child-12 event. The move to child 13 is inactive. Other `(replica,port)`
idle overlays act on separate data blocks; owner assignments and hosted charts
are fixed.

## Interval proof allowing arbitrary helper phases

Between child 10 and child 12, the data template has the bridge between pairs
2 and 3, local stage 6 on pair 2, pair-3 idle children 9 and 11, the inverse
bridge, and local stages 7 and 8 on pair 3. None mixes X0 with another stream.
Interleaved completed calls on other replicas contribute diagonal nonzero
helper multipliers, under the retained local contract. Therefore this interval
preserves the X0 coordinate line for every choice of those phase values.

Let `P` be the common invertible prefix ending just before the donor event.
Choose input `P^(-1)e_X0`. Removing a phase on Y3 does nothing to this state.
The interval keeps it on the nonzero X0 line. At the receiver the overlay adds
factor `i` on that line. The common invertible suffix cannot identify two
vectors differing by `i`. Hence the committed overlay changes the operator.

This proof uses the candidate's completed local F/B and dirty-helper contracts.
It needs no exhaustive Fourier enumeration. A violation of those local
contracts would be another obligation, not a repair of this composition.

## Exact finite calculation and source binding

The new source checker reconstructs ten copies of the literal base fill and
applies all 145 preimage-checked edits. It serializes and hashes all 2,717,280
rows in the original streaming format. The decoded payload SHA256 equals

```
8f4d6965ba573ff2b71fd7bf6b552643e086739d90bd73c55889502077638e00
```

All 30 hosted occurrences affecting replica zero, port zero are retained,
including calls on other replicas. Slices use actual dispatched provider widths.
Occupied coordinates form disjoint compact prefixes; their complements remain
at the original idle events. Replica-zero local call indices in the lifted
order are `0,100,300,580,960,1440,2000,2660,3400`. RESULT.json stores the
projected rows, interval and exact matrices.

At stage `j`, the canonical two-stream macro is `D_j F D_(j-1)^(-1)` or
`D_j B D_(j-1)^(-1)`, with `F:(X,Y)->(X,Y+X)` and `B:(X,Y)->(X-Y,Y)`.
For Fourier character `u`, frame exponents are `X_-1=u dot q`, `Y_-1=0` and

```
X_j = popcount(u & ((1<<(9+8j))-1)),
Y_j = X_j - (u dot q),          j >= 0.
```

These canonical frames include the stored stage adapters. A bridge acts on X
and by inverse transpose on Y. The final Y translation precedes
`(X,Y)->(Y,-X)`. At cover identity the all-live correction vanishes; bank
padding acts on separate bank streams. Replay uses exact Gaussian integers
and preserves each factor's physical stream.

At `u=16` the baseline is `i I_8`. Exactly three entries change:

| Output, input | Baseline | Committed overlay |
|---|---|---|
| Y0, Y0 | i | -1 |
| Y1, Y0 | 0 | -1-i |
| Y3, Y3 | i | 1 |

Input only on Y0 therefore gives an unwanted nonzero Y1 output. Baseline
controls cover zero, all 73 coordinate characters, all-ones and 72 adjacent
pairs: 147 modes, not all `2^73`. One failing mode proves the negative claim.

## Limits

This excludes physical admission of this exact overlay under its unchanged
contract. It does not certify the complete baseline or invalidate the selected
construction. Native internals, full supplier/outer admission, all-size compiler,
precision/tape, recovery and analytic premises are not replayed. No improved
multiplication exponent follows from the rank bill without physical equality.
