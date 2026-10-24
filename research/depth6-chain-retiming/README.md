# Two extra calls suffice for genuine depth-six chain retiming

This contribution was produced by Nick Petalas. It answers Open next
question 2 of [#4748](https://github.com/CrocSwap/integer-mult-bounds/pull/4748):
the least number of unsigned complete calls permitting a commuting
retiming in a binary depth-six dirty chain, without any cancellation
obtainable by commuting calls, is **22**. This is exactly two above the
known 20-call minimum.

The new result is a scoped construction and proof. Its lower bound uses
#4748's cited finite shortest-word classification at
`fc09e5b783989d769e6ae6fffeb7d23b30177c86`. This package neither imports nor
replays that classification. No new kappa or supplier admission is claimed.

## Exact question

Call l performs `z_l += B_l z_(l-1)`, for l=1,...,6. The source z_0 is
immutable. Every other register starts arbitrarily dirty; z_1,...,z_5
must be restored, and the only final change is

```text
z_6 += B_6 B_5 B_4 B_3 B_2 B_1 z_0.
```

The maps are arbitrary compatible linear maps over a nonzero unital ring
of characteristic two. Calls have equal unit prices. No inverse,
scaling, fused call, extra storage or other operation is allowed.

Distinct calls i,j commute universally exactly when `|i-j|>1`. Equal
calls cancel in pairs. Call a word commutation-reduced if no sequence of
these commuting swaps can expose adjacent equal calls. This is stronger
than merely having no equal neighbors in the displayed word. It excludes
an inserted cancelling pair even when that pair has been separated by
commuting calls. A retiming means one actual adjacent swap of distinct
commuting calls, giving a different chronological word.

## Construction and proof

Use the two words

```text
W = 1234656564321234565432
V = 1236456564321234565432.
```

They differ by swapping calls 4 and 6 at positions 4 and 5, counted from
one. Both have count vector `(2,4,4,4,4,4)` and length 22.

First, both are universally correct. Start with the known bridge word
`(1234565432)^2`, and replace its first `565` by `65656`. This gives W.
For two adjacent chain calls A,B in characteristic two,

```text
ABA = BABAB.
```

To see the identity with arbitrary maps, write A=I+X and B=I+Y. Here
X^2=Y^2=0 and one of XY,YX is zero. Thus
`(AB)^2=I+XY+YX`; the remaining product has square zero, so `(AB)^4=I`.
Since A and B are involutions, `ABABABAB=I` implies `ABA=BABAB`.
The identity works with chronological products in either convention.
Apply it to A=call 5, B=call 6. The swap giving V preserves the operator.
The bridge construction is prior work, credited below.

There is also a direct certificate independent of this substitution. For
every increasing interval i,...,j, count scattered occurrences of
`i(i+1)...j` in W or V. Its parity is the coefficient of
`B_j ... B_i` from the initial z_(i-1) to the final z_j. Every parity is
zero except the full interval 1,...,6, whose parity is one. This proves
correctness for arbitrary maps without assuming that maps commute.
The verifier emits all 21 integer counts for each new word.

Second, both words are commutation-reduced. For every two consecutive
occurrences of a call i, there is a call i-1 or i+1 between them. Such a
call fails to commute with either endpoint. Label occurrences individually.
Commuting swaps preserve the relative order of every pair of
noncommuting occurrences. Therefore the intervening call stays between
the two i occurrences until a deletion occurs. A first deletion is
impossible. Each word has 16 such consecutive equal-call pairs, and the
verifier emits a blocker position for every one. This proves the
noncancellation claim for arbitrarily many commuting swaps, without
searching their equivalence class.

Finally, 22 is minimal. Yifan Kang's Proposition 3.1 gives the known
20-call minimum. #4748's complete classification states that every
20-call schedule is a cyclic rotation of `(1234565432)^2`, and none has
an adjacent commuting pair. Every valid word has even multiplicity of
each call, because each singleton interval coefficient must vanish.
Hence length 21 is impossible. The displayed 22-call words attain the
first remaining length and are commutation-reduced. This last exclusion
of length 20 depends on #4748, rather than being a new independent proof
of its classification.

## Verification and reproduction

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/depth6-chain-retiming/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/depth6-chain-retiming/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/depth6-chain-retiming
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/depth6-chain-retiming --check-source-history
```

Any CPython 3.12 interpreter can replace the local path. Both registered
commands run the complete new certificate. The output is a generated JSON
receipt bound to the five package files, followed by

```text
PASS_DEPTH6_CHAIN_RETIMING calls=22 extra=2 blockers=32 scalar=16384 matrix=1792 relation=1536 controls=10
```

The direct interval-count and 7-by-7 matrix checks agree. Literal dirty
replays cover every choice of six binary scalar maps and seven initial
bits for both words, for 16,384 cases. Two-coordinate replay checks 64
deterministic six-map tuples on fourteen initial basis vectors for each
word, for 1,792 cases. The local three-call/five-call relation is checked
on all 256 pairs of binary 2-by-2 maps and six initial basis vectors,
for 1,536 comparisons. These finite checks support the written proof;
they do not prove the arbitrary-map statement by extrapolation.

Ten rejection controls cover four incorrect endpoints, a valid but
commutation-reducible 22-call word, two smaller reducible words, an
unknown call, the wrong characteristic for the witness, and the local
relation in characteristic three. Checks use explicit exceptions and
remain enabled under optimized Python. No predecessor verifier runs.

## Limits and implementation bounds

The exact 22-call threshold uses the cited #4748 classification. No
independent human or formal proof-kernel review is claimed. There is no
classification of all length-22 words, all-depth theorem, other-characteristic
result, unequal-price optimum or physical supplier implementation.
Routing, native preparation, dispatch, precision, tape/storage, recursive
admission and a complete multiplication theorem remain outside scope.
The selected frontier stays unchanged.

The standalone verifier has no recursion, subprocess, network or file
writes. Inputs are fixed words of at most 22 calls; literal state size is
at most seven two-bit registers. All loops have fixed finite bounds in
code, and every function is below 60 lines. Explicit exceptions enforce
word, map and register ranges and the mathematical invariants. Standard
Python container and integer allocation is a managed-runtime deviation
from fixed-allocation operation. Its scope is this bounded one-shot
verifier, compensated by fixed case counts and a one-MiB limit per hashed
package file. Follow up with fixed-capacity buffers only if this checker
becomes a long-lived service. Warning-strict normal and optimized replay
supply the local interpreted-language diagnostics; no separate static
type checker or compiled build is claimed.

## Open next questions

1. How many commutation-reduced length-22 schedules are there, and how
   many commuting-equivalence classes do they form? Start with a bounded
   near-shortest-path search. The present result proves existence and the
   exact threshold, not a census.
2. Can the no-retiming statement at length 20 be proved structurally,
   replacing the dependence on #4748's finite classification? Start with
   the known minimum count vector and forced chronological dependencies.
3. Does an actual six-stage supplier consumer benefit from this extra
   retiming freedom? Name its maps and charge routing, frame changes and
   restoration before interpreting the abstract two-call cost as savings.

## Credit

Nick Petalas's #4748 supplies the exact shortest-word classification and
this open question. The original contribution here is the exact
commutation-reduced retiming threshold and its explicit witnesses.
Yifan Kang's [CNOT-Optimal Circuit Synthesis, Proposition 3.1](https://math.mit.edu/documents/rsi/2023KangY.pdf)
supplies the known directed-path minimum and bridge construction, building
on the construction attributed there to Nash et al. Nick Petalas's
#4249/#4263/#4281 supply the chain model and interval-count reduction;
Ryanson Jonathan's #4418 addresses separate depth-five residues. Ross
Richardson's #943/#934 lineage supplies the complete-call dirty connector
interface. The involution identity and the blocker argument are elementary
algebra and commutation arguments, not new general group-theoretic claims.
Apache-2.0.
