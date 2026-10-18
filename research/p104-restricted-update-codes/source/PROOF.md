# Pointwise defects and translation-updatable codes

All registers in the written identities below contain exact signed integers.
There are `N=2^r` Gaussian addresses and `d=2N` real coordinates. Address bits
are processed in increasing order. Floors are componentwise Euclidean floors.
The fixed pair word is the one of Tekalign/PR3025/3033 and Nick Petalas/PR3035:

```
d=a-b; s=b+floor(d/2); e=i*d;
B=s-floor(e/2); A=B+e.
```

Write `L_r` for the full lifting word, `U_r` for its ideal linear word with
exact halves, `A_r=2^r U_r`, and `D_r(x)=2^r L_r(x)-A_r x`. `A_r` and `D_r`
are integer valued. No approximate native implementation is substituted.

## 1. Periods and a complete finite domain

For one pair put `p=Re(a-b) mod 2`, `q=Im(a-b) mod 2`. Direct substitution
at **both** output addresses gives the credited pair-error identity

```
P(a,b)-C(a,b)=(q-p)(1-i)/2,
C(a,b)=((a+b+i(a-b))/2,(a+b-i(a-b))/2).
```

This holds for negative inputs as well. An even Gaussian difference between
the two input translations leaves this correction unchanged. Consequently the
prefix-parity lattice `Gamma_r` of PR3035 consists of periods of `D_r`.

There is also a simple scalar period. Set `g=floor(r/2)+1`, `q0=2^g`.
After `k` distinct address stages, every nonzero ideal complex coefficient
is a Gaussian unit times `(1+i)^k/2^k`. Each matrix entry has a unique address
path, so there is no coefficient summation in this statement. Multiplication
by `q0` gives `(1+i)` valuation `2g-k`. For every `k<=r-1` it is at least two.
The ideal translated inputs before every next stage therefore lie in
`2 Z[i]`. Induction using the pair identity proves, for all signed inputs,

```
L_r(x+q0 z)=L_r(x)+U_r(q0 z),
D_r(x+q0 z)=D_r(x).
```

Thus a full low-bit box enumerates the entire all-integer defect image.
It is not necessary to enumerate that large box if one has a complete
transversal of the sufficient prefix lattice.

## 2. Binary transversal and the finite images

Maintain an integer basis `B` in original input space and its current ideal
image `Y`. Initially both are the identity. A nonzero next parity condition
is a homomorphism from `B Z^d` onto `F2`. Choose an odd basis column `v`,
subtract it from all other odd columns, and double `v`. These operations give
a basis for its kernel, with index exactly two. The previous lattice splits
as that kernel and its translate by the **old** `v`.

Store that old column, applying identical column changes to `B` and `Y`.
After all parity restrictions for a stage, its ideal update on `Y` is integral.
Induction through the index-two subgroup chain proves that all binary sums of
the stored original-space columns form a complete transversal. No HNF is
assumed, and distinct integer representatives alone are not used as a proof
of distinct cosets. The subgroup-chain argument establishes the latter.

The verifier checks exact small-basis determinants, every prefix condition,
and every representative against the byte-authenticated predecessor floor
word. The complete census is:

| rank | prefix index exponent | cosets | distinct scaled defects | fixed label bits |
| --- | ---: | ---: | ---: | ---: |
| 1 | 2 | 4 | 3 | 2 |
| 2 | 6 | 64 | 25 | 5 |
| 3 | 15 | 32,768 | 10,225 | 14 |

Fiber multiplicities and the exact keyed image/fiber digests are retained in
`RESULT.json`. At ranks one and two, a separately implemented full-box census
agrees, including **every** fiber multiplicity after multiplying by the box's
constant number of representatives per coset. Its ideal matrix also has a
separate closed-coefficient basis check. Rank three has one transversal census
with the written completeness proof, not a second independent implementation.

These are complete all-integer image counts under Section 1, with finite
transversal/box multiplicities. They are not enumeration at rank seven.
The label lengths count states only. No encoder, decoder or recursive tariff
is free. The distinction is real: the maximal translation quotient need not
be the smallest **pointwise** defect label.

## 3. An all-rank failure under source translation

At rank one take

```
x=(0,0,0,0), y=(0,0,1,1), t=(1,0,0,0).
D_1(x)=D_1(y)=0,
D_1(x+t)=(-1,1,-1,1), D_1(y+t)=(1,-1,1,-1).
```

This is ordinary integer translation, with no modular wraparound. Repeat
each four-coordinate block at all higher addresses. The first stage gives
identical outputs in all higher-bit blocks. Every later pair has equal inputs
and is fixed by both its literal and ideal maps. For every `r>=1` this gives

```
D_r(x)=D_r(y)=0,
D_r(x+t)=2^(r-1) repeat(-1,1,-1,1),
D_r(y+t)=-D_r(x+t).
```

Hence defect equality fails translation congruence at **every positive rank**.
The all-rank assertion is a written proof; the implementation checks ranks 1–7.

## 4. The exact abstract state requirement for code-only source updates

Define the full defect-period group

```
Pi={h : D(z+h)=D(z) for every integer z}.
```

Suppose a code `C` and decoder `f` satisfy `D(x)=f(C(x))`. Require that for
**every** integer translation `t` there is a deterministic update `T_t`
using only the code and `t`, with `C(x+t)=T_t(C(x))` for every `x`.

