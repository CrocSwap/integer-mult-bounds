# A batched reversible lifting core at linear precision

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
including analysis subagents. Apache-2.0. I give a conditional construction
and finite semantic evidence, without a formal-kernel proof.

## 1. The retained premise and the new conclusion

I assume PR2287's completed exact C-layer algorithm and its named physical
bit-interchange, source-refinement, precision and parking premises. In its
notation, fix

    epsilon=997/1000, spacing=1/500, sigma=599/600,
    d=floor(p^epsilon), K=floor(d^spacing).

For any D<=d selected axes, one common offset in D consecutive complete
K-bit chunks, arbitrary complete spectators, and 2^Theta(p/d) Gaussian
coefficients per record, that algorithm computes the exact C tensor in
O(V d^sigma) time. Here V includes the guarded coefficient bits, and total
address/descriptor length is O(p). I use the C endpoint before the source's
Hadamard normalization and truncation. I do not independently verify its
all-size physical refinement in this package.

Consider N=2^n Gaussian integers indexed by n address bits, with r active
axes 0,...,r-1 counted from the least significant bit. Assume

    1<=r<=n, n=Theta(r), W=Theta(r),

where W bounds the signed input-component widths. Fix these parameters
before reading coefficient values. Choose a shared working width
w=W+O(r) and an integer precision p=Theta(w+r), large enough for all
normalized inputs below. Forward and inverse calls retain the same p and
the same order. Their order must not depend on observed input magnitudes.

Under the retained premise, I construct a bijective integer lifting map
L on these axes and its exact inverse with complete core time

    O(N r^(2-997/600000))

and additional clean workspace

    O(N r^(1+997*599/600000)) + F,

where F is the fixed compilation allowance from the inherited machine.
The data arrays themselves occupy O(Nw) bits. This workspace bound includes
reversible histories; I do not claim linear space or a dirty-workspace
implementation.

For the ideal unitary U=C^tensor-r on the active axes, both integer maps
obey the absolute Hilbert-norm error bounds

    ||L(x)-U x||_2 <= r sqrt(N/2),
    ||L^-1(y)-U^-1 y||_2 <= r sqrt(N/2).

They apply to arbitrary Gaussian integer inputs, with the time/space
bounds on the stated width domain. Scaling each integer unit by 2^-p
scales these error bounds by 2^-p. This is a standalone core theorem.
Native monomial wrappers, a collector's consumer, hosting and a full
supplier moment require their own costs and contracts.

## 2. Declare the new nonlinear order

Write ell=ceil(p/d). For sufficiently large r, ell<r. Regard the existing
flat order

    [higher n-ell address bits][low ell bits][Gaussian component words]

as records with 2^ell Gaussian coefficient fields. This interpretation
copies no bits and adds no address range. The low ell bits remain inactive
during the fast part, including during its inverse.

Put m=floor((r-ell)/K). The fast region contains m complete K-bit chunks
starting at address position ell. Divide those chunks into groups of at
most d chunks. For a group with h chunks, process offsets rho=0,...,K-1
in that order. At offset rho, run the h-axis lifting block on

    ell + first_chunk*K + rho + j*K,  j=0,...,h-1.

After all groups, apply direct pair lifts on the fewer than K high leftover
active axes, then on the low ell deferred axes. Thus every active axis
occurs once. Define L to be this literal ordered product. Reverse the whole
declared order and invert each pair to define L^-1.

This order changes PR3033/3072's consecutive-axis integer word. For a
four-entry input (0,0,0,1), with real entries, orders (0,1) and (1,0)
give (0,1,0,0) and (0,0,1,0), respectively. The finite checker retains
this control. Only the ideal C factors commute across distinct axes.
I neither execute nor grant a dense-to-interleaved bit-position permutation
to equate the two nonlinear words.

All fast calls use the same permanent coefficient suffix. Other groups,
unused bits and higher address coordinates remain complete spectators.
PR2287 obtains its own row/compact fields from its reserved selected
chunks, processes those reserved selected axes, and restores the fields
before return. I use that existing construction rather than add fresh
spectator dimensions. The full address length n is O(p), and
2^ell=2^Theta(p/d) satisfies its long-record condition. Also

    epsilon*(1+spacing)=499497/500000 < 1,

