# Sharp Euclidean bounds inside the dirty Toeplitz shear

This contribution is produced by Nick Petalas. Apache-2.0.

**Claim type: scoped proof with exact finite corroboration.** For the retained
section-2 FFT implementation of a dirty Toeplitz shear, every prefix, suffix,
inverse prefix and inverse suffix has Euclidean operator norm at most

```text
Phi(beta) = (sqrt(beta^2 + 4) + beta)/2,
beta = ||g||_1 + ||h||_1.
```

This holds in every dyadic dimension, including cuts after any subset of a
matching layer's individual gates. The constant is sharp as a function of beta.
It sharpens Jose Manuel's existing dimension-independent `1+beta` envelope
to the optimal constant for these four operators. The improvement is strict
for every beta>0. No new kappa or supplier admission is claimed.

The symbols g,h are the circulant/negacyclic split in Vlado Vojdanovski's
[SHALLOW-TOEPLITZ.md section 2](../unconditional-batched-crt/vendor/SHALLOW-TOEPLITZ.md),
retained by Cinna Davis's Gaussian construction. Brian's
[forward macro-prefix theorem](../triangular-parity-forward-bound/README.md)
explicitly leaves this internal-shear question open. Neither predecessor's
executable is imported or rerun here. Jose Manuel's [rational-unitary-fft/PROOF.md section 5](../rational-unitary-fft/PROOF.md)
already supplies the stronger predecessor envelope `1+M_g+M_h+2v`, including
masked spectral layers and all contiguous segments. That additive unitary/shear
reduction is inherited, not claimed as new here. The contribution is its sharp
constant, optimality and a separate exact matching-subset certificate.

## Precise circuit and theorem

Let m be a positive power of two. The two arbitrary independent data banks
x,y each have m complex coordinates. Put

```text
S(B) = [ I 0 ; B I ],        (x,y) -> (x,y+B x),
T = C(g) + D* C(Dh) D,       D_jj = exp(pi i j/m),
C(v) = F* diag(DFT(v)) F.
```

Here F is the unitary m-point FFT, the star means conjugate transpose,
and DFT is unnormalized. For a Toeplitz first column c and first row r,

```text
g_0 = h_0 = c_0/2,
g_j = (c_j+r_(m-j))/2,       h_j = (c_j-r_(m-j))/2  for 1<=j<m.
```

Apply the circulant shear by F on both banks, disjoint scalar shears
`y_j += DFT(g)_j x_j`, and F*. Apply the second shear by D on both banks,
then the same FFT/shear/inverse-FFT program with symbol Dh, then D*.
The second completed shear is added to the first; both restore the source.

The admissible unitary layers are the ordinary normalized radix-two
butterflies, bit-reversal swaps and unit-modulus diagonal twists. Gates in
a layer act on disjoint wires. Their two banks may execute in any order
inside that layer, including different partial subsets of x and y gates.
All unitary preparation gates for a scalar-shear layer complete before that
layer begins, and that layer completes before unitary unpreparation begins.
This theorem permits cuts inside matching layers, not arbitrary overlaps
between different dependent layers or time inside an atomic gate.

Let P be an executed prefix and Q its remaining suffix, so S(T)=QP.
For every such cut,

```text
max(||P||_2, ||P^-1||_2, ||Q||_2, ||Q^-1||_2) <= Phi(beta).
```

Thus each cut operator has Euclidean condition number at most Phi(beta)^2.
The empty and completed cuts are included. No clean coordinate, discarded
output or source copy is assumed.

## Proof

First use the standard block-shear singular-value calculation. For every
complex square B,

```text
||S(B)||_2 = ||S(B)^-1||_2 = Phi(||B||_2).
```