If `C(x)=C(y)`, applying `T_t` and `f` gives `D(x+t)=D(y+t)` for all `t`.
Set `h=y-x`, `z=x+t`; then `h in Pi`. Every code fiber lies in one period
coset, so at least `[Z^d:Pi]` states are needed. Conversely the period coset
itself is a valid code: `D` is well defined on it and translations update
it by coset addition. This is the **exact abstract minimum state count**.
It does not claim an efficient implementation of those updates or decoder.
No homomorphism or action law on all nominal code states was assumed.

For this fixed word, `h in Pi` means exactly
`L_r(z+h)-L_r(z)=U_r h` for every `z`. The authenticated PR3037
[period proof](vendor/period-PROOF.md) identifies this group with `Gamma_r`.
Its necessity argument was rechecked here and by the independent reviewer:
the last pair's output difference forces each independent lower-half
increment constant; lower-half bijectivity then permits pair rigidity.
This is credited imported maximality, not a new maximal-period theorem.
The byte-authenticated PR3035 index calculation reruns to
`128+64+48+32+28+22+21=343` at rank seven. The corollary is therefore:

**A rank-seven defect-determining code supporting all additive source
translations from the code alone needs at least 2^343 states, or 343 bits.**

The index computation is source-bound inherited code; the new part is the
code/period implication. There is no formal-kernel proof. This conclusion
does not exclude immutable-source recomputation, source-dependent updates,
restricted translation sets, approximate outputs, changed words, or a
consumer that retains additional input-dependent state. Such additional
persistent state belongs in the code when applying the theorem. Restored
arbitrary dirty spectators cannot supply missing information for free.
We do not assert that any particular full supplier requires this update
contract; it must be established at the actual source boundary.

## 5. A valid immutable-source alternative, with its complete obligations

The code-only obstruction does not invalidate a direct consumer retaining `x`.
Here is an exact algebraic contract with arbitrary dirty vector `B` and
arbitrary distinct target `Y`. Put `M=2^r` and `Q(B)=floor(B/M)`:

```
Y -= Q(B)
B += A_r x
B += D_r(x)
Y += Q(B)
B -= D_r(x)
B -= A_r x
```

The buffer increment is `M L_r(x)`. Since
`Q(B+M v)-Q(B)=v` for every signed integer `B,v`, this updates `Y` by
`L_r(x)` and restores `B` and `x` exactly. These are mathematical integer
shears, not free evaluations or an admitted circuit. With a `W_B`-bit modular
buffer and `W_B>r`, the same statement holds modulo `2^(W_B-r)` on a target of that width;
ordinary signed-integer outputs instead require sufficient headroom and
explicit carry handling. The finite replay checks 252 signed dirty cases.

The displayed implementation pays

```
2 C_A + 2 C_defect-add + 2 C_Q,
C_defect-add = 2 C_defect-XOR + C_wide-add
```

if a clean encoded correction is computed, added, then uncomputed. It also
needs the source, dirty buffer and target capacities, a clean materialized
correction bank, lookup work, address/program storage, source/table movement,
and any exact division/representation interface. Four XOR-oracle calls occur
in that implementation; an XOR oracle into a dirty target is not a free
integer addition into a wide coordinate. A fused implementation may differ
but needs its own proved and fully charged schedule.

For real source coordinates bounded by `X`, the integer numerator has
`||A_r x||_infinity <= 2^(r+ceil(r/2)) X`. For even `r` each Gaussian matrix
entry has one nonzero real component; for odd `r` it has two. Counting their
magnitudes gives this bound. Thus `W+r` alone is not a sufficient generic
numerator allocation: allow `r+ceil(r/2)+O(1)` additional source bits before
dirty-buffer, addition and carry headroom, including the interior after the
separate `A_r x` addition and the target's initial quotient subtraction.
The actual recursive backend,
physical stock, restoration and complete supplier moment remain unpriced.

For calibration, a **specified unsynthesized full equality-scan XOR table**
with `n>=2` address bits and an arbitrary output uses `n-1` clean AND/flag
bits. Each row computes and uncomputes equality using `2(n-1)` Toffolis,
emits one CNOT per set output bit, and uses two X gates per negative address
control. Summing all `2^n` rows gives

```
Toffoli=2(n-1)2^n, X=n2^n, CNOT=sum row-popcounts.
```

`RESULT.json` gives exact finite table invoices. Given a *precomputed* 15-bit
rank-three transversal label the table has 917,504 Toffolis and 3,145,728
explicit table bits. Producing that label is additional. A raw rank-three
32-bit address full scan has 266,287,972,352 Toffolis. These are exact costs
of this chosen scan, including zero-output rows, not minima or circuit
lower bounds. Rows may be pruned and logic may be synthesized. No such large
table was generated or executed. Smaller images alone do not remove input
address acquisition or output materialization.

A structured rank-one control from the credited pair identity uses two clean
parity bits, 16 CNOTs, four Toffolis and four X gates to XOR eight signed defect
bits into an arbitrary target, restoring source and work. All 4,096
source/target pairs pass. This demonstrates why scan prices are not universal
bounds; it is not claimed as a new primitive or a completed wide consumer.

## Scope and decision

The changed pointwise interface compresses small-rank labels, but the proposed
code-only mutable version cannot retain that compression under arbitrary
additive updates. The retained-source alternative has an exact dirty contract
and a stated bill, with unknown backend/access costs still unknown. Stop at
this interface result; no rank-seven synthesis, all-size supplier, favorable
complete recursive comparison or new kappa is established.

Ross Richardson, with substantial OpenAI Codex assistance and a separate internal
carry-and-rounding review. Apache-2.0. Credit Tekalign/PR3025/3033, Nick
Petalas/PR3035/3037, Ross Richardson/PR3043, Arham Tahir/PR3046, ywz65/PR2586,
and the retained P104/native lineage. No independent human review is claimed.