so dK=o(r). A group fits in the original address range. The final group
uses h<=d complete chunks; the separate direct tail avoids an incomplete
K-bit chunk. For the finite initial range in which these fits or the
retained compact inequalities fail, use direct lifts. Since n,W=Theta(r),
that range changes a fixed time constant, not the displayed exponent.

## 3. Exact scaled linear output on each full batch

Tekalign's PR3033 supplies the signed residue identity. For any ordered
k-axis block B, including an arbitrary coordinate relabeling, put
g=floor(k/2)+1. For Gaussian integer x, split each real component using
Euclidean division:

    x=2^g q+s,  0<=Re(s),Im(s)<2^g,
    B(x)=2^g U_k(q)+B(s).

The same statement holds for B^-1 and U_k^-1. I retain this guard rather
than reduce it to the weaker integrality-only minimum.

The k-axis C tensor and its inverse have coefficients that are Gaussian
units divided by (1+i)^k. Since 2 is a unit times (1+i)^2,
2^g U_k and 2^g U_k^-1 are integral whenever g>=ceil(k/2). Their product
is 2^(2g)I; the two scaled integer maps are not mutual inverses.

For a signed w-bit input q, choose p>=w+2 and regard it as 2^-p q.
Each coefficient then lies in the unit disk. PR2287 computes the exact
C endpoint on its grid 2^-(p+Delta), Delta=ceil(2^210000 d).
If z is its returned integer numerator, then

    z=2^Delta U_k(q),
    2^g U_k(q)=z/2^(Delta-g).

The output integrality just proved makes this shift exact. Read the
discarded low bits once, check they are zero, and copy the retained bits
with signed extension. Do not perform Delta-g repeated full-word HALF
passes. Normalization, shifts and word-width conversion cost O(Np).
The internal source width p+2Delta+3 is O(p), including its enormous fixed
constant. A returned scaled value needs w+g+ceil(k/2)+O(1) bits.

For the opposite orientation, let S exchange real and imaginary components
pointwise. Since S(z)=i conjugate(z),

    S U_k S = conjugate(U_k) = U_k^-1.

The last equality uses this symmetric coordinate C tensor; I do not claim
it for an arbitrary Clifford map. Two S scans cost O(Np). The forward
algorithm on S q therefore supplies the opposite scaled map on arbitrary
integer q, without assuming q lies in the image of a previous transform.

Each call acts on the complete N-entry batch. Its volume is Theta(Np),
including all coefficient fields and spectators. Use the source's uniform
tariff O(Np d^sigma) even when k<d. An isolated 2^k cube with only a few
coefficient fields would not satisfy this source premise.

## 4. Source preservation and paid clean history

