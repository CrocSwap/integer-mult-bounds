# Independent review of selected physical narrow pairs

**Outcome: PASS for the scoped exact theorem. No new kappa.**
Reviewed author proof SHA256:
`ce72eb550b609fea7efd29fdefafc72f005bf52594aafb6efeda40c830c1073e`.
Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
This separately executing OpenAI review is not a human review, a formal
kernel proof or a numerical verification of transcendence. No author
implementation is imported by `independent_check.py`.

## 1. Exact source boundary

BILATERAL-LDU explicitly defines nearest embeddings
`q_i=floor(t*i/s+1/2)`, centered residues `beta_i=t*i/s-q_i`, and

    G_ij=exp(-a[((t/s)j-q_i)^2-beta_j^2]).

Its periodization uses `0<=i,j<s`. The retained phase-cell derivation
keeps the original physical cut and endpoint cells separate. The fine
prime construction preserves original source side s and dyadic target
side t, with t in `{r_source,r_source/2}`. A local capped interior,
microbox side or separately supplied page length is not substituted for
either original side. The additional canonical microbox source audit
confirms that the source cores partition `[0,s)` exactly.

This G is already the retained column-normalized coefficient array from
the earlier `N=C T D` interface. It is not raw resampling T. The theorem
uses its unrounded, alias-deleted coefficients on that finite index list.
The fully periodized N adds aliases, even to its diagonal. The stored H
uses rounded weights and a rounded kernel. Neither is identified with G.
No new shift or chirp similarity is performed, and no ordinary
Stein-rank invariance under similarity is assumed.

For odd s there are no half-integer ties. Delta=t-s is a unit modulo s,
so the numerators `n_i=s beta_i` traverse all centered residues exactly
once. The embeddings lie in `[0,t)`. A same-cell consecutive source pair
maps to consecutive selected target positions, although the theorem does
not identify it with the different broad target-grid matrix or with a
currently scheduled capped interior. The chosen vertices could belong
to a scheduled boundary.

## 2. Physical entries and the endpoint

For a same-cell pair, `n_(i+1)=n_i+delta`. Direct substitution into the
original G gives

    [[1,U],[V,1]], U=exp(-a A/s), V=exp(-a B/s),
    A=2t-s+2n_i, B=s-2n_i, A+B=2t.

The exact phase range is the odd-lift interval
`2delta+1<=A<=2s-1`; B then lies in the same positive interval.
The independent checker derives both exponents with Fractions from the
nearest indices, including the direction of U versus V. The source
normalization is retained; there is no discarded linear or quadratic
gauge.

An admissible lift determines `i=delta^-1*n_i mod s`. If a same-cell
unit step started at the terminal index s-1, its next numerator would be
`n_s=0`, so `n_i=-delta` and A=s. Therefore excluding zero residue A
also excludes that terminal index. This uses the retained period cut at
zero. An arbitrary shifted cut would need its own endpoint argument or
one extra excluded point.

Each factor is invertible because `UV=exp(-2at/s)<1`. It is generally
nonsymmetric and is not asserted to be SPD. This is sufficient for the
general inverse displacement identity used later.

## 3. Independent count and square-root cap

For `2r<s`, a collision in the degree-r pair box yields nonzero
`(d,e) in [-r,r]^2` with

    (d-e)A=-2te mod s.

If d=e!=0 there is no solution, since t is a unit and `0<|e|<s`.
Otherwise the coefficient of A is a unit and fixes at most one root.
Of the `(2r+1)^2-1` nonzero pairs, 2r are impossible equal pairs.
Identifying each remaining pair with its negative leaves
`2r^2+r` classes. Zero roots and coincidences between different classes
only loosen this upper bound. Thus at most `2r^2+r` nonzero residues
are bad. At most delta odd lifts also violate the physical phase range.
The lower bound

    b=s-1-delta-2r^2-r

is therefore correct. Its positivity implies `2r<s` for r>=2, so the
theorem states no hidden extra numerical hypothesis. Each good A gives
a distinct starting index. The count concerns centered residual phases
beta_i or starting indices, not original cells `q_i-i` (at most
delta+1 of those exist).

Under p>=3, s>=p^4 and delta<=s/p^2, the even cap
`2 floor(sqrt(s_min)/4)` is at least two. With r no larger than that cap,
`2r^2<=s/2` and `r<=sqrt(s)/2`. The author's displayed estimate is valid:

    b >= s-1-s/9-s/2-sqrt(s)/2 >= s/3-1,

because s>=81 implies `sqrt(s)/2<=s/18`. The exact integer computation
of the cap is `2*(isqrt(s_min)//4)`. Combining it with the even A9 floor
`R_N=2 ceil((N+3)/5)` preserves all parity and size requirements.

The fine-prime source scale eventually supplies s>=p^4, without a
practical-cutoff claim. For large groups the rank floor saturates at the
square-root-prime scale; it is not automatically linear in N. The
positive-density statement is per axis. It is not a dimension-independent
positive fraction of all g-fold phase tuples.

## 4. Directed polynomial specialization and inverse

The inherited A9 matching certificate, trimmed to size r by even
endpoint prefixes, is a principal minor of the full displacement matrix.
For the directed formal tensor `tensor [[1,U_i],[V_i,1]]`, its determinant
polynomial remains nonzero: specializing U_i=V_i=Q_i gives the nonzero
symmetric certificate. Every entry is squarefree, so each individual
directed-variable degree is at most r. Nonzero symmetric restriction is
a sufficient test; its converse is not asserted.

