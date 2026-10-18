# Exact source-XOR floor at seven queries

This is a scoped obstruction and sharpness statement in the five-source
common-B mutable-source alphabet of
[PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898).
It does not claim a new kappa, physical supplier tariff, or global unequal-price
optimum over all query counts.

It answers open question 1 of the path-lowered
`research/mutable-source-789q-invoice` lineage: whether a non-path XOR schedule
at seven queries can reach `X≤2` with `R=82` (tariff `≤436`). The answer is
negative for a stronger reason: **every restored seven-query word needs
`X≥6`**, path or non-path. The credited path-lowered champion attains `X=6`,
so the floor is sharp.

## Alphabet and restoration

Retain five distinct arbitrary-dirty F₂ source rows `x₀,…,x₄`, thirty-one
distinct arbitrary-dirty outputs `y_m`, a connector `z`, and private scratch.
Complete calls are `Q_j: z += B x_j`, `R_m: y_m += A_m z`, and paid
`X_(s,t): x_t += x_s`. The exit map is

```text
y_m += A_m B(sum_j bit_j(m) · x_j_initial),
```

with every source, connector and private scratch restored. Straight-line words
are data independent. Extra connectors, free copies, output mixing and
source-specific B maps are excluded. This is PR1340/PR1898's source-shear
alphabet.

## Interaction graph and component lemma

Build the undirected **interaction graph** on the five source labels: every
`X_(s,t)` contributes the edge `{s,t}`, including edges whose matrix effects
later cancel. Suppose the graph has `c` components `C_i` of sizes `n_i`.

Each query increment lies in the coordinate subspace of its source's component.
Connector restoration forces the sum of increments inside each component to be
zero, so the increments that touch component `i` span a space of dimension at
most `t_i − 1` whenever that component is queried `t_i` times. Covering the
`n_i`-dimensional source space on that component therefore requires
`t_i ≥ n_i + 1`. Every component must be queried (an unqueried component cannot
contribute its sources to the AB image while restoring). Summing yields

```text
Q = Σ t_i ≥ Σ (n_i + 1) = n + c.
```

Thus an interaction graph with `c` components forces at least `n + c` queries.
This lemma is the same component bound used by open
[PR2455](https://github.com/CrocSwap/integer-mult-bounds/pull/2455) at six
queries; the proof is reproduced here so the present package is freestanding.

## Census of restored XOR words through length six

A restored source-shear word of XOR-length `ℓ` is a product of `ℓ` elementary
shears that returns every source to its initial basis. Meet-in-the-middle on
`(source matrix, all-used-edge graph)` lists every restored interaction graph
at each length `ℓ ≤ 6` (PR2455 technique; digests match that package's
`RESULT.json` for lengths 0–6). Observed minimum component counts:

| X length | Restored graphs | Min components | Query floor `n+c` |
|---:|---:|---:|---:|
| 0 | 1 | 5 | 10 |
| 1 | 0 | — | — |
| 2 | 10 | 4 | 9 |
| 3 | 0 | — | — |
| 4 | 55 | 3 | 8 |
| 5 | 10 | 3 | 8 |
| 6 | 175 | 2 | 7 |

No length through six has a connected restored graph. In particular, every
restored word with `X ≤ 5` has query floor at least 8, so it cannot run at
exactly seven queries.

A coarser edge bound already excludes the 789q OQ1 target without the census:
any graph with `e ≤ 2` edges on five labels has `c ≥ 5 − e ≥ 3`, hence
`Q ≥ 8`. The census strengthens `X = 2` to `c ≥ 4` / `Q ≥ 9` and extends the
exclusion through `X = 5`.

## Sharpness at seven queries

The first XOR length whose census floor is `≤ 7` is `X = 6` (minimum
components 2). Therefore every restored seven-query word satisfies `X ≥ 6`.

The path-lowered closed prefix

```text
(0, 1, 2, 6, 12, 24, 16, 0)
```

attains `7 Q / 82 R / 6 X` under even-subset readout and path-local
compute/uncompute lowering (credited champion of the 789q invoice lineage).
Dirty root and inverse identities hold for the PR1898 abstract maps. Its
abstract complete-call tariff at `(b,a,x)=(38,2,2)` is 442. Attainment shows
the XOR floor is sharp.

## Scope limits

- No claim that seven-query words cannot undercut tariff 436 via a **lower R**
  than 82 with `X ≥ 6`. Readout minima under unrestricted non-path schedules
  remain open.
- No claim about eight or nine queries beyond the inherited path-lowered floors.
- No physical common-B hosting, precision, tape or selected-supplier invoice.
- No new kappa.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| PR1898 | Min `Q = 6`, min `R = 96` at that `Q`, `8 X` construction | — |
| PR2455 (open) | `X ≥ 8` at exactly six queries | — |
| 789q invoice (fork, path-lowered) | Path-class `Q∈{7,8,9}` invoices; OQ1 asks non-path `X≤2` at `R=82` | — |
| **This** | — | **`X ≥ 6` at exactly seven queries, sharp; rejects OQ1** |
