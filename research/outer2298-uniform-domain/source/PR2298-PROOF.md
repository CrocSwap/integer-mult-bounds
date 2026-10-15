# Conservative outer transfer for the selected callees

We give a complete outer caller for two pending selected constructions:
PR2234 at `d047ef86fbc5b1614d3d8e2b8d3441413beab73f` and PR2287 at
`8c60765b5dea9d862b3b190d55da102a576031bf`. We retain the original
FFT, Gaussian, packing and recovery arguments in source sections 06–08,
and Douglas Colkitt's nonadjacent-axis schedule. We instantiate their
interfaces below; we do not claim those inherited methods as new.

**Transfer theorem.** Under the completed ordinary-interchange and
complex-layer construction contracts specified in section 1, the caller
multiplies two n-bit binary integers in a fixed multitape model in

    O(n (log n)^(1-1/20000000))

time, with exact 2n-bit output, including leading zeros. We use published
analytic algorithms as described in section 5. The pending selected
callee proofs still require independent review. This is a proposed
composition, not an independently verified unconditional multiplication
theorem or a replacement selected frontier. In particular, our finite
tests do not execute the enormous recursive suppliers or Gaussian maps.

## 1. Callee admission and the dimension extension

PR2234 supplies ordinary interchange of two complete E-bit fields in
`O(V E^tau)` time, where `tau=99830289/100000000`. The caller may supply
arbitrary complete preceding, intervening and following fields and
arbitrary payload. The callee preserves payload, restores spectators,
clears work and returns its heads. V is the complete logical bit volume.
For E=0 we use the identity. We use the elementary linear-time bit move
for a one-bit difference between field widths. We do not expose a weighted
or radix-q internal operation to this outer caller.

PR2287 proposes an exact complex C tensor, its normalized H0 tensor,
and an optional final p-grid truncation, with

    H0 = [[1,1],[1,-1]]/2,   cost O(V d^lambdaPrime),
    lambdaPrime=599/600, c=1/500, K=floor(d^c).

Its literal statement fixes dimension exponent 997/1000. We need a
separate extension to `epsilon=1/40`, not an invocation of that statement
with different inputs. We retain its algorithm, finite words, row reserve,
proper-width induction, global compact parameters and one root grid.
We replace only `d=floor(p^(997/1000))` by `d=floor(p^(1/40))`.

In that proof the dimension exponent enters through these conditions:

    d=Theta(p^epsilon),  1-epsilon(1+c)>0,
    1-epsilon>0,        epsilon*c>0.

For our choice the three gaps are `19499/20000`, `39/40` and `1/20000`.
The new long-record range `r=2^Theta(p/d)` still exceeds every fixed
polynomial in p. The guard `Delta=2^210000*d` is still o(p). The row
reserve has O(log d) selected axes; the compact reserve has
`O(d^(1-c) log p)` selected axes. Neither changes its exponent or constant
when we lower epsilon. We keep the selected axes at the same offset in
consecutive K-bit chunks and retain complete spectators.

The internal, leaf and reservation exponents in PR2287 remain

    99832997289/10^11, 99833167/10^8, 499/500,

each below `lambda=249583/250000<lambdaPrime`. Their moment, row and
precision inductions contain no additional epsilon-dependent step.
The same log-absorption proof therefore proves the extended layer
contract, with a different fixed cutoff. For a bounded initial range
we use elementary kernels and enlarge its fixed time constant.

At a layer entrance we use p-grid Gaussian values of modulus at most one,
O(p)-bit components, D<=d selected axes and an O(p)-bit descriptor. At
return we remove guard and padded row fields only after their complete
restoration and write `Q_p(H0^tensor-D z)`. Its error is less than
`sqrt(2)*2^-p`; it preserves the disk. This conclusion uses the completed
normalized layer, not a contraction estimate on individual internal gates.

## 2. A uniform input and prime box

