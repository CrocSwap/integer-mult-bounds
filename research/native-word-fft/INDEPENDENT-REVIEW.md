# Independent arithmetic review

Read-only review by the arithmetic worker for the current native Word RAM
campaign. Prepared with OpenAI Codex assistance. This is an informal mathematical
review of current source bytes, not a Lean or human peer-review certificate.

## Root seed: accepted within its stated model

Inspected `recovery/root_seed.py` and `recovery/ROOTS-RECOVERY.md` directly.
The construction uses bounded signed magnitudes, fixed-point integer arithmetic,
Machin's identity and a finite Taylor loop. Decimal appears only in the separate
validation routine; it is not called by `root_seed`.

The following all-parameter points were checked independently:

1. With P=8(p+16), stopping the alternating arctangent sum when the next
   q^(2j+1) exceeds S=2^P gives omitted tail <1/S. There are at most P+1
   retained terms. Floors add at most one scaled unit per retained term.
   The Machin combination therefore has error at most 20(P+2)/S.
2. The integer angle floor(2*A/D) differs from 2*pi/D by at most
   [40(P+2)+1]/S. It lies in [0,8] after scaling, including D=1.
3. The term recurrence uses the old real and imaginary coordinates in both
   numerators before assigning the new pair; no sequential-update error occurs.
   Its coordinate error recurrence is E_k <= (8/k)E_(k-1)+1/S. Unfolding it
   and using j!/k! <= 1/(k-j)! gives E_k < exp(8)/S <4096/S.
4. For K=128(p+1), the omitted Taylor tail is at most
   2*8^(K+1)/(K+1)!, bounded by 2^(-K/2-3). The last K/2+1 factorial
   factors are at least 128. The inequality 2^(-K/2-3)<=32/2^P holds for
   every p>=1; p=1 is the limiting equality in this last comparison.
5. The printed internal error numerator simplifies exactly to
   524608*p+529521. For p>=1 this is <2^21*p. Since p<=2^p,
   its product with 2^(p+1) is <2^(2p+22)<2^(8p+128). Thus the final
   nearest-p-bit rounding proves strict coordinate error <2^-p for every p,
   not just for the finite p fixtures.
6. Machin denominators have at most P+O(log P) bits and its next power is
   at most 239^2*S. Taylor values are bounded by a fixed multiple of S;
   the stated 2P+20 physical word width covers the 2P+17 product envelope,
   denominators, accumulators and rounding. D must also fit, as stated.
7. Both arctangent loops have O(P) iterations and the Taylor loop has K=O(p)
   iterations, each using a constant number of bounded-word MUL/DIV and
   ordinary operations. Therefore O(p) setup is justified in the declared
   unit-cost logarithmic-word model. It is not a claim about bit operations.

The same physical word width must be used by the whole caller. A private wider
seed word model cannot be hidden inside a narrower FFT model. With p=Theta(log n)
and D polynomial in n, the explicit seed width is still Theta(log n), though
its constant is intentionally large.

## Native FFT: accepted within its stated operational-model scope

Read the actual `root/native_fft.py`, its current root seed, and the integrated
`FFT-ERROR.md`. The executable now includes the separate 65,535-bit extremal
fixture. This review does not relabel its operational model as an emitted
RamStd program or formal compiler certificate.

### Correctness and numerical sufficiency

The bit-reversal permutation and iterative radix-two loops use ordinary
unnormalized forward transforms with negative exponent and inverse with positive
exponent. Twiddles are prepared from the positive primitive root and conjugated
for forward calls. Root indices k*(N/step) lie below N/2, so the prepared table
contains every requested value. Three transforms and one pointwise multiplication
compute the zero-padded ordinary convolution when N>=2L.

I independently checked the integrated FFT-ERROR.md recurrences. With its
coordinate-to-complex error conversion, the one-transform error bound
36*N^3*beta/S, pointwise error 112*N^5*beta^2/S, and normalized final error
216*N^6*beta^2/S are conservative valid envelopes. The use of approximate
rather than exact second-input amplitude in the twiddle perturbation term is
correct. Its closed larger envelope and the substituted F=24*ell+64 prove a
strict error below 1/4 for every n>=1. The seed/table error supplies the stated
twiddle hypothesis; rounded complex arithmetic supplies the local error.

