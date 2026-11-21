# General tight-edge contraction: algebra, limits, and P104 controls

## Status and source

This is a paper proof plus exact finite Python controls, **not a Lean proof**.
It works with the general rational network model at
[`#7852` head `41beda1d6435760dc99e38bd7e65f36798aad212`](https://github.com/CrocSwap/integer-mult-bounds/pull/7852).
It neither proves nor refutes `NetD56`, and gives no legal-word instance:
`word_netW` is a word-to-network bridge, not a network-to-word bridge.

Principal source files are `research/p104-lowerbound-toolkit/lean/Nov15/`:

| File | SHA-256 |
| --- | --- |
| `NetContract.lean` | `2d561d34306cd1801c43df41951ed3bd3a120b8a5b2408ab4306b5c907302a58` |
| `NetBowtie.lean` | `c376512fc071b0edb94c9118aaa3d128617b51be08325e070bccc566cfe623c1` |
| `Net8.lean` | `8cfc0f3c86642c3ea6d9ddd61a51b9d4dfc60e3769635fd345445b2cab45e12f` |
| `DecoderWall4Data.lean` | `081bf16ed5e19930082ffb58548c6e6cded5c100f15332e797695e0cd07ef8c4` |
| `DecoderFacts.lean` | `9da74a8e7226ea4d785b3388505dc6fdcc92172d3a3e03fc6e788f2bd4a6bb77` |
| `BridgeNet.lean` | `a247e7da67d9d4496610c6e78faf5419bde95ced407ba7f389780b57795b400e` |

The source `DecoderWall4Data.lean` is Git blob
`90949f8d5dbcdee99974de505018768f4f9f640e`. `data_p104.json` is the local,
readable extraction of the 104 labels and 104 packed Gram rows from that file.
The eight-port frame used for the compact construction was independently
provided by the campaign's `19-challenge` lane. No credit is claimed for the
existing Lean series contraction, bowtie theorem, or E8 data.

## Exact cover-edge contraction

Notation matches `NetContract`: `F` has one row per node, `G` one column per
node, `H[k,j]` is an edge from `j` to `k`, and `M = G (I-H)^(-1) F`. Each
node has F2 subspaces `b_i <= a_i`. **The latter is an extra hypothesis for
abstract `NetW`**, supplied for word networks by `word_netW`. A nonzero
`F[i,p]` requires `q_p in a_i`; `G[s,i] != 0` requires `q_s` perpendicular to
`b_i`; and `H[i,j] != 0` requires `b_j <= a_i`. The drop is
`dim(a_i)-dim(b_i)`.

Suppose `H[k,j] = eta != 0`, the edge is tight (`b_j = a_k`), and the
directed graph has **no second path from j to k** after that direct edge is
removed. Other incoming edges at `k` and outgoing edges at `j` are allowed.
Identify `j` with `k`, retaining `k` and making `j` inert. Let all unlisted
entries be unchanged, and let `x,y` range outside `{j,k}`:

```
a'_k = a_j,                     b'_k = b_k
F'_k = F_k + eta F_j,           G'_k = G_k + G_j / eta
H'_ky = H_ky + eta H_jy,        H'_xk = H_xk + H_xj / eta
F'_x  = F_x - H_xj F_k / eta
G'_y  = G_y - G_j H_ky / eta
H'_xy = H_xy - H_xj H_ky / eta.
```

Here `F_i` is a port row and `G_i` a port column. Set all of the row and
column of `j` in `H`, its row in `F`, its column in `G`, and both its charts
to zero. The formulas can be used over any field; for words the field is Q,
so the inverse of every nonzero rational `eta` is admitted. The independently
verified Lean construction in `NetContract` handles the special case where
`k` is the only successor of `j` **and** `j` the only predecessor of `k`.

**Claim.** There is a topological reordering of the resulting network, its
drop is exactly the old drop, and

```
M' - M = (G_j F_k) / eta.
```

Thus all cells on which `q_s . q_p = 1` are unchanged, including each P104
diagonal. In particular a P104 `NetW` satisfying the extra `b_i <= a_i`
assumption remains such a `NetW` with its original `c_s`, after reindexing.
The equality does **not** hold in general on even cells, and the graph
reachability relation need not be unchanged.

**Derivation.** Write the node value as
`x_i = F_i u + sum_y H_iy x_y`. The equation for `k` gives
`x_j = (x_k - F_k u - sum_{y not j,k} H_ky x_y)/eta`. Substituting this in
the other equations gives the displayed matrices and the output correction
`-G_j F_k u / eta`. If that explicit direct input-output term is omitted,
the displayed equation for `M' - M` follows. If both `G[s,j]` and `F[k,p]`
are nonzero, `q_p in a_k=b_j`, while `q_s` is perpendicular to `b_j`;
therefore their pairing is zero. The correction vanishes on every odd cell.

All support obligations survive: for a new `F_x` term,
`q_p in a_k=b_j <= a_x`; for a new `G_y` term,
`b_y <= a_k=b_j`; and for a new `H_xy` term,
`b_y <= a_k=b_j <= a_x`. The other altered rows and columns use the same
inclusions, plus `b_k <= a_k=b_j <= a_j`. The original and contracted
drops at `j,k` agree because

```
(dim a_j - dim b_j) + (dim a_k - dim b_k)
    = dim a_j - dim b_k.
```

For acyclicity, contract the edge in the unweighted support graph and discard
its resulting loop. The quotient is acyclic exactly when there is no other
`j -> k` path. Every new nonzero matrix edge is either a quotient edge or
a shortcut of the quotient path `y -> [j,k] -> x`, so it is also acyclic.
A finite topological order supplies the required strict node order. The proof
does not require graph reachability to be preserved. The `01-net-small` lane
independently checked the substitutions, support implications, topological
argument, drop accounting and the extra `b <= a` premise on paper.

## Why the graph and bowtie gaps remain

The script checks the following separate controls with exact `Fraction`
arithmetic, exact F2 subspace membership, and exact rational matrix ranks.

* A 3-node merge with `eta=2` and another incoming edge of weight `1/2` has
  odd matrix `I_2` and drop 3. Applying the *existing* series formula after
  deliberately dropping its unique-predecessor premise loses a genuine path
  and changes the rational rank from 2 to 1. Keeping the other input without
  the required output compensation instead introduces the forbidden odd
  off-diagonal `1/2`. These are **negative controls on invalid extrapolations**,
  not counterexamples to the existing Lean theorem.
* An exact branching cover-edge contraction pays all four units of drop and
  preserves the odd transfer, but adds `u -> x` graph reachability. Its new
  direct edge of weight `-3/8` cancels an indirect path algebraically.
  A second cover-edge example deletes a formerly present `k -> x` path
  because two rational edge coefficients cancel.
* If `j -> x -> k` is a second path, exact substitution still preserves drop
  and odd transfer as a linear system, but produces a self-loop `-1/8`.
  That network is not an admissible DAG; the calculation does not rule out a
  different transformation.

There is also a P104-level obstruction to reaching bowtie by tight contractions
alone, at **D = 72**, with 9 gathering and 9 depositing nodes. The source E8
Gram gives an exact 8-row rational completion `M0` of rank 8, with each row's
source-label span of dimension 9; use eight isolated nodes with charts
`a=F2^9, b=0`, giving total drop 72. Starting with one such node `j`, add a
node `k` with `a_k=b_k=span(q_0)`, edge `H[k,j]=1`, and one gather and deposit
coefficient `F[k,0]=1, G[1,k]=1`. Replace `G[:,j]` by its former value minus
`G[:,k]`. Then

```
M = M0 + e_1 e_0^T;      q_1 . q_0 = 0.
```

The only changed transfer cell is even; all 104 odd diagonal requirements and
odd off-diagonals remain valid, including alternating `c_s=1/2,1` in the
control. `k` costs zero, so D remains 72. The sole edge is slack
`b_j=0 < span(q_0)=a_k`, hence no tight contraction can even start. Both
endpoints gather and deposit, so `BData.hgath` and `BData.hdep` force each to
be a hub; `hcomp` and the uniqueness of the component hub then contradict
the edge. Thus this actual P104 `NetW` is not bowtie and is terminal under
the existing or cover-edge tight-contraction rules. The checker also has a
simpler 105-node, D=105 diagonal-completion version.

This obstruction rules out that particular universal normalization claim,
not all possible normalizations, a decoder-wall proof, `D >= 56`, or any
legal-word property. The compact example has 9 gatherers and 9 depositors,
so the existing at-most-eight theorem is inapplicable.

## Replay

Requires Python 3.10+ only; no solver, Lean installation, or network access.
From this directory:

```
python3 check.py
python3 check.py /path/to/DecoderWall4Data.lean
```

The optional source path verifies its SHA-256 and compares both extracted
tables to the fixture. Executed with the pinned campaign export: all exact
controls passed; the compact completion's ordinary rational rank changes
from 8 to 9. The F2 chart calculations are distinct from those Q ranks.
The scripts are finite controls of the derivation, not a universal or
kernel-checked proof.
