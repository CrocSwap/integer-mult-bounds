# Raw endpoints and projected cleanup have independent ranges

This is a theorem about the stated scalar operation alphabet over F2, followed
by a source-bound finite witness. It does not relax the selected supplier's
hypotheses. PR1105 / @woklerx already supplied the raw-feedback obstruction,
the four-block criterion and the complete three-wire census. The new results
are the constructive all-dimension range, sharp identity-loop lengths and the
selected-word witness below. PR1194's correct semantic-D theorem is unaffected.

## 1. Model and exact joint range

There are k>=1 coordinates z and q>=1 coordinates y, with n=k+q. Every value is
arbitrary in an F2-module M. Thus the identity is uniform in scalar dimensions
and in the value space, including pointwise F2-valued streams. There is no clean
ancilla, reset, allocation, COPY or hidden operation in this abstract model.

A unit-cost gate T_ab is `r_a += r_b`, a!=b. All source/destination pairs are
allowed: this explicitly removes the original target-feedback prohibition.
A chronological word w has raw matrix R(w). Delete its y-destination gates,
keeping the order of the other gates, to obtain its projected matrix P(w).
Products act on column vectors; the last executed gate is the leftmost factor.
The prescribed scalar projected cleanup is P(w)^(-1).

Let

`G = GL(n,2)`, `H = { [A B; 0 I_q] : A in GL(k,2), B in F2^(k x q) }`.

**Theorem.** Every pair in G x H is `(R(w),P(w))` for a finite word w on these
same n registers. In particular, every H element occurs in the raw-identity
fiber. No target or helper is assumed clean, even temporarily at a boundary.

The forward inclusion is immediate: every gate is invertible, and every kept
gate fixes all y rows. The reverse inclusion follows from the explicit loops
and factorization below; it is not inferred from finite enumeration.

## 2. Identity loops realizing every projected elementary gate

Fix a<k and b!=a. If a target c different from b is available, execute

```
a += c
c += b
a += c
c += b
a += b
```

The first four gates add b to a, restore c and leave b unchanged; the fifth
restores a. This is the raw identity for all dirty inputs. Projection removes
the two c-destination gates. The remaining `a+=c; a+=c; a+=b` has matrix T_ab.
Such c exists whenever b is a z coordinate, or q>=2. Every operation is counted:
this loop costs exactly five unit gates and uses only the declared registers.

If q=1 and b is that sole target, execute

```
a += b
b += a
a += b
b += a
a += b
b += a
```

On the two involved coordinates `(T_ba T_ab)^3=I`. Projection keeps the three
a-destination gates, whose product is T_ab. This costs six gates and also
restores arbitrary values of both coordinates. All other coordinates are fixed.

Elementary gates with z destinations generate H. To see this constructively,
row-reduce A using only z rows, then clear the remaining B entries using target
rows. Reversing those operations factors H. Replacing each factor with its
five- or six-gate loop realizes `(I,H)` on the same registers.

For arbitrary R, ordinary binary elimination gives a chronological word w0
with R(w0)=R. Let P0=P(w0). Append identity loops realizing `H*=P P0^(-1)`.
The raw result is still R and the projected result is `H* P0=P`, as required.
`algebra.joint_word` implements precisely this construction.

One explicit size bound is

`n(n-1)+3(n-1) + 6[k(n-1)+3(k-1)]` gates.

The first term bounds binary elimination for R. For H*, z-row elimination
uses at most k(k-1) additions and k-1 swaps (three additions each), followed
by at most kq target-column eliminations. All prep/restoration gates are inside
the displayed cost. When q>=2 the multiplier six can be replaced by five.
The bound concerns this constructor, not an arbitrary pair's minimum circuit.

Both coordinate classes matter. If q=0, P(w)=R(w) for every word, so their
joint range is diagonal instead of a product.

## 3. The elementary loop costs are sharp, even with extra dirty registers