An SVD of B reduces S(B) by unitary changes of basis to scalar blocks
`[1 0; t 1]`, where t ranges over singular values of B. Their Gram matrices
have characteristic polynomial `lambda^2-(t^2+2)lambda+1`. The square root
of the larger root is Phi(t), which is increasing for t>=0. Negating B
leaves its singular values unchanged. This elementary formula is background;
the application here sharpens the retained cut bound to its optimal constant.

For a scalar-shear mask M with entries zero or one, define

```text
B_g(M) = F* M diag(DFT(g)) F,
B_h(M) = D* F* M diag(DFT(Dh)) F D.
```

Since the diagonal phases and F are unitary, and every Fourier coefficient
is a sum of unit-modulus multiples of symbol coefficients,

```text
||B_g(M)||_2 <= ||g||_1,       ||B_h(M)||_2 <= ||h||_1.
```

The same bounds hold for the complementary masks I-M. In the first scalar
layer put A=B_g(M); in the second put A=C(g)+B_h(M). During a unitary part,
A is the completed spectral sum from the last scalar layer. At every cut
there is a block-diagonal unitary W, with possibly different current unitary
frames on x and y, such that exactly

```text
P = W S(A),              Q = S(T-A) W*,
P^-1 = S(-A) W*,         Q^-1 = W S(A-T).
```

During a partial scalar layer both banks have the same completed Fourier
frame, so conjugating its selected scalar shears gives the displayed masked
component. During a partial unitary layer, left-multiplication changes W only.
The complete unitary preparation/unpreparation pair restores W to I.
These observations prove the first identity gate by gate. The second follows
from Q=S(T)P^-1 and S(B)S(C)=S(B+C); it also gives both inverse identities.
This explicitly handles a partial layer in which only one bank has advanced.

In the first scalar layer A uses a g mask, while T-A is its complementary g
mask plus the whole h component. In the second, A uses the whole g component
plus an h mask, and T-A is the complementary h mask. Before, between and after
scalar layers these descriptions specialize to empty or full masks. Therefore
both ||A||_2 and ||T-A||_2 are at most beta. Unitary invariance, the shear
formula and monotonicity of Phi prove all four bounds in every dimension.

The proof also covers a matching layer whose gates have completed in an
arbitrary subset. Unfinished individual gates are outside the model.

## Improvement, sharpness and the triangular caller

For beta>0, `sqrt(beta^2+4)<beta+2`, hence `Phi(beta)<1+beta`.
At beta=0 both bounds equal 1. Jose Manuel's stored rational unitary program
uses spectral bounds M_g+v and M_h+v. Citing those hypotheses, the same proof
replaces its exact-circuit cut envelope `1+B` by `Phi(B)`, where
`B=M_g+M_h+2v`. This corollary concerns exact execution of stored coefficients;
it does not change or independently verify the predecessor's rounded-data
allocation. No predecessor executable is imported.

For any real beta>=0 take T=beta I_m, hence g=h=(beta/2,0,...,0).
The completed shear has norm Phi(beta), proving the uniform constant cannot
be lowered. The same norm occurs at a proper gate cut just after all scalar
shears in the second Fourier frame and before its unpreparation, when m>=2.
An empty g mask at a proper initial FFT cut makes the remaining suffix attain
the same constant. Inverses have equal norms. At beta=3/2 the norm is exactly
2; the verifier checks an exact Gram eigenvector with eigenvalue 4.

For a lower or upper triangular T, the split has beta equal to its coefficient
l1 norm, since each off-diagonal coefficient is split equally between g and h.
Consequently a triangular dirty shear of coefficient l1 at most eta has all
four internal gate-cut norms at most Phi(eta). At eta=1/2 this is
`(sqrt(17)+1)/4`, a constant independent of m. This statement concerns one
shear starting from its input; ancestors and completed sibling work must
still be composed under the caller's contracts.

## Exact finite evidence and reproduction

