# Exact FFT word multiplication

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
I give a fixed-tape implementation of the classical radix-digit/FFT
reduction, using the complete normalized product from corrected PR3709.
I retain its numerical proof and source notices. I distinguish the
all-size argument below from the finite checks in EVIDENCE.md.

## Contract and dependency

The caller supplies two canonical nonnegative Count magnitudes a and b,
at their origin heads, and a canonical positive width n. I require
`0<=a,b<2^n`. The borrowed tapes must lie outside the owner's scratch and
child roles. The two magnitude ports may alias each other. I return
exactly 2n raw LSB-first bits for ab, including high zero bits, and
restore the borrowed values and origin heads.

The caller must consume the protected output before reuse. I expose the
`closed`, `pool`, `output` and `canonical` ownership interface used by
the retained signed arithmetic consumer. I erase owned scratch and
consume child returns before completing a legal call.

I use a fixed small-word cutoff of 16 by default. The constructor can
compile another fixed cutoff at least two; it is a program constant,
not an input-dependent parameter. Below that cutoff I call the retained
WordProduct. Above it I call RingProduct, whose internal multiplier
remains the original Karatsuba WordProduct. The dependency is acyclic.
In particular, I do not install FftWord inside its own RingProduct child.

The word theorem uses PR3709's normalized-product proof and the elementary
tape codecs. I make no call to a T74 supplier, a full synthetic Fourier
transform or an HH integer-multiplication oracle in this word algorithm.

## Encoded geometry and packing

For the FFT branch, let

    beta=ceil(log2 n), B=2^beta, q=ceil(n/beta),
    r=2^ell, ell=ceil(log2(2q)), p0=2beta+ell.

The default branch has n>16, so beta>=1 and the divisions are defined.
The same formulas work above any fixed cutoff at least two. I have
`2q<=r<4q`, `r*beta>=2n` and `1<=ell<p0`. I compute the geometry with
encoded logarithms, division, shifts and addition in `fft_word_plan.py`.

Write the input as radix-B digits a_i and b_i for 0<=i<q, padding the
last partial digit with zeroes. Define

    f(X)=sum_i (a_i/B) X^i,  g(X)=sum_i (b_i/B) X^i.

I encode a_i/B on the p0 grid with numerator `a_i*2^(p0-beta)`.
Each coefficient lies in the unit disk. I pad both polynomials through
r coefficients, append a complete zero second record, and call the
retained product with A=1 and C=1. These parameters satisfy its complete
two-record packet contract.

In `fft_word_codec.pack`, I read the canonical magnitude once. For each
digit I append beta+ell low zeroes, its next beta bits, and two high
zeroes to the real component; I append p0+2 imaginary zeroes. After
RIGHT I supply zero bits without moving past the canonical end. I then
append the remaining zero coefficients and second record. The fit check
ensures that q digits exhaust the input. I avoid growing-offset slices
and repeated division of the full input magnitude.

I preserve the source head by rewinding only after the complete packing
scan. Each input costs O(n+r*p0) bit operations and O(r*p0) output cells.
The initial fit scan adds O(n) work.

## Exact coefficient recovery

The ordinary product degree is at most `2q-2<r`. Consequently I incur
no negacyclic wrap in the retained ring product. Put

    c_i=sum_(j+k=i) a_j*b_k.

Since `2^p0=r*B^2`, the exact normalized product has coefficient

    (fg/r)_i = c_i/(r*B^2) = c_i/2^p0.

It already lies on the p0 grid. PR3709's exact endpoint
`Q_p0(fg/r)` therefore returns c_i as its real integer numerator and
zero as its imaginary numerator. I apply no additional numerical scale
or truncation to those returned numerators.

For headroom,

    0<=c_i<=q(B-1)^2<qB^2<=rB^2/2=2^(p0-1).

The signed p0+2-bit return has ample room. I check nonnegative real
coefficients, zero imaginary parts and this strict coefficient bound
before carrying. I also check the complete zero second record and the
final packet extent.

## Carries and fixed output length

I initialize K_0=0 and scan the first record in increasing coefficient
order. For each coefficient I compute

    z_i=c_i+K_i,
    d_i=z_i mod B,
    K_(i+1)=floor(z_i/B).

The identity `c_i+K_i=d_i+B*K_(i+1)` proves the usual radix-carry
invariant. Moreover, if `K_i<=q(B-1)`, then

    K_(i+1) <= floor((q(B-1)^2+q(B-1))/B) = q(B-1).

Thus each local carry has O(log n) bits. In `unpack`, I scan the low
beta bits of the owned local total and obtain the next carry with one
linear right shift of that total. I never shift the original n-bit
operand during this pass.

After r coefficients the carry is zero: the product is below
`B^(2q)<=B^r`. I use an encoded counter to emit exactly the first 2n
bits. Since `ab<2^(2n)` and `r*beta>=2n`, the remaining padding bits
are zero; I check them rather than discarding them unchecked. I require
both a finished output counter and zero final carry.