First, any raw identity word of length at most four has P=I for any partition.
A one-gate word is not identity; a two-gate identity repeats the same gate.
For distinct elementary gates the exact product is

`(I+E_ab)(I+E_cd) = I+E_ab+E_cd+[b=c]E_ad`.

If b!=c, its difference from identity contains exactly the two gate entries.
If b=c, the extra entry is distinct from both: it either marks the directed
length-two path and its shortcut, or is a diagonal entry in the two-cycle
case. Thus the two gates and their order are determined, except that commuting
gates may be exchanged. A product of two distinct gates cannot be one gate.
It follows that no length-three word is identity, and any length-four identity
consists of pair cancellations or a commutation relation. Deleting all gates
of one destination class preserves each such identity. This proves the lower
bound five in arbitrary dimension, without a bound on unused registers.

The two-product classification is independently checked on all 144 ordered
pairs on four labels, giving 97 distinct products and 1,044 projected-relation
checks. Four labels suffice for the nonidentity two-product argument because
the displayed support reveals every endpoint of the two gates. Degenerate
identity pairs are already covered by the repeated-gate case. This finite
check corroborates the preceding symbolic classification.

For q=1, a projected gate from the sole target b into a z coordinate a needs
at least six gates. Suppose a raw identity word had length at most five.
Every register that is written must be written at least twice: with only one
write, its final row would differ from its initial row by the nonzero donor
row at that instant, since every prefix is invertible. Hence at most two
registers are written. Register a must be written; the sole target b must
also be written, or projection would delete no gates and P would equal R.
All other registers remain their independent initial rows.

Restrict to coefficients of the original a,b values in the two written rows.
Gates from other, unwritten registers do not affect this 2x2 restriction.
The only remaining operations are A=`a+=b` and B=`b+=a`. They are distinct
involutions and AB has order three. A nonempty alternating word of length
less than six is not identity: an even length gives AB or (AB)^2 (or their
inverses), while odd alternating words are nonidentity involutions. Any
identity word of length at most five therefore cancels in adjacent equal
pairs and has an even number of A operations.

After projection the coefficient of the original b in a is exactly that A
parity; unwritten registers cannot contribute b. It is zero, contradicting
P=T_ab. This proves the six-gate lower bound for any number of other dirty
z registers. Together with the loops above, the exact minimum is five when
an alternative target c is available, and six in the sole-target case.

These are minima for **raw identity loops with a prescribed nontrivial
projected elementary effect**. PR1105's three-gate minimum has a different
premise: its raw endpoint need not be identity. Neither minimum contradicts
the other, and no complete-program circuit optimum is claimed.

## 4. Consequence for any proposed endpoint-only cleanup test

For each fixed raw matrix R there are exactly

`|H| = |GL(k,2)| * 2^(kq)`

distinct attainable projected matrices. These are counts of joint matrix
states, not probabilities or proportions of the infinitely many words.

Fix a preliminary D and desired complete operator S. If one projected cleanup
can satisfy `P^(-1) R D = S`, then its matrix is uniquely

`P = R D S^(-1)`.

Provided this matrix is in H, exactly one of the |H| attainable matrices in
that raw fiber gives the desired completion; otherwise none does. Thus a test
that inspects R alone cannot distinguish successful from unsuccessful
projected cleanup throughout this enlarged alphabet. Additional chronological
or cleanup information is necessary. The original H1/H3 prohibition supplies
such information; this theorem does not challenge it.

## 5. Exact selected PR589 witness and full boundary

The live source pins specify the unchanged PR589 word, its original owning
checker, literal exporter and retained scalar envelope formulas. It has
111 sources, 111 targets and 439 helpers, totaling 661 dirty coordinates.
The retained scatter uses one clean temporary nine times; all nine COPY and
ERASE pairs are included, and no new temporary is introduced by the witness.