I use Bennett's standard compute-copy-reverse construction, with its time
and history charge, rather than treat an irreversible routine as a
reversible oracle. See C. H. Bennett, [Logical Reversibility of Computation,
1973](https://worrydream.com/refs/Bennett_1973_-_Logical_Reversibility_of_Computation.pdf).
For a deterministic fixed-tape computation of T steps, record the finite
transition choice and overwritten symbols in a constant-size history item
per step. Copy its completed output by XOR into the separate target, then
undo the trace, restoring the source, heads and work. This costs O(T+output
length) time and O(T) clean history. Each later call can reuse that history
after erasure. The target may begin dirty; its XOR update is reversible.

Apply that construction to each exact scaled-linear routine. Its clean
XOR oracle costs O(Nw d^sigma) time and history. All scans and input/output
conversions from section 3 lie inside this tariff. The dependency is
acyclic: the earlier C algorithm uses the retained ordinary bit backend;
neither uses this new lifting construction.

PR3072's clean evaluation pattern now applies to the whole batch. Preserve
x, copy its quotient and residue fields, compute the scaled wide term,
compute the narrow B(s), XOR their sum into the target, then uncompute
the private outputs and split fields. Use the opposite narrow word and
opposite linear orientation for B^-1. Integer addition in the sum needs
the declared headroom; output XOR itself works for any target bits.

To update x in place, evaluate B(x) into a zero bank y, then evaluate
B^-1(y) by XOR into x. The latter clears x exactly; swap the bank roles.
This uses four scaled-linear XOR oracle invocations per batch, including
their cleanup. Each such oracle pays a forward trace and its reversal.
I do not count either its private output or its history as free scratch.

A narrow k-axis block has O(k) component width. A sequential split,
pair-evaluate and merge implementation costs O(Nk) per axis and
O(Nk^2) for the block. Binary countdowns select whole half-blocks;
no n-bit random address is charged once per butterfly. Reinitializing a
length-a countdown occurs at most N/2^a times, so its total setup cost
is O(N), in addition to polynomial-size header work. If one uses generic
record-and-reverse for this narrow routine too, charge O(Nk^2) clean
history and a constant number of narrow traversals. The bound below
includes this conservative choice. Direct leftover axes similarly cost
O(Nw) each, with O(Nw) reusable history if needed.

The original lifted prefixes have width W+O(r): a pair increases maximum
component magnitude by at most a fixed factor plus a constant. Over r
stages this adds O(r) bits. Within a split block the wide term and narrow
term each need only O(k) additional bits. Choose w and p once with this
margin. Do not recompute the plan from an intermediate value's bit length.

## 5. Complete time and space

There are

    B=K ceil(m/d) <= r/d+K

fast blocks, and their ranks k_i satisfy sum k_i<=r and k_i<=d. Therefore
sum k_i^2<=rd. The complete bound, including scans, splits, protected
copies, both orientations, histories and direct tails, is

    T=O(Nw(r/d+K)d^sigma + Nrd + Nw(ell+K)) + F.

Polynomial header/plan preparation fits the exponentially large N and
long-record allowance. Keep it in the construction; do not create a
data-dependent table for the address permutation that this algorithm avoids.
At w,p=Theta(r), the exact powers of r, excluding N, are

| Charge | Power |
| --- | ---: |
| Full fast groups | 2-epsilon*(1-sigma)=1199003/600000 |
| Short-group allowance | 1+epsilon*(spacing+sigma)=5991997/3000000 |
| Narrow lifts | 1+epsilon=1997/1000 |
| Deferred record axes | 2-epsilon=1003/1000 |
| Incomplete-chunk axes | 1+epsilon*spacing=500997/500000 |

The first power strictly exceeds the others and is below two by
997/600000. This proves the stated time bound. In particular, an added
O(Nwr) dense-position shuffle would destroy this result; the permanent
suffix and declared order remove the need for that operation.

Sequential calls reuse history. The full additional-space ledger is

    O(Nw + Nw d^sigma + Nd^2) + F.

The three terms cover live copies, wide history and conservative narrow
history, respectively. Since

    2 epsilon < 1+epsilon sigma,

the wide history dominates at linear precision, giving the space bound
in section 1. I do not carry B histories concurrently. A future native
collector must host this clean space or prove a different implementation;
the standalone theorem supplies no free dirty-helper conversion.

## 6. Error and evidence boundaries

For one forward pair with difference a-b=u+iv, the deviation from its
ideal C pair is the same at both outputs:

    ((v mod 2)-(u mod 2))*(1-i)/2.

Its squared norm across the two outputs is at most one. The inverse has
the same bound. A stage on N entries thus has error norm at most sqrt(N/2),
independent of the input magnitude. Propagating these stage errors through
the remaining ideal unitary factors and using the triangle inequality
gives the r sqrt(N/2) bounds. The argument permits any declared axis order.
It does not assert that the new and old nonlinear words agree.

The executable checks use a direct exact linear oracle, not the fast
physical source algorithm. They cover complete ambient arrays, signed
inputs through 257 bits, both orientations, source/split/private cleanup,
the four-oracle invoice, all spectator and coefficient fields, and the
noncommuting-order and insufficient-guard controls. The parameter checker
tests exact finite partitions and rational exponent identities. These
checks corroborate the written construction; they do not measure its
asymptotic tariff or execute a full selected cover.

I leave PR2287's inherited refinement premises explicit. I have not
supplied a new selected supplier, external wrapper bill, linear-space
backend, dirty hosting, full multiplication theorem or improved kappa.
The result changes the standalone lifting-core bound and the backend
contract available to later consumer work.
