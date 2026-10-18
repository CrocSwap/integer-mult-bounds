# Exact output channels for the P104 lifting defect

Let r>=1, N=2^r, and x in Z[i]^N. Real coordinates are interleaved by
address. L_r is the fixed Tekalign/PR3025/3033 word, applying on address bits
0,...,r-1 the signed-floor pair

```
d=a-b; s=b+floor(d/2); d=i*d;
b'=s-floor(d/2); a'=b'+d.
```

Floors are componentwise Euclidean floors. U_r is the corresponding ideal
linear word with pair
`C(a,b)=((a+b+i(a-b))/2,(a+b-i(a-b))/2)`.
Write delta=L_r(x)-U_r(x) and D=N*delta. All mathematical upper bounds in
this proof hold for every signed integer input, without a magnitude bound.
The finite executable has the separate rank 1..7/4096-bit entrance bounds.

## Universal output subspace

If p_R and p_I are the real and imaginary parities of a-b, each literal pair
output differs from C by `(p_I-p_R)*(1-i)/2`. This includes negative odd
differences: substituting `floor(t/2)=(t-(t mod2))/2` proves the formula.
Let e_j be these errors immediately after the actual literal stage j. Then

```
delta = sum_j U_(r-1) ... U_(j+1) e_j.
```

This follows by telescoping the actual and ideal prefixes. It does not assume
independent rounding errors. Each e_j is equal on a bit-j pair and belongs
to `(1-i)/2 * {-1, 0, 1}` at each address.

Use the unnormalized Gaussian Walsh transform
`(Hz)_m=sum_a (-1)^popcount(m&a) z_a`, with H^2=N I. The bit-k ideal stage
has Walsh eigenvalue 1 if m_k=0 and **+i** if m_k=1. Thus the m-th transformed
defect lies in the real subspace

```
W_m=span_R{(1-i)*i^popcount(m>>(j+1)) : m_j=0}.
P_m={popcount(m>>(j+1)) mod2 : m_j=0}.
```

The dimension of W_m is |P_m|, which is zero, one, or two. The all-one mask
is the only zero-dimensional mode. For a one-dimensional mode P_m={p},

```
Im(z_m)=(2p-1)*Re(z_m).
```

These modewise equations are independent because H is invertible and distinct
modes have disjoint coordinates. They constrain every actual defect, even
though the coefficients of different stage errors can be correlated.

Let F_0=0,F_1=1,F_(j+2)=F_(j+1)+F_j. Scanning mask bits from high to low,
the suffix parity starts at zero. Words allowing a zero only at even suffix
parity number F_(r+2): the state transitions are the two-state Fibonacci
matrix, with a zero loop only at even parity. Allowing zeros only at odd
suffix parity gives F_(r+1). The two sets intersect only in the all-one word.
Remove that word from each set to count one-dimensional modes. Therefore

```
n_0=1, n_1=F_(r+3)-2, n_2=2^r+1-F_(r+3),
R_r=sum_m dim W_m=2^(r+1)-F_(r+3).
```

Consequently the real span of all D_r(x) has dimension at most R_r. This is
an all-rank written upper bound, not a formal-kernel proof or an all-rank
attainment theorem.

## Finite sharpness certificates

For each r=1,..., 7, RESULT.json gives actual integer input descriptors and
nonzero elimination pivots modulo the prime 65537. The corresponding D vectors
have rank R_r modulo that prime, hence have rank at least R_r over Q and R:
some integer R_r-by-R_r minor is nonzero modulo the prime and therefore is
nonzero as an integer. The universal upper bound proves equality for all
integer inputs at each of these seven ranks.

The separate independent.py uses a different impulse order and signed LCG
sample, prime 65521, and its own integer word, elimination, and Walsh code.
It reaches the same seven ranks: 1, 3, 8, 19, 43, 94, 201. Both primes are checked
by integer trial division. Neither checker enumerates the rank-seven residue
domain or proves attainment for r>=8. These are exact finite independence
certificates combined with an all-input written upper bound, not a census
of every defect value.

Any fixed real-linear decoder from k real channels has image span of dimension
at most k, even if its encoder is nonlinear. Thus k>=R_r is necessary at the
seven certified ranks. The construction below attains this real-channel count.
This is not a bit-information bound, a nonlinear decoder bound, a generic
circuit lower bound, or a recursive-cost floor.

## Integral packet and sufficient widths

Define c=H*delta. Walsh diagonalization gives

```
c=H*L_r(x)-diag(i^popcount(m))*H*x in Z[i]^N,
D=H*c.
```

Store Re(c_m) in a one-dimensional mode, both components in a two-dimensional
mode, and no component in the all-one mode. The missing components are fixed
by the displayed phase lines. This gives exactly R_r integer channels, and
decoding the scaled defect D requires **no final division**.

For z(m)=r-popcount(m), each of z(m) possible stage contributions to either
real component of c_m has magnitude at most N/2. The factor of two from the
equal bit-j pair cancels the local denominator two. Hence

```
|Re(c_m)|, |Im(c_m)| <= M_m=(N/2)*z(m).
```