For sufficiently large n define

    b=ceil(log2 n), p=6b, d=floor(p^(1/40)), K=floor(d^(1/500)),
    4n/b <= T < 8n/b, T a power of two,
    ell=ceil(log2(T)/d), r=2^ell.

Choose `d*ell-log2(T)` axes of length r/2 and the rest of length r.
Their product is T, and we choose the last axis to have length r. For
large n, `b/2<=log2(T)<=b` and `d<=b`, so

    p/(12d)<=ell<=p/(3d), d*ell<=p/3,
    Tp=Theta(n), d=Theta(p^(1/40)), r=2^Theta(p/d), r<2^p.

Consequently `K=o(ell)`, `K/log p` tends to infinity and the exact-K
layer domain holds. We use the supplied d, not the older `floor(b^epsilon)`
choice. A fixed cutoff includes `p>=2^40`, which ensures d>=2.
For b>=3, `(6b)^3<=b^10`, hence `d<=b^(1/12)`.

Put `alpha=ceil((12d^2 b)^(1/4))`, `gamma=2d alpha^2` and `eta=1/(4d)`.
The elementary ceiling bounds give

    alpha<=2(12d^2 b)^(1/4),
    gamma<28d^2 sqrt(b)<32b^(11/20).

For the last inequality use `6^(1/20)<8/7`, which follows by taking
twentieth powers. Thus `2<=alpha<sqrt(p)` and `gamma<=b/4` eventually.
The source's convenient b>=2^24 recovery threshold also has enough room
for the last gamma bound. We retain separate layer and prime thresholds.

For each target length t_i choose a distinct odd prime satisfying

    (1-2eta)t_i < s_i <= (1-eta)t_i.

Harvey–van der Hoeven's Lemma 5.1 supplies at least
`eta*x/(2 log x)` primes in this interval when `x>exp(2/eta)`.
Here `log(r/2)/d=Theta(p^(19/20))` tends to infinity, and each interval
eventually contains more than d primes. The r/2 and r intervals are
disjoint. We need no short-interval prime theorem. Trial division over
both intervals costs `O(d r^(3/2) poly(p))=n^o(1)` and generates the
primes without advice.

Write S=product(s_i). Strict Bernoulli gives `T/2<S<T`. Each
`theta_i=t_i/s_i-1>1/(4d)`, so `alpha^4 theta_i>3db>=p`.
Also `gcd(s_i,t_i)=1` and `t_i<2^p`. These are the complete domain
conditions of the original one-dimensional Gaussian interface.

For q=ceil(n/b), the input radix polynomials have degree q-1, with
digits in `[0,2^b)`. Their product degree is at most
`2q-2<2n/b<=T/2<S`; cyclic wraparound cannot affect them. Each integer
coefficient is nonnegative and less than `q*2^(2b)<=2^(3b)`.
The machine counts n, computes fixed integer roots, writes descriptors
and finds primes using the source's deterministic setup. A finite initial
range uses schoolbook multiplication. One fixed machine handles both ranges.

## 3. Complete coordinate layouts

For the prime-box map put `P_i=product_(j<i) s_j`,
`mu_i=P_i^-1 mod s_i`, and write an ordinary index as `k=sum a_i P_i`.
The algebra isomorphism `Phi(x)=product x_i^mu_i` sends it to

    b_i=a_i+mu_i sum_(j<i) a_j P_j mod s_i.

Embed the stream in the full dyadic box in `(a_d,...,a_1)` order, with
zeros at invalid coordinates. Reverse the axis order by at most floor(d/2)
nonadjacent endpoint exchanges. Apply the triangular shifts in decreasing
i, so lower controls still hold their original digits. A shift rotates
only `[0,s_i)` and fixes padding; if a lower control is invalid, use the
identity. Validity and zero padding survive each complete update. Inverse
updates use increasing i and then restore the original axis order.

For a nonadjacent pair with one extra bit use

    e x G y -> e y G x -> y G e x,
    x G e y -> e x G y -> e y G x.

