# Independent R437 bad-class pivot and high-lift audit

**No gap found in the scoped implication in #4176, NUMERICAL.md §3.** For a
split rank-r projector, the low-field leading principal minors determine the
literal runtime GOOD branch over every high lift. Diagonal unit conjugation
preserves every one of those minors, even when the weights depend on the low
class, high field or earlier history. The complementary-minor argument therefore
supports the stated per-request bound under a complete, uniformly weighted
GL64 low cover. This is a written conditional proof audit with exact finite
checks and literal source execution, not formal verification or full supplier
admission. No new κ or selected-frontier change is claimed.

This answers the bad-class portion of Open next question 3 in
[Chris R / Clear1nsight's #4176](https://github.com/CrocSwap/integer-mult-bounds/pull/4176),
head `71914dfbc9ed757f6746c02e9206bb7a984edfbb`, retained on main
`f626db5c3a3d781d8f7695038776c621651f75e1`. The new work is the independent
proof-to-pivot check and its premise controls. The probability bound itself,
the carrier, its paid profile, and the numerical admission proposal belong to
the predecessors. [SOURCES.json](SOURCES.json) pins the exact eight live inputs;
[TASK.json](TASK.json) records the refined revision-7 assignment and overlap.

## 1. Precise statement and boundary

Let q be an odd prime, w≥1, R=Z/q^w, n≥2 and 1≤r<n. Let E_r be the
coordinate rank-r projector, G∈GL_n(R), and P=G E_r G^-1. A fixed invertible
source preparation can be absorbed into G. Define Δ_0=1 and
Δ_k=det P[0:k,0:k] for 1≤k≤r.

The no-row-swap elimination used at this boundary succeeds exactly when every
Δ_k is a unit. Its pivots are Δ_k/Δ_(k-1). For these split projectors, successful
pivots also imply the required *full-ring* zero residual block. Consequently
success is determined by G modulo q, and every high lift of one low matrix has
the same branch. For any diagonal H with unit entries, all Δ_k of HPH^-1 equal
those of P pointwise; no independence assumption about H is necessary.

For uniform G modulo q, the bad fraction is at most

    min(1, n*r*(q-1)/(q*(q-2))).

At n=64, r≤42 and q>2^80 this is strictly below 2689/q and 10^-16, as #4176
states. This implication assumes a fixed invertible preparation for each
request, the declared split rank, a complete uniform low cover, and unit
weights. It does not prove the actual request inventory, cover multiplicities,
ancestral-weight producer, or physical cost of fallback. Those remain caller
premises. In particular an arbitrary subset of low classes is not covered.

## 2. Why every high lift reaches the same literal branch

Gaussian elimination without row swaps gives the pivot ratio
Δ_k/Δ_(k-1), by the determinant identity for the leading k×k block. Inductively,
the first k pivots are units exactly when Δ_1,...,Δ_k are units. In R, an
element is a unit exactly when its reduction modulo q is nonzero. Reduction
commutes with products, determinants and inverses of invertible matrices.
Thus the low-field decision applies to *every* high lift, not just a sampled
high matrix. Adding q times the high digits is essential to this conclusion.

The residual block requires more than a rank test modulo q. Write P=UV where
U is the first r columns of G and V is the first r rows of G^-1. Partition
U=(U1;U2) and V=(V1,V2) at r. If A=P[0:r,0:r]=U1 V1 is invertible, both
square factors U1,V1 are invertible over this commutative local ring. Therefore

    P22 - P21*A^-1*P12
      = U2*V2 - U2*V1*(U1*V1)^-1*U1*V2 = 0

exactly in R. No nilpotent remainder survives. This is the premise that makes
the runtime Schur/endpoint check follow from the compiled pivot branch.

The pinned implementations line up as follows:

| Source entry | Relevant operation and scope |
|---|---|
| `sources.compile_specification` | Forms `(low * fixed_preparation) E_r (...)^-1` modulo q and calls `oracle.good_pivots`; it has no width or high-digit input. |
| `Matrices.prepare` | Forms `(low + q*high) * fixed_preparation` using binary Word/Ring arithmetic, then the split projector. |
| `Matrices.good_pivots` | Requires actual ring inverses, performs no-row-swap elimination and checks the full trailing Schur block is zero. |
| `forms.good_form` | Reverses columns, so its northeast pivots are the same original leading-principal pivots; row/column elimination requires the complete diagonal endpoint. |
| `numeric.selected_page` / `Page.coefficient` | Builds the unweighted form using the fixed selected branch; incoming unit ratios decorate coefficients later. The full weighted operator/Callback implementation is not replayed here. |

For a principal index set I, (HPH^-1)[I,I]=H[I,I]P[I,I]H[I,I]^-1, giving
equal determinants in R. This pointwise fact is valid even for weights chosen
adaptively from G. Nondiagonal conjugation need not preserve the pointwise
decision, and a nonunit diagonal has no inverse; neither is the stated contract.

## 3. The complete-cover probability argument

For I={0,...,k-1}, Cauchy–Binet followed by complementary minors gives

    det(G) Δ_k = F_k(G)
      = Σ_(J⊆{0,...,r-1}, |J|=k)
          (-1)^(ΣI+ΣJ) det G[I,J] det G[I^c,J^c].

This is a polynomial identity on invertible matrices. Each summand has degree
k+(n-k)=n. At G=I_n exactly the J=I summand survives and is 1, in every
characteristic. Hence F=∏_(k=1)^r F_k is a nonzero polynomial of degree at most
nr, with F(I_n)=1. On GL_n(F_q), its zero set is precisely the failed pivot
event; det(G) is a unit there.

A nonzero total-degree-d polynomial in N variables over F_q has at most
d*q^(N-1) zeros. One proof inducts on N: write it as degree t in the last
variable; its leading coefficient has degree at most d-t. There are at most
(d-t)*q^(N-2) exceptional prefixes and at most t roots at every other prefix,
yielding the bound. If d≥q the desired probability estimate is already
trivial. Also

    Pr(G∈GL_n) = ∏_(j=1)^n (1-q^-j)
       ≥ 1-Σ_(j=1)^n q^-j > 1-1/(q-1) = (q-2)/(q-1).

Conditioning the ambient polynomial bound on GL_n gives the displayed
nr*(q-1)/(q*(q-2)) ceiling, capped by 1. Multiplying each low header on the
right by its fixed invertible preparation permutes the complete cover. Each
low header has exactly q^((w-1)n²) high lifts, so uniform lift multiplicity
does not change the fraction. Summing separate per-request fallback costs
uses linearity of a finite sum, not independence among requests or weights.

For the stated cutoff, 2688*(q-1)/(q-2)=2688+2688/(q-2)<2689, and
2689/2^80<1/10^16; the verifier checks these endpoint rational inequalities.
The formula is an upper bound, not an exact bad fraction or a new optimized
surcharge. #3950 already used the rank-seven complementary-minor specialization.

## 4. Exact evidence and failure controls

The reference checker uses its own Leibniz determinants, adjugate inverses and
complementary-minor sums. It imports the original oracle and runtime only as
implementations under test. It does not import #4176's compiler, numerical
verifier or stored scientific receipts to establish the results below.

| Exhaustive field domain | Rank | GL headers | GOOD | BAD |
|---|---:|---:|---:|---:|
| GL2(F3) | 1 | 48 | 28 | 20 |
| GL2(F5) | 1 | 480 | 336 | 144 |
| GL2(F7) | 1 | 2,016 | 1,548 | 468 |
| GL3(F3) | 1 | 11,232 | 5,472 | 5,760 |
| GL3(F3) | 2 | 11,232 | 4,704 | 6,528 |

Every case checks idempotence, the signed complementary-minor identity, the
original oracle's branch and successful pivot ratios, and every diagonal unit
weight over its field. The GL2 counts also match an independent closed form:
rank-one projectors correspond to an image line and a complementary kernel
line, giving q(q+1) possibilities. The bad event is image line span(e2) or
kernel line span(e1), two sets of q elements intersecting once. Thus its exact
fraction is (2q-1)/(q(q+1)), with equal conjugacy multiplicities.

All 48*81=3,888 lifts from GL2(F3) to Z/9 agree with their low branch; all
139,968 combinations with diagonal units preserve the principal minor. There
are 2,268 GOOD and 1,620 BAD lifts.

The literal binary Word/Ring implementation runs **61 fixtures through both
`good_pivots` and `good_form`**. They include all 48 GL2(F3) headers with a
nonidentity chart and nonzero high digits, rank-one/two examples modulo
3,9,27,5,25, and three explicit rejection cases. Successful fixtures free every
owned Word. Rejected arenas are discarded; failure-path cleanup is not claimed.
Separately, the actual 64-dimensional `compile_specification` classifies 20
synthetic GOOD/BAD cases at ranks 1,2,7,14,42 and primes 3,5, with an invertible
dyadic preparation. It rejects a singular preparation. These synthetic cases
are not a reconstruction of all 903,456 actual carrier requests.

The receipt contains explicit controls for the assumptions:

- Over F3 the split rank-two projector `[[0,2,1],[2,0,1],[2,2,2]]` has leading
  minors 0,2. Its final rank-two minor is invertible, but the first pivot fails.
- Over Z/9 the split rank-one projector `[[6,3],[5,4]]` has nonzero first pivot
  6, which is not a unit. Both literal runtime routines reject it.
- I2 falsely declared rank one passes the low oracle's pivot-only test but
  fails both runtime Schur/endpoint checks. This is a premise control, not a
  defect in `compile_specification`, which constructs a split projector.
- A singleton cover supported on the swapped rank-one projector has bad
  fraction 1, exceeding the full-GL2 bound 200/9999 at q=101. Nondiagonal
  weights, dropping the q multiplier on high digits, omitting complementary
  signs, and singular preparation have separate exact controls.

## Reproduce and limits

Python 3.12, standard library only; the registered replay takes about 16 seconds
on CPython 3.12.0 / Windows AMD64, including ordinary and optimized executions:

```sh
python3.12 -B scripts/research_package.py --package research/r437-bad-class-pivot-audit --check-only
python3.12 -B scripts/research_package.py --package research/r437-bad-class-pivot-audit
```

Direct source-export replay: `python3.12 -I -B research/r437-bad-class-pivot-audit/verify.py`.
Every input is hashed before import, the import bytecode cache is isolated, and
ordinary execution compares the result with [RESULT.json](RESULT.json) without
rewriting it. `--write` explicitly regenerates that deterministic receipt.

The universal result rests on the written argument above. Exhaustive checks
cover only their listed finite domains; the binary fixture set is smaller.
This does not rerun the full carrier compiler/inventory, check every actual
dyadic base/chart or ancestry, execute the full weighted caller/fallback,
prove logical/physical stock, certify a fixed-tape tariff, or establish a new
multiplication theorem. The selected cold replay, Lean and Docker were not run.
The orientation baseline was attempted but stopped at a selected package omitted
from this sparse checkout; no selected-baseline pass is claimed.

## Overlap, coordination and credit

Canonical investigation: [Discussion #4575](https://github.com/CrocSwap/integer-mult-bounds/discussions/4575).
The entry overlap snapshot has complete pagination for 355 open PR bodies and
3,470 Discussion records, fetched 2026-10-22 at 07:46/07:48 UTC. Local note
coverage is sparse and explicitly incomplete; relevant R437 notes were then
materialized. No exhaustive novelty claim is made.

Before submission, canonical main and the relevant guidance/inputs were
unchanged. The refreshed snapshots cover 358 open PRs and 3,489 Discussion
records with complete pagination (08:07/08:08 UTC); 35 of 5,860 in-scope local
notes were searched. No new conflicting scope was found. The exact refresh
record is in TASK.json; sparse local coverage remains a limitation.

The central ledger records #4176 as merged for archive and partially reviewed.
[James Reed's earlier audit](https://github.com/CrocSwap/integer-mult-bounds/pull/4176#issuecomment-6294783671)
checked 29 finite receipt/seal/compiler-profile/numerical-delta/residual facts;
it did not prove this low-class/high-lift implication. This contribution adds
that scoped proof audit and direct binary-source tests. It does not replace
his work or change the ledger's disposition.

Credit Chris R / Clear1nsight for #4176's argument/integration and #3950's
rank-seven specialization; unpaidmoon for #4147's distinct coefficient audit;
ai-nanachi, Ali Romman, Sagar Thakrar and Rohan Arun for the carrier/hosting
lineage. The retained binary source and normal forms credit Jose Manuel /
jmbarrancoml, David Arias, Nick Petalas, ywz65 and the source527 / PR2159 / PR2160 /
PR2188 / PR2234 / PR2405 lineage. Their source bytes and notices are unchanged.
New proof audit and checker prepared for **mihir-s-05 with substantial OpenAI
Codex assistance**. Apache-2.0. No independent human or proof-kernel acceptance
is claimed.

## Open next questions

1. Independently reconstruct #4176's actual split-projector and fixed-chart
   inventory, including COPY's single chart application, then bind it to this
   lemma. This would discharge the inventory premise rather than infer it from
   a receipt. First compare actual generated bases/ranks/charts against the
   source compiler with independent rational arithmetic; the full source closure
   and a separately budgeted compiler replay are required.
2. Join the unit-weight and complete-cover multiplicity premises to one actual
   original-root ancestry path and its paid fallback. First trace one request
   through `Callback`, `selected_page` and the completed child contract at
   nonzero high digits. The full encoded ancestry and physical cost boundary
   are outside this package; further root digits would not close that gap.
