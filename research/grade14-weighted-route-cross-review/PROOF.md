# Independent binary composition audit of PR #7837

## Conclusion

**Scoped PASS: no blocking composition flaw found in the assigned binary
right-route, port-matching, return, and common-weight seam.** The argument
requires two qualifications that are satisfied by the stated construction:

1. Arbitrary role-dependent routes may surround a completed **independent-job
   endpoint**. A child with an off-diagonal endpoint requires compatible
   routes on its coupled inputs and outputs. The actual native port routes
   both main fields of a pair by the same matcher.
2. The common external weight must be invariant under each current route.
   The source's ancestor-only condition is sufficient, while some nonconstant
   fresh-dependent weights also satisfy this weaker algebraic condition.
   Full inverse return must restore the current cover before later parent uses.

These are substantive conditions, not consequences merely of allowing
arbitrary child input values. The source states the shared pair routes in
`inputs/PR7837-PROOF.md` Section 2, distinguishes completed independent targets in Section
3, and states the ancestor/fresh separation in `inputs/PR7837-ROUTES.md`. The algebra below
makes their joint use explicit. Negative controls fail when these conditions
are removed.

This review is **not** acceptance of the entire four-premise multiplication
theorem or removal of a selected assumption. It does not repeat the author's
finite leaf tests, audit the K-shear identity assigned to the root, or assess
the complex supplier and full analytic application. The canonical selected
five-assumption record is unchanged.

## Exact source boundary

Reviewed PR head: `a7f99a5f5f919dd3ffb2987f90c1e7d6527feb1e`, Ali Romman's
`research/grade14-native-realization`, over canonical main
`e54523517d0f03e58352e647c403a5af3e525a57`.

`SOURCES.json` authenticates the targeted files read and their necessary retained closure. The local
initial `reference/pr7837` proof, route, application and validation copies were
compared byte for byte with this exact commit. The existing source packages
`delayed-cover-batch-allocation`, `selected-bit-recursive-closure`, and
`notes/three-stage-cover-bit.tex` were inspected for their address, ancestor,
and retained-macro contracts. No source or worktree was modified.

Important reviewed hashes:

| Source | SHA256 |
| --- | --- |
| `inputs/PR7837-PROOF.md` | `2acfa8dacf98629d3ec51a3475557706723f6bdecd37b1d6ffdfaa4a278de013` |
| `inputs/PR7837-ROUTES.md` | `5e7ff92ce2566158bef66536c76c0b2dbece45ac66f85c7c902f4de2ed802d16` |
| `cover.py` | `52cfdb73f0289b1d2fd015865104dc66ecb7478eef2dbe3d48325791cea7b786` |
| Literal binary word | `d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9` |

## 1. Full right action, carry cocycle and inverse

Fix an admissible prime q and a rational invertible matcher S whose entries
and inverse are q-integral. A complete cover header has unique coordinates

```
g = g_0 + qX,
g_0 in GL_N(F_q) represented entrywise in {0,...,q-1},
X in Mat_N(Z/q^(w-1)).
```

Write `h_0` for the chosen representative of `g_0 S mod q` and define the
q-integral rational carry

```
C_S(g_0) = (g_0 S - h_0)/q.
```

Then the unique low/high decomposition of `gS mod q^w` is

```
(g_0,X) -> (h_0, X S + C_S(g_0) mod q^(w-1)).
```

This formula acts on **every one of the N squared high entries**. A matcher
supported on a few address axes still acts on those columns in all N high
rows. It is not sufficient to update only a small square high submatrix.
The source loops over all rows and retains all other coordinates.

For a second matcher T, with `k_0=(h_0 T mod q)`, exact rational arithmetic
gives the cocycle identity

```
C_(ST)(g_0) = C_S(g_0) T + C_T(h_0).
```

Consequently the two complete affine routes compose in precisely the order
`g -> gS -> gST`. With `T=S^-1`, the low representative returns to `g_0`
and the total carry is zero. This proves inverse return at every w, including
nonzero high carries. It does not infer an inverse merely from a low residue
permutation. At w=1, the high ring has one element and the same identity
specializes to the low route without a zero-width interchange.

This proof also establishes a genuine bijection on all GL cover headers:
right multiplication preserves invertibility, and the decomposition is
unique. Arbitrary padding or zero payloads must traverse the same bijection;
discarding them before the completed endpoint is not licensed.

### The row factorization is a valid implementation target