From the repository root, with CPython 3.12 and the standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/fft-dirty-shear-cuts/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/fft-dirty-shear-cuts/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fft-dirty-shear-cuts
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fft-dirty-shear-cuts --check-source-history
```

Any CPython 3.12 executable may replace that local path. The direct verifier
is self-contained and writes no files. It constructs normalized FFT
butterflies and twists exactly over Q(zeta_8), never using floating point or
numerical rank. Three fixtures at m=1,2,4 enumerate 12, 56 and 688 cuts respectively,
756 in total. They enumerate every subset of every matching layer, including all independently chosen source/target twist gates.
Each cut checks the prefix and suffix identities; each gate's unitary or
shear contract and every frame restoration and Toeplitz endpoint are checked.
The finite fixtures corroborate the written all-dimension proof.

Controls reject a nonunitary gate, wrong shear direction, overlapping gates
and a nondyadic finite-checker input. Missing negacyclic twists and a wrong
final shear sign change the endpoint. A separate positive control proves the
sharp beta=3/2 singular value and dirty inverse exactly. The generated stdout
receipt binds all five package files by SHA-256. No receipt is handwritten.

The verifier follows bounded loops with m<=4, no recursion and explicit
exceptions that remain active under -O. Managed-runtime allocation is a
Power of Ten deviation confined to these finite matrices and masks; no
unbounded input or subprocess is accepted. Python syntax and warning-strict
execution are the available diagnostics; no external static analyzer is
required. The verifier does not compute numerical spectral norms or infer
a universal theorem from its finite examples.

## Limits

Exact roots, normalized unitary butterflies and the specified phase ordering
are hypotheses. No rounded-root/error budget, internal implementation of an
atomic 2x2 gate, non-Toeplitz generator compiler, all-depth physical caller
composition, fixed-tape bill or complete multiplication theorem is proved.
Independent human and formal proof-kernel review are unclaimed. The selected
frontier remains unchanged.

## Open next questions

1. **Compose this local bound with one literal triangular caller.** This
   would turn the local constant into a full gate-cut guard. First bind the
   caller's ancestor operators and both child schedules to the four macro
   envelopes and this exact shear cut. Rounded gates and coordinatewise
   precision still need their own ledger.
2. **Price rounding of the unitary butterflies and twists.** Exact unitary
   invariance is what removes dimension growth here. First propagate a
   per-gate perturbation through the proved prefix/suffix bound and count
   the actual gates, retaining the dirty source restoration requirement.
   This package supplies neither a rounded implementation nor its cost.

## Sources, overlap and credit

Canonical base is 624de9dc66858af0945e5f8a0942488d62280d43, priority revision 7.
SOURCES.json pins historical guidance and the compiler/question prose as
provenance. None is an executable input to this self-contained verifier.
The selected source-binding positive control passed before the investigation.
[The advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132751)
records this single question and its stopping rule.

A later source search found the already dimension-independent section-5
envelope in Jose Manuel's rational compiler. The
[progress correction](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132834)
records that prior-art refinement explicitly. The exact-root theorem's domain
and sharp bound are unchanged; the additive reduction remains credited to
its predecessor.

The overlap helper's entry snapshot covers 348 open PRs and 3,782 Discussion
records with complete reported remote pagination. Only 109 of 6,319 local
note paths were materialized. Separate Git searches examined all main
research READMEs for the named object and singular-value/gate-cut terms;
live capped PR lists and merged searches were also read. These searches do
not cover unpublished work or certify novelty. The cited predecessor supplies the additive bound; no sharp Phi(beta)
constant was found within that coverage.

Credit Vlado Vojdanovski for the shallow Toeplitz compiler, Cinna Davis for
its retained Gaussian caller, Brian for the uniform macro-cut and sharp
forward-prefix results and explicit internal-shear question, Jose Manuel
for the rational compiler and physical-cut continuation, Ryanson Jonathan
for the one-factor error ledger, unpaidmoon, and James Reed for the retained
one-level/finite-prefix lineage. Classical FFT diagonalization, singular-value
decomposition and the elementary shear norm formula are background.
