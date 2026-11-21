# Support-saturated chart normalization for nested networks

This is an elementary paper reduction with exact finite controls; it is not
Lean-checked and does not prove `NetD56`. The model is pinned by
`README.md` to `#7852` head `41beda1d6435760dc99e38bd7e65f36798aad212`.
The result applies to rational `NetW` networks **with `b_j <= a_j` at every
node**. That additional premise is supplied by the upstream word bridge;
it is not a field of abstract `NetW` itself.

## The normalization

For a fixed network, put `V = F2^9`. At node `j` define the input span and
output constraint

```
L_j = span({q_p : F[j,p] != 0} union {b_y : H[j,y] != 0}),

U_j = (intersection over s with G[s,j] != 0 of q_s-perp)
      intersect (intersection over x with H[x,j] != 0 of a_x).
```

The span of an empty collection is `0` and an empty intersection is `V`.
Change only node `j`'s charts:

```
a'_j = L_j,                 b'_j = L_j intersect U_j.
```

Leave all other charts, matrices `F,G,H`, labels and `c` unchanged. Then:

1. The new network is legal and still satisfies `b <= a` at every node.
   Inputs to `j` land in `L_j`; the new `b_j` is inside every outgoing
   chart and orthogonal to every output label. All unaffected incidences
   remain legal.
2. Its drop at `j` is exactly

   ```
   r_j = dim L_j - dim(L_j intersect U_j)
       = rank(L_j -> V / U_j).
   ```

   This is no greater than the old drop. Indeed `L_j <= a_j`, while the old
   nested `b_j` lies in both `a_j` and `U_j`, so

   ```
   rank(L_j -> V/U_j) <= rank(a_j -> V/U_j)
                       <= dim a_j - dim b_j.
   ```

   Equivalently, this rank is the rank over **F2** of the pairing matrix
   between generators of `L_j` and generators of `U_j-perp`. The network's
   transfer coefficients themselves remain arbitrary rationals; no modular
   reduction of those coefficients is assumed.

   It is the **minimum possible local drop** with the other nodes' charts
   and the same `F,G,H`: every alternative legal `a*` contains `L_j`, and
   every alternative nested `b*` lies in `U_j`, forcing
   `dim a* - dim b* >= rank(L_j -> V/U_j)`.
3. The directed support graph, the reachability preorder on all input and
   output terminals and retained nodes, and the complete rational matrix
   `G(I-H)^(-1)F` are **identical**, because none of `F,G,H` changes. Thus
   all P104 odd cells and diagonal coefficients remain the same, as do node,
   gatherer and depositor counts.

Apply this operation repeatedly to every non-normal node. This terminates:
every update has `a'_j <= a_j`. If this inclusion is strict, `dim a_j`
decreases. If equality holds, old `b_j <= a_j intersect U_j=b'_j`, so a
nontrivial update strictly increases `dim b_j`. Consequently the
lexicographic potential

```
(sum_j dim a_j,  sum_j (9 - dim b_j))
```

strictly decreases in a finite set. At termination, every node simultaneously
satisfies `a_j=L_j` and `b_j=L_j intersect U_j`, computed using the **final**
neighboring charts. Every update is non-increasing in total drop. This is a
normal form, not a claim that the globally resulting chart assignment is
unique or globally minimal among all simultaneous chart assignments.
Updates must be **sequentially recomputed** against the current neighboring
charts. Applying independently computed changes from stale charts in one
batch can violate a relay: for `j -> k` with both old `a=span(q)`, both old
`b=0`, and a single input of `q` at `j`, the stale local results are
`b'_j=span(q)` and `a'_k=0`.

**Reduction.** If `D >= 56` is proved for every nested, support-saturated
P104 `NetW`, it follows for every nested P104 `NetW`: normalize an arbitrary
one without changing its `F,G,H` or odd-cell requirements, and use
`D(original) >= D(normalized)`. The resulting network need not be the
network of an actual word, and the reduction does not require it to be.

## Controls and remaining problem

The exact standard-library program `tighten.py` independently implements
the updates and checks the lexicographic descent, legality after every update,
unchanged `F,G,H`, full transfer equality and drop inequality. Its synthetic
two-node network normalizes from **D=5 to D=2** in two updates, including a
changed relay chart. A separate negative control checks the stale-batch
failure above. An exhaustive F2^3 control checks the minimum rank invoice
against all legal chart assignments for all 256 input/output subspace pairs.
The script also consumes the source-checked lane 01 construction:

* The actual P104 8/8 equality network has **D=56** and is already a fixed
  point, with zero updates.
* The actual P104 9/8 `D=56` example with **two distinct low gatherers** is
  also already a fixed point. Thus saturation alone does not discharge lane
  01's remaining two-low obstruction or yield a bowtie structure.

The normalization does not assert `D` remains equal to the original drop;
each local decrease is an explicit rank difference. It does not claim that
a normalized graph is realizable by an actual verifier word, that it has at
most eight gatherers/depositors, or that it reaches a bowtie. Those gaps are
separate from the exact reachability, transfer and invoice statements.

Replay alongside `README.md`'s `check.py` and `ROUTING.md`'s `zero_drop.py`:

```
python3 tighten.py /path/to/01-net-small
```

The sibling directory supplies `check_separator.py`, `p104_roots.json` and
the pinned Lean source files for the optional byte comparison. The recorded
run completed with all exact checks passing. Lane 01 independently reviewed
the local minimum, sequential relay support, termination and P104 fixed-point
controls; no Lean build was run.