The source reduces `S^T` by rational row operations with pivots that are units
at q. The current active Schur block remains invertible modulo q, so a unit
pivot exists after row permutation. Its row operations remain q-integral.
Reversing and inverting those reductions gives the right action `X -> XS`
on each high row. In particular, the emitted `add(target,source,c)` means
`X_target += c X_source`; it does not mean a left matrix action.

For a later source than target, exchanging the two complete fields makes the
source earlier; the ordered update followed by the inverse exchange restores
the intervening and exterior fields. The complete ordinary interchange used
for that step is explicitly the previous stage's service. Fixed unit scaling
is a whole-fibre permutation. The finite low route and high carry are also
charged. Nothing here requires a native operator assertion to implement the
route itself. Its tape tariff continues to use the declared retained stream
and precision assumptions.

## 2. Role-dependent matching: the needed endpoint condition

Let role i carry an arbitrary function `x_i(g,z)` of the cover header g and
all payload/spectator coordinates z. Define ingress R_i by transporting its
entire field from g to `h=gS_i`. If a completed child endpoint is diagonal
in productive roles and performs `J_i(h)` on role i, its returned parent
operation is exactly

```
x_i(g,.) -> J_i(gS_i) x_i(g,.).
```

The roles may use different bijections because each completed output depends
only on its corresponding input. Internal mixing between roles is harmless:
at each h the child receives arbitrary independent functions, and its exact
endpoint identity cancels all unwanted dependencies before return.

For a fixed child projector Q_i and parent projector P_i satisfying
`S_i Q_i S_i^-1=P_i`,

```
(gS_i) Q_i (gS_i)^-1 = g P_i g^-1.
```

Thus matching is exact, including the direction of S_i and its inverse.
The same identity applies to split projectors and their complete complementary
spaces; it requires denominators and basis determinants to remain units at q.

### Why arbitrary-input wording alone is insufficient

If the child has a nonzero off-diagonal term from role i to role j, after
return to parent header g in role j its donor comes from

```
g S_j S_i^-1
```

in role i. Unless the intended parent endpoint includes that row displacement,
the two routes must agree on this dependency. For an ordinary shear, different
S_i and S_j give an immediate arbitrary-payload counterexample: put a one at
one of the two distinct donor rows and zero at the other.

The actual binary native interface has off-diagonal terms only within each
main X/Y port pair; helpers have independent returns. `inputs/PR7837-PROOF.md` routes both
main fields of port i with the same `S_(i,s)` and undoes both routes. Its
completed outer caller has independent productive jobs before the general
whole-job matching step. This is exactly the structural condition needed.
The review did not re-run the author's 680-by-680 incidence test; the stated
support and the retained exact source identity are its explicit finite input.

### A joint mixed-field identity over the full ring

For two complementary split projectors Q_0,Q_1 and one common head weight A,
write D_0,D_1 for their weighted address permutations and F_A for the weighted
full interchange. Then

```
F_A D_0 = D_1.
```

On arbitrary binary payload arrays the sequence

```
Y <- Y XOR X;  X <- D_0 X;  Y <- D_1 Y;  Y <- Y XOR F_A X
```

returns `(D_0 X_original, D_1 Y_original)`. The foreign donor appears twice
at exactly the same address and cancels over F_2. This argument uses equality
of address permutations; it never mistakes addition in the odd residue ring
for payload XOR.

The new verifier joins this cancellation with two different rational routes,
their nonzero low/high carries, common ancestor-dependent weights, and
individual inverse returns. It therefore checks the interface that the
author's low-only mixed-cut test and separate high-route tests treat
separately. It imports no author leaf, projector, or route evaluator for
these joint checks.

## 3. Common weights, fresh coordinates and complete spectators

Let a denote all exposed ancestor fields, and let `A=A(a,j)` be the common
unit head weight at atom index j. A current route changes only the invocation's
fresh g, so it commutes with the head address conjugation `diag(A,I)`.
Pointwise XORs and role permutations also commute with applying this same
address permutation to every role. Conjugating the **completed compiled
program** therefore supplies the weighted endpoint without giving separate
private weights to internally matched roles.

A fresh-dependent weight that fails route invariance can break this reasoning:
differently matched roles at one child h can carry different weights. The
joint verifier deliberately makes that mutation and exposes 100,016 failed
column cancellations/endpoints. This is a counterexample to that particular
non-invariant extension, not to all fresh dependence or the stated theorem.

