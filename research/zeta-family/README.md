# The zeta family: Boolean-lattice finite networks

Under the retained fixed-alphabet interfaces, the construction below compiles
through the merged in-tree compiler
(`scripts/paired_cube/frames.py::compile_graph`, the #144 path) and its profile
prices through the in-tree assembly (`scripts/structured_bulk_assembly.py`) with
both sides configured at the family saving (the two-sided projection; the
bit-side realization is an open obligation, see D):

| h | v | R | R/v | saving (both sides) | kappa | x PR #163 |
|---|---|---|---|---|---|---|
| 3 | 6 | 12 | 2.00 | 3.0519e-2 | 2.8764e-2 | 48.4x |
| 4 | 14 | 38 | 2.71 | 1.7960e-2 | 1.7337e-2 | 29.2x |
| 5 | 30 | 100 | 3.33 | 1.2279e-2 | 1.1985e-2 | 20.2x |
| 6 | 62 | 242 | 3.90 | 9.0809e-3 | 8.9189e-3 | 15.0x |
| 7 | 126 | 560 | 4.44 | 7.0573e-3 | 6.9591e-3 | 11.7x |
| 8 | 254 | 1262 | 4.97 | 5.6780e-3 | 5.6142e-3 | 9.5x |

**Construction.** Inputs are all nonzero, non-full bitmasks of [h]. The DAG is
the fast Yates zeta transform over the Boolean lattice: accumulators
`A_j(W)`, h*2^(h-1) - (2^h - 1) additions. The side root for target `t` is
`Z_{full^t}`: the sum of every input submasked into `complement(t)`, i.e. bit-
disjoint from `t`. The side-root orthogonality contract is met by construction:
the accumulated addresses are exactly the directions orthogonal to `t`
(integer disjointness), so every value span lies in the required complement.
There are no center roots, so `ell = 0` and the in-tree identity gives
`deficit = 2v` (maximal data freeness). `R/v = 2.0 .. 5.0` is the binding
quantity: `kappa ~ 1/(3h (2 + R/v) E)`.

**Verify.**

    python3 research/zeta-family/verify.py

Stdlib only, run without `-O`, about 1 second. It checks (1) a literal semantic
evaluation of the DAG: every root equals `sum_{u: u&t=0} x_u` for random inputs,
both seeds; (2) their compiler's full assert chain on each graph (value spans
inside frames, backward-intersection annotators, root legality, target chains,
`mass == h*R + ell`, `deficit == 2v - 3*ell`); (3) their 47-constraint
assembly with both sides at the family saving, all slacks and seven margins,
`b < 1/32`. The frontier multiple is re-derived from PR #163's certified number
and is used for reference only.

**Scope and open obligations (explicit).**

A. The source-data histogram shape is supplied explicitly for `h <= 6`. The
   in-tree default `Counter({2:v, h-4:v, 1:v})` is a dict literal whose
   duplicate keys collapse at `h in {5,6}` and whose key is negative at `h=3`;
   the supplied shape `{2:v, 1:v(h-3)}` is the legal mass-`v(h-1)` form and is
   conservative (more rank-1 children, hence larger E) relative to a
   big-stride shape. At `h >= 7` the in-tree default is used unchanged.
B. Centerless scope: `ell = 0` passes every in-tree assert. Whatever role the
   coordinate-star centers discharge in the retained proof notes is not
   re-derived here and is an open written obligation.
C. The DAG computes the orthogonal-broadcast map `y_t = sum_{u: u&t=0} x_u`
   (checked literally above). Its service to the upstream reduction - the
   analogue of the `H+K+B = I` scalar ledger - is not established here and is
   the main open obligation.
D. The scalar word (ops/replay), the physical layer, and the scalar-domain
   realizations are not built here. The graph is verified through the merged
   complex-side compiler path; the bit-side path carries its own H0 = (I-J/9)/2
   cap geometry and does not accept this graph as-is (checked: it rejects with
   'root physical compatibility'). The bit-side construction is therefore an
   explicit obligation, and every table number is a two-sided projection under
   obligations A-C. This package is a compiled graph and its in-tree-verified
   profile, not a certificate of multiplication.

**Credits.** The compiler (`frames.py`), the assembly, the side-root
orthogonality contract and the identity bookkeeping are icekylinx's PR #144
lineage (with the retained notices), used unchanged. Graph construction,
semantic evaluation and the audit table by this contribution; prepared with
AI assistance (Cline). Apache-2.0.
