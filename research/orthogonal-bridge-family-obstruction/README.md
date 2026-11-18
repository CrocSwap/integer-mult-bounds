# No rank saving for the orthogonal fresh-bridge family

An arbitrary old orthogonal binary projector basis plus the prescribed
family of b orthogonal fresh-coordinate links cannot save paid rank under
the stated relation budget. Use `Z=I_b+(N modulo 2)J_b` for the fresh
covectors and require `N*b` even, so Z is invertible. At b=2 these are
the links from [PR #7707](https://github.com/CrocSwap/integer-mult-bounds/pull/7707).
Every type must occur. The exponent group must be paid-generated,
torsion-free and abelian. The saturated relation rank must be at most
the actual pattern dimension k, and the full ambient endpoint must be
diagonal monomial. No additional projector type is allowed.

No old call can lie between the first and last occurrence of any bridge
type. All bridge types commute, so their calls can interleave. Each type
can be collected into one block without crossing an old call. All block
totals are zero, and deleting them preserves every ambient input. Each
physical target exponent is then a sum of a disjoint paid subset. Rank
subadditivity gives total target rank at most paid rank. No new kappa follows.

PROOF.md states the all-width and all-length theorem. RESULT.json records
the finite checks. The star rank is Nb for odd old dimension and `Nb-b+1`
for even old dimension. Independent sets of bridge variables force the
chronology despite the b-1 star dependences in the even case. The actual
pattern dimension is `k=N-d+b`, where d is the old Boolean partition size.

The named pair/triple attaining alphabets of PR #7707 are covered when
all their members occur and the relation budget holds. At (k,nu,n)=(4,0,5),
the source's complete pool has a sixth projector. That extra type changes
the first-order equations and is excluded. Other even maximizers, larger
relation budgets and arbitrary fresh embeddings are outside the theorem.
The old geometric maximum remains a source result.

## Reproduction

Use CPython 3.12 and the standard library from the repository root:

```sh
python3 -B scripts/research_package.py --package research/orthogonal-bridge-family-obstruction
```

For a standalone package:

```sh
python3 -I -W error -B research/orthogonal-bridge-family-obstruction/verify.py
python3 -I -W error -B -O research/orthogonal-bridge-family-obstruction/verify.py
```

Both modes print:

```text
PASS_ORTHOGONAL_BRIDGE_FAMILY_OBSTRUCTION
20335 bases; 81002 basis/bridge checks; 55250 full Laurent words; 10148 passing orders
15 larger fixtures; all bridge totals vanish in the stated class.
```

The basis census covers all GL_N(F2) for N=1,2,3,4, with actual physical
partitions and star quotients. For each permitted b from one through four,
this gives 81002 basis/bridge-count checks. All 55250 word orders have
degree-two and complete Laurent checks. A separate gap count confirms
the 10148 passing orders. Fifteen larger fixtures through old dimension
ten and up to six bridges include repeated old calls, three calls of one
bridge, literal interleavings and unused spectators. Complete deletion
and physical target labels agree.

Removing a bridge call changes an arbitrary fresh-input column. Twenty
wrong-parity links fail idempotence. Identifying bridge variables adds a
relation and hides a quadratic rejection, but the full endpoint still
fails. The sixth-projector control checks its changed first-order kernel.
Twelve odd-N, odd-b fixtures have explicit common-kernel vectors and are
rejected for their singular fresh pairing. Two further controls separate
exact exponent totals from parity and check use of the paid-generated
group. These controls do not assert that a larger class saves rank.

The source routines and proof methods are adapted, with explicit pins in
CREDITS.md. Their full suites were not rerun. No selected cold replay,
native or physical implementation, Lean, Docker, human or formal-kernel
review was run. All five selected assumptions remain. The result supplies
no complete multiplication invoice and changes no selected frontier.

## Task and overlap

Base: current main `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8. The `bit-helper-contract` card is narrowed to this full-endpoint
word obligation. The selected binding check passed. Live handoffs,
source-reference intake and phrase searches found no competing claim
for this bridge-family word theorem. The complete closed cache and its
updated-order delta were checked. Sparse local and unpublished work
remain limitations. The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19710858)
records the original two-link task and its explicit generalization within
the same result. This is a bounded proof continuation, not a new native
construction.

## Open next questions

1. Can the exceptional six-projector pool support a saving? Start with its
   coupled first-order totals. The present bridge-variable separation
   does not apply. Keep the actual relation rank and full endpoint.
2. Do other even maximizing pools or specified extra relations admit a
   legal word? State the exact alphabet and paid/target invoice first.
   Failure of this theorem's hypotheses is not evidence of a saving.

Prepared by Ali Romman with substantial OpenAI Codex assistance under
Apache-2.0. Credit CubeJerry for the original chronology and Laurent
methods, Ali Romman for the consumed arbitrary-basis extension and
two-link geometry, and the earlier contributors named in CREDITS.md.