The exact weaker condition is `A(a,gS_i,j)=A(a,g,j)` for every routed role i.
Then arriving roles have `A(a,hS_i^-1,j)=A(a,h,j)`, so they still share the
common weighted endpoint. The two test matchers have determinant one. The
new positive control takes `A_0=u_0(a,j) det(g)` and
`A_1=u_1(a,j) det(g)^2`, proving cancellation and parent endpoints in another
109,536 column cases. At fixed context and column the determinant assumes
more than one value, so this control is genuinely fresh-dependent.

Every actual port matcher has determinant `(-1)^7=-1`, independently checked
from all 222 exact row factorizations. Thus functions of `det(g)^2` commute
with these port routes. This does not establish invariance under every later
compiler matcher: over Z/9, `g=I` and `S=diag(2,1)` change `det(g)^2` from
1 to 4. The refinement is algebraic only. No descriptor, cost or complete
runtime extension is claimed, and #7837's stronger ancestor-only source
theorem is unchanged. [LEMMA.md](LEMMA.md) states the reusable condition.

The retained batch address map preserves the distinction. At depth j write

```
b = U H^j + A_old,
U = U' (L H) + l H + h,
b_child = (U' H + h) H^j + A_old.
```

Here `A_old` is the retained tuple of earlier high coordinates, not the
weight array. Current matching permutes the complete current `(l,h)` cover
and fixes `U'`, `A_old`, all body coordinates and all spectators. At a child,
the current parent h joins the exposed ancestors. The next child fresh cover
comes from disjoint unused U'. Conditional on any ancestor assignment it is
still a complete cylinder. The inverse Euclidean divisions recover the
parent row exactly. This preserves all high matrices while the child volume
shrinks by L, not by LH.

The generation order and branch schedule in the source are fixed by finite
instructions and current low types, rather than payload values. A branch
retains every unused fresh digit. Thus each actual entered child contains its
full next fresh cover even when its ancestor weight correlates with past
choices. The good/bad fraction is taken separately on each fixed edge's
complete fresh low cover; statistical independence of payloads or different
invocations is unnecessary.

Owner independence has an explicit boundary: distinct logical roles must be
backed by distinct supplied owners, private roles initialized and retired,
and parent owners suspended while a child uses their exposed fields. These
are consumed from `owned_erasure`. The algebra proves arbitrary-data behavior
on those supplied owners; it does not build an allocator or establish those
ownership premises from address bijectivity alone.

All arguments tensor with the identity on every other complete coordinate.
The code checks the actual reversal of the column order when identifying
logical `(H,CT)` coordinates with physical head and tail slots. For general
f each column has its own allowed unit weights, and the column slot bijection
covers all 4f coordinates in the two-dimensional witness. No coefficient or
payload depends on an omitted spectator assignment. Extra owner tapes remain
outside this operation by the supplied disjoint-owner contract.

## 4. Binding the route factorization to actual source ports

The review reconstructs all 111 actual U_i from the literal word's first head
basis and complementary seven-body basis. On the active fifteen-dimensional
space it constructs

```
S_i = (U_i direct-sum I_7) swap(E[1:8],B_s)
      (U_i^-1 direct-sum I_7)
```

directly on basis vectors. Each exact rational matrix is involutive. Its
entries have denominators only 1 or 4. The remaining 119 address axes in the
134-axis caller are identity factors. Choosing any of the eighteen body
blocks only changes this fixed coordinate embedding.

For q=3 and q=5, the unchanged source `cover.row_program` is run on every
actual S_i. A separate exact rational column-operation oracle multiplies its
emitted elementary word and verifies equality with S_i, rather than testing
sample payload values. All emitted scale coefficients are local units, and
all shear coefficients are q-integral. This gives **222 exact rational
factorizations**, totaling 8,446 elementary row slots, with maximum 43.
They therefore work at every precision w for these two tested primes.

The unit-pivot proof in Section 1 covers every admissible prime, including
the much larger actual construction prime. The finite tests are not a claim
to have enumerated those primes or the astronomical compiled matcher list.
When lifted to the full ambient, this word must be applied to every high
matrix row; the identity spectator columns must also remain represented.

## 5. Dependency audit of the four retained assumptions

