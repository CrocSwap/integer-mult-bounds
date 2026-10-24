# Four graph frames require a relative operator

Two ordered quadruples of graph frames admit one common invertible map exactly
when their relative operators are similar. [PROOF.md](PROOF.md) gives the
all-field criterion, a constructive cyclic-module basis algorithm, and the exact
finite-field number of realizing maps, including nonsemisimple blocks and an
explicit unused ambient complement. This answers the complementary-graph first
case of **Open next question 2** in Nick Petalas's
[three-frame package](../three-frame-shared-map/README.md) (#4919).

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Claim type: **scoped proof with finite exact corroboration**. Similarity,
rational canonical form and primary-module algebra are classical background,
with no literature-priority claim. No new kappa or supplier admission is claimed.

## Contract and construction

In active coordinates U=A direct-sum B, dim A=dim B=r, let the ordered frames be
A, B, graph(L), graph(M), with L invertible and M arbitrary. Their target
counterparts use L',M'. All four frames lie inside U; an unused complement of
dimension s is retained explicitly. Put T=L^-1 M and T'=L'^-1 M'. A shared
map exists if and only if there is an invertible S satisfying S T=T' S.
Its active block matrix is diag(S,L' S L^-1). The proof constructs S from
matching rational cyclic bases over any field; it never assumes diagonalization.

If the invariant factors differ the finite-field count is zero. Otherwise,
for each monic irreducible p of degree d, let its primary block sizes be lambda,
let h_l count blocks of size at least l, and let m_j count blocks of size j:

```
active_count = product_p q^[d*(sum_l h_l^2 - sum_j m_j^2)]
                         * product_j |GL_(m_j)(F_(q^d))|,
ambient_count = active_count * q^(2rs) * |GL_s(F_q)|.
```

The complement factor counts arbitrary upper-right shear and arbitrary
invertible complement action. It is not an unpriced native operation or erasure.

`core.py::complete(L,M,Lprime,Mprime,q,unused=0,shear=None,complement=None)`
returns compatibility, active/ambient counts and a concrete map. Its executable
reference is deliberately bounded: prime q in {2,3,5}, r<=4, 2r+s<=9 and at
most 4096 coefficient choices in the intertwiner solution space. Exceeding
that limit is an explicit rejection, not evidence of incompatibility. Matrices
use canonical integer entries and act on column vectors. The written all-field
algorithm and formula have no such finite-experiment bounds.

## Why dimensions and characteristic polynomial are insufficient

Binary companions of t^3+t+1 and t^3+t^2+1 give two quadruples of pairwise
complementary three-frames. All individual, intersection and sum dimensions
agree, but the characteristic polynomials differ, so no common ordered map
exists. Embedded in six active plus three unused coordinates, the compatible
self-case has exactly **308,281,344** maps, not merely seven active realizers.

There is also a stronger nonsemisimple control: for p=t^2+t+1 over F2,
companion(p^2) and two copies of companion(p) have the same characteristic
polynomial and pairwise complementary graph frames, but primary partitions
(2) and (1,1) differ. Their self-centralizer counts are 12 and 180, respectively.
Thus characteristic polynomial alone cannot replace invariant factors.

## Independent finite evidence

The literal verifier enumerates all linear operators and invertible vector
permutations in three complete domains. It constructs conjugacy orbits using
only those permutations, independently of the primary classifier. For every
operator it compares the invariant, centralizer formula and **every** invertible
intertwiner with the literal realization set:

| Field | r | Operators | GL size | Similarity orbits |
| --- | ---: | ---: | ---: | ---: |
| F2 | 2 | 16 | 6 | 6 |
| F3 | 2 | 81 | 48 | 12 |
| F2 | 3 | 512 | 168 | 14 |

That is 609 operators and 32 orbits. Eight additional binary primary fixtures
have counts 168, 4, 8, 7, 12, 180, 96 and 4, covering scalar zero, nilpotent
Jordan blocks, irreducibles, repeated blocks and mixed primary components.
An independent bit-vector oracle enumerates all matrices on their underlying
r<=4 spaces, without using the polynomial/elimination code. No ambient GL9
enumeration is performed.

Literal vector sets verify all four images and invertibility of the emitted
nine-dimensional map, including nonidentity L,L', arbitrary supplied shear
and a nontrivial complement map. Singular fourth graphs, directed ternary
intertwining, zero active dimension, a prime-five positive control and sixteen
malformed/boundary-input rejections are included. Runtime checks survive `-O`.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
python3.12 -Werror -B research/four-frame-shared-map/verify.py
python3.12 -O -Werror -B research/four-frame-shared-map/verify.py
python3.12 -Werror -B scripts/research_package.py --package research/four-frame-shared-map
python3.12 -Werror -B scripts/check_research_commit.py --package research/four-frame-shared-map --check-source-history
```

Expected direct output is `PASS_FOUR_FRAME_SHARED_MAP` with `operators=609`,
`orbits=32`, `primary_fixtures=8` and `native_self_realizers=308281344`.
`RESULT.json` binds proof, code, metadata and live source bytes, and is compared
to exact recomputation with Boolean/integer distinctions retained. Ordinary
verification writes no artifact. `--write /a/new/path.json` generates a receipt
and refuses an occupied path. Use `scripts/export_research_package.py export`
and `check` for an official committed export; direct verification needs only
the package and its four declared live inputs, and works without Git.

## Source binding and limits

Base canonical main is `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`.
[SOURCES.json](SOURCES.json) records exact commit/blob/SHA256 pins for #4919's
README and proof, and Cao Yifan's `constrained_map.py` and `helper_line_milp.py`.
The predecessor files are authenticated as context and never imported or run.
The original card and selected record are Git provenance; [TASK.json](TASK.json)
explicitly changes scope from a cost improvement to this algebraic side result.
Canonical claim: [Discussion #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19140243).

No actual emitted source operator with four independent graph contacts has
been established. Arbitrary four-subspace systems, vector-value constraints,
symplectic restrictions, absolute phase, a whole native word, owners, restoration,
precision, tape costs and a complete supplier remain outside this theorem.
Finite experiments corroborate the written proof; they do not prove the
all-size multiplication theorem. Independent human/proof-kernel acceptance is
unclaimed. No native optimization, MILP, historical scientific suite, Lean or
Docker replay is needed for this algebraic contract.

## Open next questions

1. Locate one actual emitted shared-G occurrence with four independent graph
   image constraints, and derive L,M,L',M' from its source. This decides whether
   the invariant changes a real caller. The present source only establishes
   a line-preservation/subspace-capacity contract; four graph contacts are a blocker.
2. Add specified vector actions or symplectic/phase restrictions to that exact
   occurrence before counting its admissible completions. First intersect the
   intertwiner space with those literal constraints. The unresolved physical
   operator, ownership and full invoice prevent any paid-savings claim now.

Retain Nick Petalas's #4919 three-frame result and Cao Yifan's PR4610 native
map/helper work, together with their credited supplier, transported-frame,
native/compiler and recursion contributors. No predecessor result is re-audited.