Each line uses one completed equal-width interchange and one elementary
bit move. G includes the complete intervening fields. Thus a reversal
costs `O(V d(1+ell^tau))`. Prefix-controlled rotations cost O(dV);
polynomial offset setup per prefix costs `O(dT poly(p)/r)=o(V)`.
For Gaussian axis exposure, exchange that axis with the innermost field,
process its lines, then reverse the same exchange. We retain the source
axis order and truncations, using at most 2(d-1) exchanges per tensor map.
Each inverse uses its actual payload width, which remains O(p).

For synthetic transforms we use the original exact-K positional layout L
in source06. Move the extra top bits and at most K-1 bottom levels to a
prefix, then transpose the equal K-bit chunks to group-major order. This
costs `O(V[dK+p K^(tau-1)])`. The polynomial coefficient suffix remains
contiguous. A round's selected bits have one common offset in D=d-1
consecutive K-bit chunks, with complete preceding/following fields and
total address length at most d*ell=O(p). The header has O(p) bits.
The extended layer therefore accepts each call. The separate named-slot
table has polynomial size and fits the long-record setup charge.

We compute prefix rounds with exact elementary H0 kernels and one final
truncation. We process common rounds with the extended selected layer.
For a round at named level h, the monomial exponent is

    E=-sum_i (2r/2^(h+1))*b_i*k_i mod 2r,
    k_i=sum_(v<h) 2^v x_(i,v).

The machine reads named slots, not the low bits of the current physical
address. It applies the signed two-piece coefficient rotation y^E in
`C[y]/(y^r+1)`. In the opposite direction it applies y^-E before H0.
The completed exact operators are `L B F^-` and `F^+ B^-1 L^-1`, where
B reverses frequency bits within each named axis. Both normalized
transforms divide by M=product_(i<d) t_i; their composite is I/M.
Signed monomials commute with component truncation. Each of at most ell
completed rounds is a contraction, giving error `<sqrt(2)*ell*2^-p`.

## 4. Signed ring products and storage boundaries

Use signed, most-significant-bit-first component words of width w=p+2,
real before imaginary, with coefficient indices increasing. The last
scalar axis already has r entries; grouping it as a polynomial record
changes only its descriptor. We do not transpose or copy that payload.

Write `f=2^-p(a+ib)` and `g=2^-p(c+ie)`. For each real numerator
polynomial use base `B0=2^(4p)` and evaluate at B0. A left-to-right scan
in increasing coefficient order maintains the signed packing carry
in {-1,0}. It writes one B0 block per coefficient, then converts the
fixed-width two's-complement result to sign/magnitude if needed.
Four calls to the established O(N log N) integer multiplier produce
ac, be, ae and bc evaluations. Their inputs have O(rp) bits.

Each ordinary product coefficient has modulus at most
`r*2^(2p)<2^(3p)<B0/2`. Read the product's 2r unsigned blocks q_j with
sign extension epsilon in {-1,0}. Start rho_0=0, extract the centered
residue of q_j+rho_j, and set

    rho_(j+1)=(q_j+rho_j-h_j)/B0.

The carry lies in {0,1}. After extracting the padded final zero
coefficient, `rho_(2r)+epsilon=0`. This sign-extension identity is
essential for negative products. The scan recovers the complete ordinary
products, then forms ac-be and ae+bc and subtracts upper halves from lower
halves for the negacyclic wrap. Each output numerator is a sum of r signed
Gaussian products, so its modulus is at most r*2^(2p).

Shift absolute component magnitudes right by p+ell, restore signs and
write width-w words. This returns exactly `Q_p(fg/r)`, remains in the
disk and adds less than `sqrt(2)*2^-p` error. Packing, extraction and
conversion cost O(rp); four short integer products cost O(rp log(rp)).
Their established multiplier does not call the proposed faster algorithm.

