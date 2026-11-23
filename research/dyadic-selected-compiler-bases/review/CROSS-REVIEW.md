# Independent review: selected dyadic compiler bases

**Disposition: accept the scoped alternate-basis theorem.** The proof
`PROOF.md` at SHA-256
`080be9adb3d9a6f2bd58be334881d7ce7c3be691b49c7fb451705917d92a1283`
is unchanged from the interrupted author package. The completed review
confirms its lattice lemma, its application to the actual selected source
differences, and the literal carried-basis compiler interface.

This result removes an additional finite set of forbidden odd primes for
one compatible choice of fixed pre-cover bases and matchers. It does not
make an arbitrary predecessor basis dyadic or a chosen rational Gaussian
pivot valid at every odd prime. It supplies no new kappa and no whole
foundational-assumption discharge. The main selected certificate remains
conditional at `363005817/100000000000`.

## Mathematical review

For an idempotent P over a localization R, choose an allowed denominator
clearing s. The two column lattices of sP and s(I-P) have complementary
rational spans. Their chosen integer bases concatenate to a square B, with
PB = B diag(I_r,0). Their sum contains sZ^n because sI=sP+s(I-P), so its
index divides s^n. Thus det(B) is a unit of R, and the adjugate identity puts
B inverse in the same ring. This controls the entire image and kernel;
no appeal to a single nonzero minor is needed.

For nested P,Q with PQ=QP=Q, the three projectors Q, P-Q and I-P are
pairwise annihilating and sum to I. In particular the kernel of P-Q is
im(Q) plus ker(P). This directly verifies the complement that is easy to
lose in a normalization argument.

If P=B_P E_r B_P^-1 and Q=B_Q E_r B_Q^-1, then the proposed orientation
S=B_P B_Q^-1 gives SQS^-1=P and also sends I-Q to I-P. The same matrix
identities survive any ring homomorphism R -> Z/q^w. For R=Z[1/2], every
odd q is admissible. This proves split rank for all widths through a
complete inverse pair, not through a presumed nonvanishing fixed minor.

The deterministic integer column algorithm uses unimodular Bezout
operations and is a valid construction of the lattice basis. The written
proof controls the determinant independent of any pivot accident. The
optional q-independent Euclidean factorization does not supply the retained
`2N^3` physical route bound; the proof correctly leaves that separate.

The complete syntax review is in [SOURCE-SYNTAX-REVIEW.md](SOURCE-SYNTAX-REVIEW.md).
It checks the suspended outer normalizers, all complement columns, coupled
port route, actual restricted-sector formula and full GL physical service.

## Separate exact computation

`independent.py` imports neither `localized.py` nor `check_localized.py`.
It reconstructs the source catalogue directly from authenticated source
bytes, uses reverse-pivot inversion and rational Gram-Schmidt selection,
and uses a finite quotient group to obtain the lattice index independently
of the author's Euclidean column reduction:

    [Z^n:L] = s^n / |L mod s|.

Modulo s, complementary columns are negatives of the sP columns; explicit
subgroup generation therefore computes this index. This second route
checks every one of the 513 actual differences. The largest enumerated
quotient image has 256 elements. Its index distribution agrees with the
author's absolute determinant distribution. This agreement concerns the
distribution; the separate basis conjugations are checked individually.

The reviewer then chooses its own complete source bases and checks both
summands over q^w for q in {3,5,7,11} and w in {1,2,3}: **6,156** exact
prime-power cases. It also runs q-unit Gauss-Jordan elimination for each
case; tests all 111 actual 15-axis port-route blocks; verifies source
scalar endpoints and current charts; and checks carried non-prefix image
splits and complete equal-rank matchers. No all-width conclusion rests
on the finite list of prime powers.

Meaningful failure controls include:

- Rescale one **kernel** column of the actual (2,270) source difference by
  3. The complete matrix still normalizes the rational projector, but its
  determinant becomes -3/4 and it is not invertible at q=3. Image-only
  checking would miss this error.
- Route the two ends of a coupled scalar contact differently. An exhaustive
  48-row GL_2(F_3) fixture exhibits a changed source row and payload.
- Replace an idempotent sector by a non-idempotent matrix. The proposed
  restricted-sector inverse fails.
- A determinant-one matrix with prescribed leading pivot 3 requires a
  different unit pivot at q=3. Full elimination succeeds after a swap.
- The restricted ordered-shear example over Z/9 fails its allowed first-row
  invariant, while the full GL elimination succeeds. No restricted tariff
  is silently imported.

## Recovery correction and retained erasure premise

The interrupted review script had not produced an accepting receipt. Its
first execution failed because it required every raw CLEAR to contain zero.
That was a mistaken test contract: retained #7840 Section 2 explicitly
reports **237 nonzero BIT CLEAR sites** under `owned_erasure`. The reviewed
source also swaps the current chart metadata with its whole field. The
recovered checker now verifies private ownership/current chart, counts all
237 nonzero erasures and preserves chart metadata through SWAP.

No source bytes or erasure theorem were changed to make the replay pass.
The result intentionally retains that assumption. This correction is
recorded because an apparently stronger zero-retirement check would have
silently audited a different source program.

## Relationship to the five selected assumptions

| Selected assumption | What this review establishes | What remains |
| --- | --- | --- |
| `native_all_columns` | Fixed binary complete matchers and projectors remain valid at every odd-prime-power width | Native scalar/phase semantics, all-column execution and physical service obligations outside this algebraic part |
| `owned_erasure` | The source dependency is explicit, including 237 nonzero clears | Allocation, erasure, suspended ownership and its time/space contracts |
| `compiler` | The alternate carried-basis arithmetic closes under the literal finite binary grammar | The full finite-word/funding/runtime proof, supplied separately in #8092 and its predecessors |
| `precision_tape` | No new forbidden odd denominator is needed in a fixed pre-cover matcher | The actual descriptors, factorization, scans, inverse routes, movement and storage prices |
| `analytic_recovery` | No extra finite-cover bad-prime list for these fixed choices | The quantitative `q > 2^45 N^5` bound and the distinct growing outer fine-prime, analytic decomposition and exact recovery obligations |

## Reproduction and scope of acceptance

Run the four commands registered in `VERIFY.json`, or run the author and
independent checkers directly with normal and optimized Python. The expected
markers are `PASS_LOCALIZED_ALTERNATE_IMPLEMENTATION` and
`PASS_INDEPENDENT_DYADIC_REVIEW`. The latter writes its deterministic evidence
and independently selected complete bases to this directory. Both use the
standard library and authenticated retained inputs; no network is needed.

The review accepts a scoped written proof and finite corroboration. It is
not a complete selected multiplier replay, an execution at the astronomical
compiler ambient, human peer review or proof-kernel acceptance.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Original source authors and the interrupted author/reviewer work retain
their credit in `NOTICE.md` and `ORIGINS.json`.
