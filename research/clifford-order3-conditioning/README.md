# A second trace constraint for three-qubit Clifford conditioning

Prepared for ToikY with substantial source-aware OpenAI Codex assistance.
New work Apache-2.0; [LICENSE](LICENSE) and [NOTICE](NOTICE) retain the repository
license and source attribution. Retained source notices and numerical facts
keep their provenance. This is a written native-algebra side result, separate from
physical implementation, selected admission and human/proof-kernel acceptance.

This takes [Nick Petalas PR6794](https://github.com/CrocSwap/integer-mult-bounds/pull/6794)'s
second-class trace handoff, using [alephnan PR6714](https://github.com/CrocSwap/integer-mult-bounds/pull/6714)'s
exact alphabet, width-nine multiplicities, tensor reciprocity, Pauli-character
orbits, Gram normalization, Schur propagation and published-table identification
as inherited mathematical inputs. The one-transvection relaxation and bound807
are predecessor work, not a new computation or theorem here. Own excluded6718
reviewed the earlier even-sector argument and is not counted again.

The actual new lift is g=(hS) tensor I4, with
h=(1+i)/2 [[1,1],[1,-1]] and S=diag(1,i). It is Gaussian-dyadic, has trace4
and cube -I. Its symplectic quotient acts with order three on one hyperbolic
plane and fixes the complementary four dimensions. The associated source
quotient fibre5 has size672 and fixed dimension4, corresponding to published
columns9/10, distinct from the transvection's quotient index14/columns31..33.
The lift-to-class argument is in PROOF.md; the old table identification remains
a cited premise, not reconstructed from group multiplication.

For an even-sector irreducible mu with central iI acting by -I, write
conjugate(V) tensor mu = sum n_sigma (V tensor sigma), d_mu=N*a, N in{28,36}.
Exactly6 forms in the36-form even-Arf orbit and10 forms in the28-form odd-Arf
orbit are fixed by this quotient. On a fixed multiplicity space, g has cube I
in mu, so the real part of its trace lies between -a/2 and a. Individual traces
need not be real. The exact natural trace4 cancels in the character identity;
the retained real quotient column then gives the new constraint on
T3=sum n_sigma chi_sigma(gbar):

```
N=36: -3/N <= T3/d_mu <= 6/N
N=28: -5/N <= T3/d_mu <= 10/N.
```

Combine this with the credited transvection constraint |Tt/d_mu|<=16/N.
The checked orbit-specific multiplicity-ratio intervals are [2/7,2353/20]
for N=28 and [1,2621/36] for N=36. They give, for every integer f>=10,

```
(405/16384) I <= H_f <= (1334151/131072) I,
condition(H_f) <= 16471/40 = 411.775 < 807.
```

Three rowwise affine inequalities, checked for every one of the thirty cited
types, and feasible primal mixtures certify the relaxation extrema. All four
displayed dual certificates have zero transvection coefficient: the new
order-three constraint alone supplies the numerical bounds, while all
attaining mixtures also satisfy the retained transvection slab. These convex
extremizers need not be actual irreducible decompositions or actual Gram
eigenvalues. No threshold change is proposed. The all-width consequence uses
the written proof and inherited Schur propagation, separately from execution.

## Evidence and reproduction

The new standard-library verifier authenticates five retained inert source
files and their exact manifest before calculating. The first run passed in
0.702 seconds with24.3125MiB maximum RSS. It checks one actual8x8 Gaussian lift,
64 signed Pauli images, all64 quadratic forms over4,096 distinct form/vector
cases, and252 distinct feasible vertices:84 for N28 and168 for N36. The generic
support-three branch finds no positive three-row vertex in this fixed dataset;
it is not an enumeration of the full group or all representations. Four
30-row dual certificates and six witnessed controls pass. Controls distinguish
phase, Pauli membership, Arf classification, omitted/new bound information and
column selection; two display lost-constraint primal admission, rather than
rejection of an otherwise valid representation. It imports
or runs no predecessor scientific program, group census, numerical decomposition
or full even-sector table. No new dependencies are required.

```
python3.12 -B scripts/research_package.py --package research/clifford-order3-conditioning
python3.12 -B scripts/check_research_commit.py --package research/clifford-order3-conditioning --check-source-history
```

Generic SOURCES binds only canonical-main selection/catalogue provenance.
Actual foreign mathematical sources are byte-identical package-local copies,
bound by SOURCE-PINS with exact head/path/blob/mode/size/hash and checked at
acquisition against the source trees. That foreign association is distinct
from generic canonical ancestry; cached refs are not publication history.
Direct replay needs only these local files and no Git or network. VERIFY has
no external live runtime input. Default normal/optimized commands compare the
entire typed retained RESULT. Final normal/optimized packets are identical:
13,000bytes, SHA25638380ddd9be74d0bf0beb6bd2c21a4dddbc7e78e94ffc3607c08bf421118771a.
After the first PASS, one receipt key was renamed from form_vector_evaluations
to distinct_form_vector_pairs:4,096 denotes distinct grid cases, not the two
function evaluations per case. The entire typed first packet is otherwise
identical; original bytes/code and both pre-correction replays are retained
in the session receipts. No mathematical arithmetic/source/control changed.
No package self-hash is included in its own scientific packet.

## Open next questions

Determine whether the relaxed extrema are realized by actual even-sector
irreducibles. The smallest useful next step is one actual quadratic-form
stabilizer representation/decomposition bound to this central sector, not an
unlabelled convex mixture. That information is absent here; no full table or
follow-on search is reserved.

For physical use, name an exact caller and its alphabet/coefficients, then price
preparation, coefficient recovery, precision, routing, movement, ownership,
restoration, stock and the complete recursive supplier invoice. These remain
unknown. All five selected assumptions and the frontier are unchanged.
The formal-interface-lemma card is explicitly changed/partial: no Lean
proposition or original selected-interface acceptance gate is closed.

## Credit and exposure

Credit Petalas6794 for its exact one-transvection807 certificate and explicit
second-class request; alephnan6714 for the three-qubit theorem, decomposition,
normalization, reciprocity and Pauli-orbit reduction; Lee, Yu, Peng and Lai for
[the published table](https://arxiv.org/html/2309.14850v2#S6.SS3); Ali Romman and
MatShep for the general Clifford and sharp small-qubit lineage; and all retained
authors/notices. Quadratic-form classification, character trace bounds,
centralizers, tensor reciprocity, convex duality and Schur positivity are
classical. No new character table or separate review of those inherited
identifications is claimed.

The root proposed paired-transvection count guesses and the hS lift/phase
recipe during preclaim orientation; these were unaccepted then and no new
scientific execution had occurred. Related source-aware proof, implementation,
overlap/metadata and challenge roles see those sources and proposal. This is
not blind independence, human acceptance or proof-kernel verification. Exact
claim, source pins, stop rule and preserved exposure are linked from TASK.json.