For an additional independent route, use complex error tau<=16*N/S for the
successively generated twiddles and local error <=2/S. A transform with ideal
input magnitude X and input error E has output error at most

    N^2*E + N^3*tau*X + 2*N^2/S.

This follows from per-stage error <=3E+tau*N*X+2/S and 3^log2(N)<=N^2.
It yields forward error <=18*N^4*beta/S, pointwise error
<=56*N^5*beta^2/S, and normalized final error <=76*N^6*beta^2/S.
The forward-error assumption <=N*beta used here is implied by the chosen F.
Since N<4n<2^(ell+2) and beta<=2^ell, even this separate final bound is
less than 2^(8ell+19-F)<1/4.

Consequently the runtime separation checks are backed by a universal error
proof; checking proximity to some integer alone would not have been enough.
They do not abort on valid inputs. The nearest integer is the exact convolution
coefficient, the high zero convolution coefficients really vanish, and the
subsequent carry loop and output high-padding checks are justified.

### Word bounds and operation model

Every MUL in `multiply` is on bounded word data: four fixed-point coordinate
products in complex multiplication, limb/scale products, or polynomially bounded
index/range arithmetic. The independent unbounded product x*y appears only in
`check`, never in the algorithm. Padding by scale can equivalently be a left
shift. Powers of two used for normalization and carry can be shifts/masks;
ordinary bounded-word DIV is permitted by the declared model in any case.

A crude actual inverse-prefix amplitude bound is 6*N^6*beta^2. Transform
products and combined real/imaginary sums thus have magnitude width at most
2F+6*ceil(log2 N)+2b+8. Pointwise forward products fit that same bound.
This is covered by the single global width 16*(F+16)+20, which also covers
the root seed's larger working precision. Integer counters, indices, polynomial
coefficient-range bounds, array lengths and fixed-table pointers fit too.

`Words.limit`, overflow diagnostics, Python containers and the independent
reference are model/checking machinery, not an assertion that the emitted
machine stores an unbounded integer or obtains transcendental constants.
The universal bounds justify removing overflow checks in a future machine
lowering. Literal `charged_word_operations` are displayed operational-model
charges, not an exact count from an emitted instruction stream.

### Direct cost and scope

With b=max(1,floor(ell/8)), L=ceil(n/b) and N the least power of two at least
2L, we have L=Theta(n/log(n+2)), N=Theta(L), and log N=O(log n).
Bit reversal uses O(N) aggregate mask flips. Three transforms cost O(N log N)
word work; root preparation O(F), root-table recurrence O(N), padding,
pointwise products, recovery, carry and packed IO cost O(N+L). Thus the whole
direct native algorithm costs O(n), with every preparation and IO stage paid.
It uses neither TM simulation nor a TM multiplication antecedent.

This is a complete positive native arithmetic baseline, not a new best-known
asymptotic exponent: the cited log-RAM literature already contains O(n)
algorithms. The separate stable-native-provider and phase-table lemmas do not
by themselves establish a stronger all-length cyclic transform or new kappa.
An actual stronger provider still needs its own quantitative full-conditioning,
preparation, depth, and caller-boundary admission.

## Reviewed byte identities

- `root_seed.py` (recovery): `9b323f84ade7decfa6152dd4385e90ec43b56087927ac23ad4ef73ae4d5d3042`
- `native_fft.py` (root): `83bff7591e4ffa36fe3713f9d639de6ed1edc715d3698bc6d2d0dc3b90146cc5`
- `root_seed.py` (root): `9b323f84ade7decfa6152dd4385e90ec43b56087927ac23ad4ef73ae4d5d3042`
- `FFT-ERROR.md` (native-word-fft): `ca426930df5c449ca8ce432360ba3ac80f12377bcd9a058ad16387d8ad87bef5`