Let a=222 and b=223 (the first two helpers), c=111 (the first target). Immediately
before the original A, after unchanged D, insert the five-gate loop from §2
at frame 0. Targets and helpers all enter that cut at frame 0, and the loop
returns their exact state before the original A. Every other word field is
unchanged. With the **original C**, the complete word still has precisely its
original 661-column map. This is the positive control; no original theorem
needs to be weakened to understand deletion of this neutral block.

The new projected raw matrix, however, is `P_old T_222,223`, so its inverse is
`T_222,223 C_old`. A scalar compilation of the projected inverse is therefore
the original C followed by the single full-frame gate `222 += 223`.
Both helpers are at the full frame at that time. The literal projected reverse
would also contain two equal helper-from-target gates; their scalar cancellation
explains the shorter compiled form. We **do not execute** those two potentially
illegal full-frame target reads or claim the original literal H4 is met. The
proposed relaxed rule is equality to the projected inverse as a scalar matrix,
implemented here by a frame-legal helper-only suffix.

This compiled cleanup corrupts the original dirty input of helper223 into
helper222. Relative to the original complete map, the only differing row is

`output[222] = input[222] + input[223]`.

All source and target outputs are unchanged. The helper-zero restriction also
looks unchanged, so it misses precisely this dirty-state error. The original
owning checker correctly rejects the candidate with `helpers not restored: [222]`.
There is no claimed production-checker defect.

The raw A/scatter/B matrix is identical in all three cases. The invalid case
satisfies the actual raw U/J/K conditions, retains H2 and H5, and its compiled
C is exactly the inverse of its projected raw word. H1/H3/H4 remain explicitly
false, and `C_is_U_inverse` fails. The positive neutral-loop control has the
opposite distinction: complete restoration succeeds while C is not the
projected inverse. This separates both directions of the missing implication.

| Complete quantity | Baseline | Neutral loop, old C | Loop, projected C |
|---|---:|---:|---:|
| ADDs | 24,305 | 24,310 | 24,311 |
| MOVEs | 2,911 | 2,911 | 2,911 |
| COPY / ERASE | 9 / 9 | 9 / 9 | 9 / 9 |
| Record count | 27,234 | 27,239 | 27,240 |
| Positive F | 49,347 | 55,059 | 55,059 |
| Positive B | 1,113,070 | 1,113,070 | 1,113,470 |
| Local / nine-stage envelope bits | 93 / 177 | 94 / 178 | 94 / 178 |
| Exact complete dirty map | pass | pass | **fail** |

All 661 ordered frame paths are identical. The paid histogram stays
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`, rank mass 5,129. The exporter
and literal stream agree opcode by opcode. Both strict retained scalar
inequalities `64 F^3 B^2 < 2^104` and `2^18 F^5 B^4 < 2^192` hold, and their
formulas are bound to the predecessor AST. These are scalar-envelope checks,
not a fresh native/packed precision proof. A valid paid budget cannot repair
the exact dirty-state failure.

## 6. Verification scope

Independent packed-row and literal-permutation engines enumerate every joint
state in the (k,q)=(1,1),(1,2),(2,1) cases: 12, 672 and 4,032 states, with
28,248 edges in total. They agree on every shortest distance and all 37,680
literal input assignments. The 4,032-state case reproduces PR1105, rather
than being claimed as new. The constructor also attains all 4,716 pairs.

All 12,630 parabolic matrices with k<=3 and 2<=k+q<=5 are constructed in the
raw-identity fiber and checked on every Boolean assignment. Thirty-nine larger
fixtures through n=64 are checked by independent literal columns. These finite
checks support the code; the all-dimension theorem and sharp costs are proved
above. The general constructor is not claimed to minimize total gate count.

The selected-word replay covers all 661 dirty columns in both directions for
all three variants, including literal COPY/ERASE. Frame/lattice checks and the
exporter are source-bound retained implementations; the row and numeric-column
replays are new separate implementations. No native 5/9/11-stage, owner/window,
hosted supplier or outer assembly replay is claimed. The proof is written,
not Lean-checked. No supplier saving or new kappa follows.