Multiply corresponding forward records in their common LB order, apply
the opposite transform, then scale by M exactly. The result approximates
the normalized ring convolution `(f*g)/(rM)` with error
`<sqrt(2)*M*(3ell+1)*2^-p`. We widen words to `w+log2 M` for that scale.
We remove leading sign-extension bits only after proving the returned
disk margin, as below. We never silently reinterpret widened words as
width w.

## 5. Published Gaussian maps and retained permutations

We use Harvey and van der Hoeven's author-hosted 45-page manuscript,
Theorem1.1, Lemma2.12, Theorem4.2, and Lemmas4.6,4.8,4.9,4.12,5.1.
We checked their displayed domains against the caller above. Their
normalized Gaussian routines return disk-grid vectors, with errors
16p, 4 and 3p^2/4 in units of 2^-p. Source07 gives value-preserving
record adapters and charges the sequential windows, iterates and resets.
We retain those published scalar algorithms and their error analysis;
we have not reimplemented them here.

For one axis, put `(P_s u)_j=u_(tj)` and `(P_t v)_k=v_(-sk)`.
Source07 composes the published normalized maps as

    P_s F_s = 2^(2 alpha^2) B0 P_t F_t A,

with A and B0 contractions, disk-grid error <p^2, and line cost
`O(t p^(3/2+delta) alpha)`, delta=1/16. The two coordinate permutations
remain in the formula. Removing their sorting operations does not remove
either their algebraic action or any scalar routine. Increasing-coordinate
selection is an ordered subsequence; the nearest indices use a carry
counter. The source's constant-tape adapters add O(tp) work.

Tensor the maps in the original axis-processing order, keeping the full
padded box and writing zeros on invalid lines. The tensor error is <d p^2,
and the arithmetic cost is `O(d T p^(3/2+delta) alpha)`. Section3 pays
all line exposure/restoration. A contraction controls the sup error on
all parallel lines without multiplying it by their number.

Let R=tensor P_s and Q=tensor P_t. For
`a_j=exp(-pi*i*sum s_i*j_i^2/t_i)`, even target lengths give periodic
chirps and

    Q F_t x = conjugate(a) * [a convolve (conjugate(a)*x)] / T.

The coefficient identity follows from
`j_i^2-(j_i-k_i)^2+k_i^2=2j_i k_i`. The cyclic scalar convolution uses
the ring convolution in section4: twist its last coordinate by
`zeta^k`, zeta=exp(pi*i/r), and untwist afterward. Since
`zeta^(j+hr)*(-1)^h=zeta^j`, the twist cancels the negacyclic sign.
We approximate each phase in the disk grid and charge its short product.
Generating chirps costs O(T d p^(1+delta)), including the axis descriptors.

For an input of norm at most 1/2, the complete source transform has exact
counterpart `R F_s=2^gamma B0 Q F_t A`. We obtain its opposite-sign
version by conjugating input and output. The retained dilation satisfies
`F^+ R_c=R_(c^-1) F^+`, so the three source transforms and pointwise
product give `(u*v)/S^2`. We preserve both factors of S in recovery.

## 6. Disk margins, errors and exact recovery

Set h=2^-p and L=log2 T. For eventual d>=2 and ell, the synthetic
transform error is <Lh. The normalized ring convolution error is
`E_ring*h`, with `E_ring=M(3L+2)<5TL`. A computed unit-phase product
does not increase the operand's norm and has error <4h.

If one scalar convolution operand has norm <=.7, the ring output after
scaling has norm <.701 for a fixed large enough cutoff. This justifies
its exact width reduction from w+log2 M to w. The two input twists and
output untwist give scalar convolution error <6TLh. A chirp input of
norm <=.6 therefore gives a legal disk output and error <8TLh.

For a source-transform input of norm <=.5, expansion has norm <.51.
After chirp and compression, the error before rescaling is
`<(2d p^2+8TL)h`. Scaling by 2^gamma gives error <E_s h, where
`E_s=9*2^gamma*T*L`, since `2d p^2<TL` eventually. The exact source
map is a contraction; the returned norm is <.501. We widen words by
gamma bits for scaling and remove only redundant sign bits afterward.

