# Source-union cuts for shared snapshot networks

The twelve rank-five candidate networks cannot give a cheaper centre
query. Each requested subspace of dimension `k` needs at least `9k`
native rank in the model below. The bound includes shared rank-one
prefixes. It follows from five source tests, each of which is injective
on the candidate query space.

The same test also gives bounds for the displayed rank-three and
rank-four query spaces. This note does not give a bound for a network
that joins different merge spaces or uses an unlisted intermediate
frame.

## Model and source premise

Use the pinned backward clean-J word and its exact snapshot rows. Put
`X=JY` and set every helper and private input to zero. Then all completed
X rows and all restored helper rows are zero. This is a valid input
family for any proposed algorithm that works on arbitrary inputs.

The independently checked snapshot support law states that a snapshot
at canonical frame `U` uses only source ports whose labels lie in
`U` perpendicular. This law holds at all listed snapshot times. The
full snapshot table has 712 input columns. Its earlier quotient does
not discard the 78 helpers that have non-FULL final frames.

Fix an actual merge frame `V` of dimension `d`. Permit all times of all
retained observations at actual positive-rank frames contained in V.
Permit every monotone native edge `U -> W` between these frames, with
cost `(dim W - dim U)` per carried field. Equal-frame scalar operations
can split, add, and cancel fields. Thus one paid field can serve several
output queries. After the requested query fields reach V, no new
observation enters. Their completion to FULL9 has cost at least
`(9-d)k` for `k` independent queries.

This model grants more access than a chronological native word. An
obstruction in this model needs no claim that all granted edges have
the indicated phase-correct recipe. It does not permit a change to
the retained core or a change to the source-port meaning of a frame.

## Union-cut lemma

For a nonzero character `alpha` on V, let `E_alpha` be the source ports
whose label restricts to alpha. Let `Omega_alpha` be the nodes U at
which alpha does not vanish. For a set A of nonzero characters, put

\[
 E_A=\bigcup_{\alpha\in A}E_\alpha,
 \qquad
 \Omega_A=\bigcap_{\alpha\in A}\Omega_\alpha.
\]

Test inputs Y supported on `E_A`. Every free observation at a node in
`Omega_A` is zero by the support law. The set `Omega_A` is upward
closed. Hence the required query values on these inputs must enter
it through native edges. If the query space has coefficient matrix
S in the eight R rows, this cut has demand

\[
 r_A=\operatorname{rank}((SR)_{E_A}).
\]

Assign nonnegative rational weights to these cuts. If the sum of the
weights of the cuts entered by every edge `U -> W` is at most
`dim W - dim U`, then the weighted sum of demands is a lower bound
for native rank before completion. This proof permits arbitrary
sharing and cancellation. For payload dimension N, demands and edge
capacities both multiply by N, so the bound in field units is unchanged.

A useful stronger case occurs when restriction to `E_A` is injective
on the entire displayed query space. Then it is injective on every
subspace of that space. The same cut has demand k for every requested
subspace of dimension k. If all positive-weight cuts have this property
and their weights sum to w, the total bound is

\[
 (w+9-d)k.                                                \tag{1}
\]

## Finite cut construction

The checker starts with all singleton and pair character sets, plus
the final-V cut. It merges equal inside-node sets. For each resulting
node set I, it uses every character whose singleton cut contains I.
The intersection of those singleton cuts is still I. This change can
increase the tested source set without changing any edge charge.

A floating-point simplex calculation selects candidate weights. The
checker then reconstructs rational weights and checks every edge
charge exactly. It computes all source restriction ranks over the
rationals. The certificate does not depend on the correctness or
optimality of the floating-point solve.

## Rank-five result

The merge frames are

```text
630, 631, 632, 633, 635, 637,
734, 735, 736, 737, 739, 741.
```

Each displayed query space has dimension five. In each case the
certificate has five positive cuts, each with weight one and full
restriction rank five. Thus `w=5` and `d=5` in (1), which gives `9k`
for every requested subspace. In particular, all five queries cost
at least 45 native rank. The target for a strict improvement was less
than 40.

The first six cases use 288 distinct closed cuts. The last six use
328. Only five cuts per case are needed in the accepted certificate.
The checker stores the exact source ports, node sets, query bases,
weights, and every inclusion edge.

## Other displayed spaces

The separate full-rank-cut checker applies the same argument to the
74 displayed maximal-overlap query spaces from the bounded screen.
It gives the following per-query bounds on every subspace of each
displayed space:

| Merge cases | Number | Bound per query |
|---|---:|---:|
| Rank-three cases | 24 | 9 |
| Rank-four cases with frame ID at most 414 | 14 | 8 |
| Rank-four cases with frame ID from 592 to 629 | 24 | 9 |
| Rank-five cases | 12 | 9 |

These certificates prove bounds for the displayed exact coefficient
spaces. The initial classification of their full observation overlap
was modular. It is not promoted here to an exact classification of
all query spaces at all merge frames. The independent rank-five
review checks the full 712-column overlap separately.

## Validation and scope

Run from the repository root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/history-encoding/check_rank5_union_cuts.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/history-encoding/check_low_birth_full_rank_cuts.py
```

The receipts are `RANK5-UNION-CUTS.json` and
`LOW-BIRTH-SUBSPACE-CUTS.json`. They pin their producers and source
receipts. The snapshot payload has decompressed SHA256
`3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c`.
The separate source-row review is
`circuit-interface/snapshot-audit/SNAPSHOT-ROWS-REVIEW.json`.
The separate support review is
`cover-algebra/SNAPSHOT-SUPPORT-REVIEW.json`.

No improved native word, complete supplier cost, universal bound of
64, or optimum over all snapshot networks is claimed. The remaining
models include networks that cross between merge spaces, larger
merge frames, synthetic intermediate frames, and changed core or
query interfaces.

The root research agent proposed pair-union source tests. The
history-encoding lane implemented the exact cut certificates and
the selective-subspace consequence. The cover-algebra lane is the
independent reviewer of the rank-five certificate.
