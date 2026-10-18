# Independent coverage audit of the five-b UT4 census

**Result:** the three-call single-label gap cap and four-call combined gap cap
used in [PR #2828](https://github.com/CrocSwap/integer-mult-bounds/pull/2828)
are sufficient for its opposite-orientation `(5,5,5)` cases, including calls
whose active projection is zero. A separate implementation reconstructs the
same **5,664 active profile pairs** and every bounded three-role gap table.

This supplies an explicit coverage argument for the truncations in
`build_gap_dirty`, `get_dirty_profs`, and `build_joint_dp` at reference head
`8a1000c09819b43ca9a8f2929788af4af40dab70`. It complements the author's full
exclusion and planted controls. It is a finite coverage/operator audit, not
another proof of the full arbitrary-workspace lower bound or a new kappa claim.

## Precise scope

Use the reference's quotient

```
Q = F2<A,B,C> / (A^2, B^2, C^2, AC-CA, degree >= 4).
```

There are two active roles `H` and one dirty role `K`. Every paid coupling is a
nonzero rank-one binary matrix `xy^T`; nilpotent and idempotent couplings are
both allowed. All five `b` couplings lie in `H x H`. In Case I, `a` may have a
dirty component in `x`, and `c` in `y`; Case II reverses these orientations.
There are 21 legal couplings for each outer label in each orientation,
including three with zero `H x H` projection.

The target is the quotient image of `diag([z],[uz],I_K)`, where
`z=I+E14` and `u=I+E13` in `UT4(F2)`. On `H`, it has coefficient `I_2` at
`1, ABC, ACB, BAC, CBA`, coefficient `S=diag(0,1)` at `AB, BA, ABA, BAB`,
and zero at the other basis elements. The reference's reduction from arbitrary
finite dirty workspaces to these orientations is **inherited**, not proved here.

Only `AC, ACB, BAC` can receive an interior dirty contraction in the active
block. Thus the other fourteen coefficient equations constrain the active
prefix profiles without knowing the dirty components or intra-gap order.
Indeed, a dirty contraction requires consecutive selected labels `c,a` in
Case I or `a,c` in Case II. After `CA=AC`, the only surviving basis monomials
containing that adjacent pair are `AC, ACB, BAC`; `ACA=CAC=0` and all degrees
at least four vanish.

## Coverage argument

Write `B_1,...,B_5` for the middle couplings. There are nine nonzero rank-one
`2 x 2` matrices. Their sum must be zero: enumerate the first four and set the
fifth to their XOR, rejecting a zero or rank-two fifth matrix. This gives all
3,600 middle sequences.

For either outer label, let `P_j` be its active prefix sum before `B_j`,
and set `P_0=P_6=0`. Its six gap increments and rank sum are

```
S_i = P_(i+1) + P_i,       i = 0,...,5,
rho(P) = sum_i rank(S_i).
```

Each projected paid call has rank at most one, so five calls necessarily give
`rho(P)<=5`. This is only used as a necessary condition; zero projected calls
are allowed. No parity or nonzero-active-call assumption is imposed.

Put `L_j=sum_(i<j) B_i` and `R_j=sum_(i>j) B_i`. The side equations are

```
sum_j P_j B_j                          = T,
sum_j B_j P_j                          = T,
sum_j P_j B_j P_j                      = T,
sum_j (L_j P_j B_j + B_j P_j R_j)       = T,
```

where `T=S` for `a` and `T=0` for `c`. For `a` these are `AB, BA, ABA, BAB`;
for `c` they are `CB, BC, CBC, BCB`. The remaining cross equations are

```
sum_j P^a_j B_j P^c_j = I_2,
sum_j P^c_j B_j P^a_j = I_2.
```

`profiles.py` enumerates all sixteen possible matrices at each of the five
prefix positions. A 2+3 meet-in-the-middle join matches the four side equations
and then checks the six gap ranks. This differs from the reference's split at
the middle prefix and packed multiplicity counters. The cross join represents
`B_j=x_j y_j^T` through the five columns `P_j x_j` and rows `y_j^T P_j`.
The identity cross-products require both associated row/column pairs to have
rank two, which justifies dropping singular keys. Exhausting these joins gives:

| Quantity | Count |
|---|---:|
| Middle sequences | 3,600 |
| `a` profiles passing side equations and `rho<=5` | 236,224 |
| `c` profiles passing side equations and `rho<=5` | 2,899,368 |
| Compatible transport-key pairs | 288 |
| Compatible active profile pairs | 5,664 |

These counts include multiplicity over middle sequences. The final profile
triples are unique. A direct expansion over all subsequences of degrees 1–3
checks all fourteen retained coefficient equations for every final pair.

For a fixed pair, let `r^a_i=rank(S^a_i)` and similarly for `c`. If gap `i`
contains `k^a_i` calls, every other gap needs at least its increment rank, hence

```
k^a_i <= 5 - sum_(h != i) r^a_h =: U^a_i,
k^c_i <= 5 - sum_(h != i) r^c_h =: U^c_i.
```

This remains true for pure-dirty calls. The complete profile enumeration gives

```
max_(pair,i) U^a_i = max_(pair,i) U^c_i = 3,
max_(pair,i) (U^a_i + U^c_i) = 4.
```

Equivalently, for every compatible pair and every gap, the combined rank demand
in the other five gaps is at least six. Therefore each label needs at most
three calls in a gap, and the combined total is at most four. **The reference's
truncations cover every word satisfying the necessary active equations.** The
bound is on a relaxation; attaining one of these upper bounds does not establish
the existence of a complete realizing word.

The `(rho_a,rho_c)` histogram is `(4,4):152`, `(4,5):760`, `(5,4):792`,
`(5,5):3960`. [RESULT.json](RESULT.json) records the full gap-cap histogram.

## Independent operator check

`gaps.py` builds the 21 couplings directly as `3 x 3` outer products. Within
an `a/c` gap only `1,A,C,AC` survive. A dynamic program retains the full
three-role `A` and `C` coefficients and multiplies them **before** projecting
the `AC` coefficient onto `H`. It never uses the reference's packed dirty
correction formulas. A separate literal enumeration supplies the single-label
tables, including the flag recording whether any dirty component was used.

For each orientation the joint table has **81,935 states**, representing
**2,798,629 words** over all `0<=k_a,k_c<=3`, `k_a+k_c<=4`, including the empty
word. Every count pair is checked against
`binomial(k_a+k_c,k_a) * 21^(k_a+k_c)`.

The optional comparison matched every table entry and multiplicity via canonical
SHA256 digests, and matched the entire sorted active-profile set, not just its
cardinality. Its profile-set digest is
`e19ab0445cd473806fb8e7e3d09b9a2911b65a4a02302720f3a7fe49e3be4961`.
The reference's differently defined digest also includes per-profile word counts;
it should not be compared directly to this digest.

Controls reject a changed middle coupling and gap caps of two/three that the
rank certificate cannot justify. A positive fixture uses `e_1 e_K^T` followed
by `e_K e_1^T`: both active projections vanish, while their product has active
coefficient `E11`. Reversing the order or multiplying only active projections
gives zero. Both orientations' gap tables must contain this fixture.

## Reproduce and evidence limits

From the repository root, using Python 3.12 and only its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/ut4-five-b-coverage-audit --check-only
python3.12 -B scripts/research_package.py --package research/ut4-five-b-coverage-audit
```

The second command rebuilds the result and checks the committed receipt; it
does not rewrite it. Measured generation time was 74.8 seconds on Python
3.12.14/Windows, with a 300-second replay limit. To explicitly regenerate the
receipt, run `verify.py --write-result`. The independent replay makes no network
requests and imports no predecessor code.

To repeat the comparison, export the files listed under `audited_reference`
in [SOURCES.json](SOURCES.json) from the
[pinned reference tree](https://github.com/steph4n-gh/integer-mult-bounds/tree/8a1000c09819b43ca9a8f2929788af4af40dab70),
retaining their repository-relative paths beneath `REFERENCE_ROOT`, then run:

```sh
python3.12 -B research/ut4-five-b-coverage-audit/compare_reference.py REFERENCE_ROOT
```

The adapter checks all source hashes before importing the reference. It observes
the reference's profile enumeration and also checks that every original census
output remains equal to its frozen receipt. Comparison took 9.2 seconds. The
author's original `verify.py` and `controls.py` were separately replayed and
passed; those reruns are **not independent implementations**.

This package does not independently reconstruct the dirty-prefix filters, the
final whole-word `AC/ACB/BAC` rejection, the other count splits, or the inherited
all-workspace compression and group-to-quotient proof. It does not establish a
native multiplication supplier. Only the selected-result binding/arithmetic
baseline was run, not the full selected supplier cold replay. No selected result
or predecessor file is changed.

Scientific inputs are pinned to main `b5e86d8104338796ce3cdf71666b6dbe72ec17fa`;
the submission refresh is recorded in [TASK.json](TASK.json). The original card
was `bit-new-register-model`, refined to a deliberately complementary audit of
pending work. Live PR searches were available; complete Discussion pagination
and authenticated Discussion posting were not. No advance reservation was posted.

## Open next questions

Independently reconstruct the remaining dirty-prefix equations and the final
three-coefficient rejection for all fifteen-call five-`b` splits. This would
test the remaining computational implication in #2828. Start from its then-current
pinned head and reuse these profile/gap digests, with a separate bounded audit.
No computational blocker is known; the inherited workspace-compression proof
still needs separate review. The structured handoff is in [TASK.json](TASK.json).

## Credit

The complete fifteen-call exclusion belongs to steph4n-gh's PR #2828. Its
predecessors include Gareth Davidson / bitplane (#2027, #2314, #2343), Nick
Petalas (#2175), ToikY (#1662, #1680), CinnaDavis / 1337isnot1337 (#1541), and
Aaron Wang / navinor's profile method (#1690). This package adds the separate
coverage certificate and operator comparison; it vendors none of their code.

Prepared for josecarlosgonzalezroque-design with substantial OpenAI Codex
assistance in analysis, implementation, verification and writing. No independent
human review or subagents. New work is Apache-2.0.