Scale each input radix digit by `2^(-b-2)`, giving exact p-grid inputs
u,v of norm <1/4. The computed source transforms have norm <.26.
Their truncated pointwise product z has norm <.26^2<.5, hence the
opposite source call is admissible. The product error is <(2E_s+2)h;
the opposite adds E_s h. After the first exact S scale we approximate
`(u*v)/S` with error `<28*2^gamma*T^2*L*h` and norm <1.

The second exact scale `2^(2b+4)*S` restores integer coefficients.
With p=6b, S<T<2^b, L<b and gamma<=b/4, its error is

    <448 b 2^(-b+gamma) <=448 b 2^(-3b/4) <1/2.

All earlier disk margins hold beyond the same fixed cutoff. Round the
real component to the unique nearest integer. The output is the exact
nonnegative coefficient, below 2^(3b); write it in 3b+1 signed bits.
Apply Phi^-1 at that payload width before propagating carries.

For radix Q0=2^b, use `k_0=0`,
`digit_j=(c_j+k_j) mod Q0`, `k_(j+1)=floor((c_j+k_j)/Q0)`.
Induction gives `0<=k_j<=q(Q0-1)<Q0^2` and

    sum_(h<j) c_h Q0^h = sum_(h<j) digit_h Q0^h + k_j Q0^j.

One O(b)-work scan per coefficient recovers the product digits. Drain
the final carry, reverse the bit stream once and retain exactly 2n bits.
The product bound makes discarded high padding zero, including zero
inputs. The two S scales use widths w+b then w+4b+4, as in source08;
these are O(p), and no intermediate scale loses a significant bit.

## 7. Paid costs and strict absorption

Divide costs by V=Tp=Theta(n). We charge the same complete streams after
each call, include inverse layouts, and reuse a fixed number of tapes.
The seven exponents and their positive savings are

| Work | Exponent | Saving |
|---|---|---|
| Prefix moves and elementary rounds | epsilon(1+c) | 19499/20000 |
| Exact-K chunk transposition | 1-epsilon*c*(1-tau) | 169711/2000000000000 |
| Parallel normalized rounds | 1-epsilon*(1-lambdaPrime) | 1/24000 |
| Nonadjacent CRT and line exposure | tau+epsilon*(1-tau) | 6618729/4000000000 |
| Original Gaussian line arithmetic | 3/4+delta+3epsilon/2 | 3/20 |
| Chirps, scalar products and descriptors | epsilon+delta | 73/80 |
| Short polynomial products | 1-epsilon | 1/40 |

The minimum is `169711/2000000000000`. Our target
`kappa=1/20000000` leaves strict gap `69711/2000000000000`.
We need positivity of this gap, not the older sufficient 2*kappa
margin. Fixed powers of log p fit this gap. The term log(rp) also
contains log p, which fits its own positive gap. Setup n^o(1), linear
record conversions and all finite cutoff cases fit the same bound.

The old adjacent-axis d^2 bill would fail this parameter choice. We use
the concrete schedule in section3, not a numerical replacement of its
cost. We have also retained the exact-K prefix and transposition terms;
we claim no balanced-width or modern global-router saving.

## 8. Evidence and remaining review

Our code checks the changed dimension/format admission, exact cost gaps,
signed packing and sign-extension boundary, truncation at complete
synthetic rounds, common retained layout, convolution normalization,
CRT/carry recovery and explicit fault controls. We reuse Philipp's
authenticated physical-layout model and credit its existing scope.
Its indexed record permutations and our small arithmetic executions
are interface experiments, not a timing simulation of a fixed-tape
machine or execution of the selected large supplier.

The all-size conclusion rests on the written composition, the pending
selected callee proofs and the stated published analytic algorithms.
An independent reviewer should check section1's dimension extension,
the complete-field contracts at section3, and the format/error boundaries
in sections4–6. We have not run a new formal proof or an end-to-end
Gaussian multiplication program. We leave the selected result unchanged.