| Retained premise | What this composition argument uses |
| --- | --- |
| `owned_erasure` | Distinct physical role owners, private zero entry, retirement, suspended parent contents and complete return discipline. |
| `compiler` | A finite emitted chronological grammar, formal independent-job target identities, rational placements, splitting and prices. These are identities conditional on the submitted abstract job symbols; physical native correctness is not included. The local route/conjugation identities are proved here. |
| `precision_tape` | Ordered controlled shifts, fixed stream operations, layout/parking and their stated tariffs. Address correctness of those routes is established independently of a native job; the prior-stage ordinary exchange endpoint comes from the staged construction rather than an extra native premise. |
| `analytic_recovery` | No role in the binary matching proof; it enters the outer integer consumer. |

The previous-stage ordinary dependency is well founded in the written
application: the preparatory stage starts from elementary digit exchange and
later stages use the completed earlier service. The same fixed template can
be selected before choosing an admissible prime. Good/bad normalization
creates smaller positive-width children; the w=1 and zero-half boundaries
are explicit. The proof does not ask the ordinary service currently being
constructed to implement its own right-route exchanges.

There are two distinct induction levels. First, the finite compiled word is
interpreted with ideal positive address-permutation jobs `D(P)`; its formal
target identity and the matching lemma prove the denotational endpoint for
every f. This is not an invocation of a recursive runtime provider. Second,
induction on the atom count implements those jobs: at a nonterminal count
`n>=N>1`, good children have width `floor(n/N)<n`, and fallback children have
at most that width. Bases and remainders use the already completed previous
ordinary stage. The width induction may therefore invoke a child's completed
runtime endpoint without assuming the parent endpoint. This distinction is
necessary to read the matching substitution without a circular native axiom.

No specific circular use of `native_all_columns` was found in this binary
composition seam. This assessment does not certify all tariff, storage,
compiler-admission or source-application obligations elsewhere in the PR.
In particular, the predecessor batch-allocation proof explicitly left the
production dispatcher to be supplied; the new source supplies a fixed
symbolic schedule and the full route construction in writing. This review
checks the correctness implication under that schedule and its inherited
allocation/layout contracts, not a literal transition-table dispatcher.

## 6. Independent execution and failing controls

Run:

```
python3 -B -O research/grade14-weighted-route-cross-review/verify.py
```

The joint independent checker uses rational matchers
`[[1,1/2],[0,1]]` and `[[1,0],[2/5,1]]`. They need not be orthogonal,
and their product order matters. It checks:

| Domain | Coverage |
| --- | --- |
| GL_2(Z/3) | All 48 headers |
| GL_2(Z/9) | All 3,888 headers, including every high lift |
| GL_2(Z/27) | Every low class and all 81 specified symmetric high lifts per class: 3,888 headers; not the complete group |
| Joint matching and cancellation | 109,536 weighted column cases, multiplicities 1, 2 and 4, two ancestor contexts |
| Route-invariant fresh weights | Another 109,536 column cases; 2, 6 and 18 distinct fresh determinant values at widths 1, 2 and 3 |
| Actual source factorization | All 111 port matrices at q=3 and q=5, exact over Q |

The independent modular route formula agrees with direct full-ring right
multiplication, with complete inverse return and the carry cocycle. Both full
enumerated groups have the required bijection cardinality. The higher-width
subset is explicitly limited rather than described as complete coverage.

Controls expose 13,122 errors when ingress carry is omitted, 13,122 when
inverse carry is omitted, 15,648 when return is omitted, 7,824 when the
matcher composition order is reversed, and the fresh-weight errors reported
above. Different routes on a coupled pair displace the donor header in all
7,824 header cases, demonstrating the necessity of the endpoint condition.

The replay passes with explicit exception-based checks under optimized
Python. `RESULT.json` includes the exact counts,
source hashes and factorization digest; the registered normal and optimized commands reproduce the frozen receipt without writing scientific files.

## Remaining review boundary and credit

The retained graph/incidence certificates, all compiler-emitted records,
the whole runtime, quantitative moment/application inequalities, complex
phases, precision recovery and the remaining lifecycle/layout premises are
outside this scoped verification. The verifier is not a literal multitape
runtime benchmark. Passing its finite cases does not itself prove uniform
native correctness; the quantified algebra and complete-cylinder argument
above give the reviewed implication.

Credit Ali Romman for #7837 and the construction under review, the retained
grade-14/iterated-return contributors identified in its ORIGINS and notices,
and the whole-high allocation and recursive-closure predecessors. The new
contribution is an independent composition proof audit and joined exact
check, without changes to their artifacts. Prepared by a separate OpenAI
worker with substantial AI assistance; no human or formal-kernel acceptance
is claimed. Apache-2.0.