The returned word is therefore exactly ab with the declared 2n-bit
extent. The carry and output passes cost O(r*p0)=O(n). The small-word
branch has the same endpoint by the retained WordProduct proof.

I include encoded loop control in that linear charge. The retained
Counter stores `finished` as a boolean and decrements only its trailing
zero prefix before rewinding that prefix. Across a countdown from N,
the ripple lengths sum to `2N-popcount(N)`. Construction and cleanup
add O(log(N+1)). The retained `indices(N)` also increments one mutable
index by its low-bit ripple; I neither retain nor close that yielded
index. Repeating `indices(beta)` across r digits costs
`O(r*(beta+log(beta+1)))=O(n)`. Each local addition and right shift
uses O(p0+beta) work. I perform no full-width count copy or comparison
per emitted bit.

## Complete time and space

For n above the fixed cutoff, beta=Theta(log(n+2)),
`q=O(n/beta)`, `r=O(n/beta)`, and `p0=O(beta)`.
I use the general PR3709 product invoice with A=C=1, retaining its
unamortized setup:

    O(r(ell+1)p0^(8/5) + r*p0^3 + p0^3).

The first term is O(n*beta^(8/5)). The twiddle term is O(n*beta^2),
and the global metadata term is O(beta^3). Packing, validation, exact
carries, copying the protected result and cleanup add O(n).
I obtain

    time = O(n log2(n+2)^2),  space = O(n).

This estimate does not assume A=Theta(p0). I pay the setup term directly
in the scalar call. For an elementary bound, n>=3 gives
`r<8n/beta`, `ell+1<=2beta`, `p0<=4beta` and beta<=n. Replacing the
8/5 scalar power by the larger quadratic power bounds the three terms
by `256n beta^2`, `512n beta^2` and `64n beta^2`, respectively, up to
the retained implementation constants. The finitely many small widths
fit the same asymptotic bound with a constant depending on the fixed
cutoff.

I keep two packed operands, the protected result, a constant number of
inherited packet buffers and O(log n)-bit carry/geometry records. Since
`r*(p0+2)=O(n)`, these occupy O(n) cells. I include the retained word
stack and twiddle workspace in that bound. The number of tape roles is
fixed. During reuse the host backing arrays retain their largest prior
blank extent; their high-water storage is O(max n over those calls).
I clear bodies and restore heads before each return. Diagnostic host
counters do not select operations and can be omitted from the program.

## Consequence for the Gaussian arithmetic allowance

For any fixed delta>0, `log2(n+2)^2=O(n^delta)`. One explicit argument
for 0<delta<=1 uses `ln(2)>=1/2`, `n+2<=3n` and
`exp(u)>=u^2/2`. It gives

    log2(n+2)^2 <= 24 delta^(-2) n^delta,  n>=1.

Thus this concrete word primitive supplies an O(n^(1+delta))
allowance for each fixed delta, including the retained delta=.0001.

The pinned bulk Gaussian reports use scalar p-bit products and four
packed Toeplitz convolutions per local inverse application. Their cell
length is at most 4d+1<=5p in the intended range, so the packed integer
width is O(L_cell*p). I can charge such a product at
`O(L_cell*p*log2(p+2)^2)` with this adapter. I preserve the report's
separate coefficient, layout, factor-page and restoration obligations.

The w^2 scalar boundary term alone, with direct p^(8/5) multiplication,
would have normalized power `8/5-rho=1.598` at rho=.002. I use that
term as a failure screen; direct multiplication of the larger packed
cells can cost more. With the new word primitive, the report's arithmetic
schedule has powers epsilon and 1-rho, up to logarithms. Absorbing those
logs with delta=.0001 gives

    max(epsilon+delta,1-rho+delta)=.9981
      < Phi=.99827619697.

I retain the positive gap .00017619697 as an arithmetic feasibility
result. I have not implemented the Gaussian caller in this package or
verified its complete physical invoice. The selected frontier remains
unchanged.

## Verification and attribution

I execute the default FFT branch at widths 17 and 19, including the
retained signed Arithmetic consumer and a base call between them. I
check codecs separately through 1,024 bits using independent integer
convolution as a boundary fixture; I do not relabel that as a full FFT
execution. I also check large encoded geometry without materializing its
payload, and execute malformed-return and ownership controls.

I credit the standard radix/FFT reduction and Karatsuba algorithm,
corrected PR3709's normalized-product implementation, Mason Hale's
certified interval reference, Dugongue's scalar-ABI precedent and the
retained source notices. The numerical predecessor remains subject to
its separate precision/recovery audit. These are AI-assisted author
checks and an algorithmic proof, not independent human or formal-kernel
verification of the complete multiplication project.