The sufficient two's-complement width is `1+bit_length(M_m)` for each active
stored component. At r=7 the packet uses seven8-bit, eighty-six9-bit, and
one-hundred-eight 10-bit channels: **1910 bits**. This is an upper allocation,
not a sharp width or minimal bit encoding. In particular it must not be
identified with PR3035's343-bit input period code.

A precise full-coordinate comparator follows from the forced local phase.
For a suffix of k ideal stages applied to `(1-i)*q/2`, the real-coordinate
row absolute sum as a map of real q is `2^(floor(k/2)-1)`. For even k, all
2^k coefficients have real absolute value `2^(-k/2-1)`; for odd k, half have
zero given component and half have absolute value `2^(-(k+1)/2)`. Imaginary
components obey the same estimate. Thus

```
|D_a component| <= B_D=(N/2)*sum_(k=0)^(r-1) 2^floor(k/2).
```

At r=7 this gives 1408 and a sufficient 12-bit uniform component allocation:
256*12=3072 bits. The bound is not claimed sharp. The 1910 versus 3072
comparison concerns these particular sufficient storage allocations, not
minimal encodings or total live physical storage.

## A fully restored delivery macro circuit

The source consists of the retained packed c, in its stated signed widths.
There are r+1 disjoint clean work banks W_0,...,W_r, each with 2N real words,
and an arbitrary dirty target S of 2N*b_D bits, where b_D is the uniform
signed width for D. Dirty spectators are untouched. Let

```
w_0=1+bit_length(N*r/2),  w_k=w_0+k.
```

Populate W_0 from the packet by 2(N-1) signed ADD shears into zero targets,
including the missing phase-line components. At stage k, each real Walsh
pair is produced in disjoint zero words by four shears:

```
u += a; u += b; v += a; v -= b.
```

Sources are retained. A shear into a w-bit target means modular addition
modulo 2^w of a source sign-extended from its declared width. It is reversible
on the full register state space. Inductively W_k has true integer magnitude
at most 2^k*N*r/2, so the specified signed widths suffice, including after the
first of a pair of target updates. A modular read is interpreted using its
source width before widening. An unsigned interpretation can change delivery.

XOR the low b_D bits of each W_r word into S, then execute **every shear in
literal reverse order with opposite sign**. At each reverse update its source
still has exactly the value used in the forward update. All W banks return
to zero; the source packet and dirty spectators are unchanged. For actual
encoded defects, W_r=D lies in the signed b_D range, so these low bits are
the exact two's-complement representation. The complete boundary is

```
(c, 0_work, S) -> (c, 0_work, S XOR signed_encode(D)).
```

Per r=7 block the exact invoice is:

| Item | Count |
|---|---:|
| Signed modular ADD macros, both directions | 7676 |
| Target-width ADD histogram | 508 at 10 bits; 1024 each at 11,..., 17 bits |
| Target CNOT copies | 3072 |
| Clean W-bank bits, widths 10,..., 17 | 27648 |
| Retained input packet | 1910 bits |
| Arbitrary XOR target | 3072 bits |

The input and target are additional to the 27648 work bits. To consume D as
numerical data, S must start clean, adding that 3072-bit clean-bank premise.
Modular ADD implementation, source sign-extension/carry ancillas and their
cleanup, instruction/table access, controller, movement, and physical routing
are additional priced obligations. These are complete counts in a declared
modular-ADD macro currency, not CNOT/Toffoli gate totals or project native-child
tariffs. W-bank cleanup is literal; arbitrary dirty W-bank entrance is outside
the contract and is rejected by the implementation.

## Connection to a retained-source consumer and stopping decision

The credited PR3059 consumer uses immutable x, exact A=N*U_r(x), D, arbitrary
dirty scratch B and an additive target Y. In order, subtract floor(B/N) from
Y, add A+D=N*L_r(x) to B, add floor(B/N) to Y, then remove A+D from B.
For every signed B this restores B and adds L_r(x) to Y. Substituting the
packet's exact decoder for D preserves this algebra. It does not supply a
free exact wide backend or a clean numerical D bank.

If L(x) is already known, the direct integer formula for c costs two Walsh
transforms and 2N real subtractions on potentially wide values. If D has
already been formed, encoding requires another Walsh transform and exact
division by N. A plain decode costs 2Nr real additions. The reversible
layered oracle above explicitly pays its additional retention and cleanup.
None of these interfaces removes the unchanged 448 narrow pair sites at r=7.

The packet can be smaller while the complete implementation is more expensive.
Inserting this decoder into the unchanged scalar split therefore supplies no
favorable recursive comparison. A different direct encoded producer/consumer
may be investigated only with its source access, exact backend, full child
profile, widths, all helper restoration and physical costs. No supplier,
selected-frontier change, new kappa, or general obstruction is proved here.
The family decision is to stop at this scoped output-interface result.

Ross Richardson with substantial OpenAI Codex assistance, including a separate
internal mathematical specialist. Credit Tekalign/PR3025/3033 for the fixed word
and scalar split, Nick Petalas/PR3035/3037 for the input-lattice boundary, Ross
Richardson/PR3043 and Arham Tahir/PR3046 for reducer/inverse interfaces, PR3059
for the pointwise/dirty-consumer boundary, ywz65 and the retained P104/native
lineage. Generic Walsh diagonalization and modular shears are not claimed new.
Apache-2.0; no independent human or formal-kernel review is claimed.
