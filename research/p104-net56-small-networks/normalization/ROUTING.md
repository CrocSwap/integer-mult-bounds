# Reachability-preserving routing with a rank invoice

This paper argument and the finite controls in `zero_drop.py` are additional to
the cover-edge contraction in `README.md`. They use the same pinned `#7852`
head. This is not Lean-checked and does not establish `NetD56` or legal-word
realizability. The original P104 `D=56` network and data are due to the
`01-net-small` campaign lane; its exact source and replay are described there.

## Local routing construction

Expand a directed rational network as a graph with separate input terminals
`p`, output terminals `s`, and relay nodes `j`. An input edge `p -> j` exists
when `F[j,p] != 0`, an output edge `j -> s` when `G[s,j] != 0`, and a relay
edge `y -> j` when `H[j,y] != 0`. All retain their matrix coefficients.

Choose any relay node `j`. For each incoming incidence `u` set

```
L_u = span(q_p)   if u is input port p
      b_y         if u is a relay from node y.
```

For each outgoing incidence `v` set

```
U_v = q_s-perp    if v is output port s
      a_x         if v is a relay to node x.
```

Replace `j` by a separate new node for **each pair** `(u,v)` of one incoming
and one outgoing incidence. The only input edge into that copy is `u`, with
its original coefficient, and the only output edge is `v`, also with its
original coefficient. Its charts are

```
a_(u,v) = L_u,             b_(u,v) = L_u intersect U_v.
```

All other nodes and incidences stay as before. Insert the new nodes at the
topological position of `j`, or reindex afterwards. If either incidence list
is empty, simply remove `j`.

This construction has the following exact properties:

1. **Chart and relay support:** an input label is in its copied `a`; an
   incoming relay brings `b_y=L_u`; an output relay has
   `b_(u,v) <= U_v=a_x`; and an output port is perpendicular to
   `b_(u,v) <= U_v=q_s-perp`. Every copy satisfies `b <= a`. Other node
   obligations are unchanged.
2. **All terminal and retained-node reachability:** each path through `j`
   enters and leaves by exactly one incidence pair. Replace that visit by
   the unique corresponding copy. Conversely, map a copy back to `j`. A DAG
   cannot visit `j` twice, so these maps give a weight-preserving bijection
   between directed paths. Thus the support-graph reachability relation
   between *all retained nodes and all separate input/output terminals* is
   preserved exactly, without assuming that algebraic path sums are nonzero.
3. **Full rational transfer:** the same path bijection preserves every
   product of edge coefficients. Hence `G(I-H)^(-1)F` is identical on every
   cell, including even cells, and the original diagonal values `c_s` remain.
4. **Explicit invoice:** the copy's exact drop is

   ```
   r_(u,v) = dim L_u - dim(L_u intersect U_v)
           = rank(L_u -> F2^9 / U_v).
   ```

   This is the smallest possible drop for an individual copy with input
   `L_u`, output constraint `U_v`, and `b <= a`. The new total drop is the
   old total minus the old drop at `j`, plus `sum_(u,v) r_(u,v)`. This is a
   *charged construction*, not a proof that the sum is the minimum possible
   for every more general normalization.

For a word-bridge network, `b_j <= a_j`. The original support laws imply
`L_u <= a_j` and `b_j <= U_v`; hence each individual
`r_(u,v) <= dim(a_j)-dim(b_j)`. **Their sum need not obey this bound.**
Thus the construction preserves all semantics and records every unit paid,
but does not by itself prove a cost-nonincreasing reduction or D ≥ 56.

## Zero-drop corollary

If `a_j=b_j=C`, all `L_u <= C <= U_v`, so each copy has `a=b=L_u` and
drop zero. The procedure therefore breaks any zero-drop merge/split into
degree-one routing nodes **for free**, while preserving all graph-terminal
reachability and the entire transfer matrix. Unlike an algebraic shortcut,
it does not silently erase a path when signed rational coefficients cancel.
It may create up to `(#incoming incidences) × (#outgoing incidences)` copies,
and can increase gatherer/depositor counts. It does not resolve branching
at positive-drop nodes.

The `zero_drop.py` generic control has three incoming and three outgoing
incidences, so it makes nine zero-drop copies. One preexisting route and one
route through `j` cancel to make a terminal transfer entry zero; the graph
path still exists before and after normalization. The script checks all
retained-node/input/output reachabilities, full Q transfer, every chart and
relay, per-copy incidence counts, and total drop. A separate positive-drop
three-port control invoices 7 after replacing a node of drop 3, while
preserving the full transfer and graph reachability.

The blow-up is not just a synthetic possibility. On node 0 of lane 01's
actual 8/8 P104 equality witness, there are 52 nonzero input-port and 52
nonzero output-port incidences. The per-pair invoice above makes 2,704 copies
and sums to **1,462**, versus the original node's drop **7**. The script
counts the precise 1,462 odd label pairs from the pinned witness; it does not
allocate the 2,704-node network. This is a calculation for the stated
per-pair procedure, not a lower bound on every alternative transformation.

## Equality example against tight-contraction-only normalization

Starting from lane 01's checked P104 8/8 network at `D=56`, take node `j=0`
with `a_j=7-perp` and `b_j=span(67)`. Add `k` after `j` with

```
a_k = b_k = span(67, 11),  H[k,j] = 1,
F[k,0] = 1,                G[1,k] = 1,
G[:,j] := old G[:,j] - G[:,k].
```

All other entries agree with the original eight nodes. The pinned labels
are `q_0=11`, `q_1=19`; their dot product is zero, and `19` is also
orthogonal to `67`. The only transfer change is the even cell `(1,0)`, by
`+1`. With `c_s` alternating between `1/2` and `1`, the exact checker verifies
every odd target and every support law. The new node has drop zero, so total
`D=56`; there are 9 gathering and 9 depositing nodes. The only edge is slack
`span(67) < span(67,11)`, so there is no tight edge. Both endpoints gather
and deposit, forcing two distinct bowtie hubs in one relay component, which
is impossible. Thus tight contractions alone cannot always reach bowtie,
even on the equality boundary of the actual P104 network model. This is not
a counterexample to `D >= 56` or a claim about legal words.

In this example the free zero-drop routing procedure replaces the new node
with two copies and removes that particular obstruction. Nothing here proves
that the resulting network always has bowtie data, or that the rest of a
general network can be handled without extra cost.

## Reciprocal review and replay

`zero_drop.py` loads `check.py` here and the sibling `01-net-small` lane's
`check_separator.py` and `p104_roots.json`. That checker ties its two tables
to the pinned `DataIdA.lean` and `DecoderWall4Data.lean` when the source
files are present. Run

```
python3 zero_drop.py /path/to/01-net-small
```

The executed run passed the two routing controls, the P104 `D=56` obstruction,
and its zero-drop normalization. It also verified the lane 01 reversal with
nonconstant `c_s`, checking all 104-by-104 entries for exact transpose and
all nine individual drops. The source check and code review independently
confirmed lane 01's 8/8, 9/8, and 8/9 examples, including its two-low 9/8
example and dual. No Lean compilation or kernel replay was performed here.