For good phases, the two-variable exponent map is injective modulo s_i.
CRT across distinct primes therefore distinguishes every monomial in
the full individual degree-r box. With `S=product s_i` and
`z=exp(-pi alpha^2/S)`, the actual exponents are
`A_i S/s_i` and `B_i S/s_i`. They are positive integers. Gelfond-Schneider
applies to common positive integer alpha exactly as in the separately
reviewed A10 theorem. A nonzero specialized integer polynomial cannot
vanish at z. Each ordering's minor is treated separately, not multiplied
into a high-degree product. The selected phases are independent of the
ordering and work for every order at the same exact tuple.

For invertible A, the two Schur complements of
`[[A,Z],[Z^T,A^-1]]`, followed by reversal J, give
`rank E(A^-1)=rank E(JAJ)`. No symmetry or SPD premise is needed.
Consequently the all-order forward result proves the inverse result.
The inverse is that of the selected tensor, not a principal section of
the inverse of a larger source array.

## 5. Selector bill and representation consequence

The stated selector can scan nonzero A residues and test all difference
pairs for each admissible odd lift. There are O(r^2) pairs and every
integer has O(log s) bits: even the unreduced expression
`(d-e)A+2te` has that bit length under r<s. Schoolbook multiplication,
division and Euclidean inversion therefore give

    O(g*s_max*r^2*poly(log s_max))
    <= O(g*s_max^2*poly(log s_max))

bit work. The nested counters, current candidate and arithmetic
temporaries use O(log s_max) local scratch. No hash table, sort or
unit-cost random lookup is needed by this selection algorithm.
Retaining all output indices costs O(g log s_max) bits. Every repeated
invocation must be charged. For the retained source scale and polynomial
g, this standalone bill is exp(o(p)); it is not an amortized caller bound.

The selector produces indices only. It constructs neither matrix entries
nor generators. Source acquisition, coefficient production and precision,
transport, runtime arithmetic, head returns, restoration and recursive
children remain separate. A literal uninterrupted source caller is not
established by this integer arithmetic bound.

The dense representation consequence is correctly restricted. Since one
ordinary lower/upper triangular Toeplitz product has rank-one Stein
displacement, a sum needs at least r terms. Separately storing both full
length-N vectors of each term uses at least 2Nr scalar slots. This is a
lower bound for that format, not a general runtime, space or multiplication
lower bound. Exact transcendental coefficients are not a finite-bit
implementation.

## 6. Independent executable evidence

`independent_check.py` compares the bad set obtained from direct degree-box
enumeration with a separately constructed set of signed-difference roots.
It reconstructs source phases by integer nearest-index arithmetic and
checks the original Gaussian exponents with Fractions. Its directed
polynomial checker compares full multivariate expansion followed by
substitution with entry-first univariate expansion. Those last two routes
share the independent determinant engine; they are not claimed to be
separate software implementations. No author helper is imported.

Normal and optimized runs give identical receipts:

| Check | Completed coverage |
| --- | --- |
| Small source/degree cases | 135 |
| Nonzero residues in those cases | 8,952, exhaustively checked |
| Degree-box points in those cases | 505,752 |
| Exact fine-prime interval fixtures | Four at p=3, r=8 |
| Directed determinant expansions | 48 full four-by-four polynomials, 720 terms |
| Controls | Six |

The four larger fixtures have 832, 844, 378 and 386 good starting indices,
above the respective certified lower bounds 781, 793, 325 and 333. Their
primes are 971, 977, 487 and 491, with target sides 1024, 1024, 512 and
512. They satisfy the exact fine-prime interval inequalities, but do not
instantiate every asymptotic assembly prerequisite. The directed minors
cover all 24 vertex orders for each of two source-axis pairs. In contrast
to the symmetric case, first-vertex normalization is not silently used
to reduce the number of directed order tests.

Controls detect a cross-cell exponent formula, the excluded physical cut,
a degree box too large for its modulus, a failed modular certificate,
positive periodic aliases and the direction of the symmetric restriction
argument. A bad modular phase fails this sufficient certificate; it is
not thereby a proved low-rank matrix. The finite checks do not prove the
universal count, inherited A9 theorem or classical transcendence input.

The checker authenticates exact retained bytes of A9-PROOF,
BILATERAL-LDU, FINE-PRIME-PADDING and PHASE-CELLS. The canonical source
extraction and additional physical-period reads are recorded in the
separate feasibility source pins. After installation beside `inputs/`:

```sh
python3 -B independent_check.py
python3 -B -O independent_check.py
```

From this separate review directory, supply `--package PATH`. Default
execution prints only; `--write PATH` explicitly saves a receipt. No
assertion is used as a validation gate, so optimization retains checks.

## 7. Limits and credit

No arbitrary-phase, raw unnormalized, periodic, rounded, scheduled-page,
larger-section or larger-source-inverse rank transfer is proved. Deleting
vertices changes the ordinary shift. There is no minor magnitude,
singular-value margin, Cp tolerance or finite-precision robustness from
the transcendence argument. All five selected assumptions and the
multiplication frontier remain unchanged.

No mathematical defect was found in the frozen scoped proof. This review
supports selected exact physical coefficient sections and their tensor
inverses, with no source caller acquisition or materialization claim.

Prepared for Jerry Chen / @CubeJerry by a separately executing OpenAI
review agent. The lead proposed the phase approach and stronger count;
the author developed the theorem. This reviewer independently checked
source geometry, both count routes, arithmetic bills and directed
polynomial specialization, preserving the A9 and A10 predecessor credit.
Separate AI review is not human or formal-kernel certification.
