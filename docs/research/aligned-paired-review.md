# Focused review of the aligned paired circuit

Andrew Barnes, October 7, 2026. Review requested; no external assessment is
recorded in this packet.

This packet isolates the transfer from an improved finite sum circuit to the
conditional integer-multiplication bound. It builds on Douglas Colkitt's paired
construction and the OpenAI manuscript *Integer multiplication below n log n*.
The pinned manuscript commit is `adc7f1241b42e322a6451854ab7e4b4c146bf78a`;
the original aligned contribution is
`a961c43eecacb72929021936798dc049771f8536` in
[PR #2](https://github.com/CrocSwap/integer-mult-bounds/pull/2).

Read the [three-page packet](../../artifacts/aligned-paired-review.pdf), the
[construction](aligned-paired-network.md), and the
[exact certificate](../../certificates/aligned-paired-network.json).
LaTeX anchors below refer to the unchanged pinned manuscript; the
[aligned patch](../../patches/h50-aligned-paired.patch) supplies the revised
construction and parameters. Earlier research notes describe historical
witnesses and must not be combined with these counts as if they were current.

## 1. Claims and their boundaries

**Finite claim F.** Let inputs `x_S` be indexed by three-element subsets of
`{0,...,49}`. For every three-element target `T` and `i` in `T`, the graph computes

$$y_{i,T}=\sum_{S\cap T=\{i\}}x_S.$$

It uses 435,450 binary additions, all with disjoint formal supports, and has
58,800 partial outputs. Summing the three outputs for each `T` gives the
intersection-one map. The unchanged local 49-point paired circuit has 9,813
additions and 1,176 outputs. The global refinement removes 14,944 additions
from the preceding paired graph. These finite identities and counts are
independently reproducible without the asymptotic theorem.

**Conditional consequence C.** Assume the retained reversible embedding and
motif argument realize the finite shear contract with the stated counts;
`prop:power-interchange` and `lem:chunk-swap` have their claimed uniform
fixed-tape costs; and the retained layer, stopped-guard, resampling, transform,
precision and assembly interfaces apply to the new parameters. Then

$$T(n)=O\bigl(n(\log n)^{1-\kappa}\bigr),\qquad\kappa=17\cdot2^{-63}.$$

The machine has a fixed finite alphabet and a fixed finite number of
one-dimensional tapes. The network data are constants independent of `n`.
This packet does not validate the complete upstream algorithm or establish
a worldwide priority claim.

## 2. Finite construction and rank obligation R1

For common point `i`, order the other points increasingly except for the
partner `i ^ 1`, which goes last. Relabel both inputs and outputs of the unchanged
weighted paired circuit. All complete root pairs now agree with the global
pairs `{0,1},...,{48,49}`. Intern equal fixed-pair stars, retain the first
decomposition, prune unused nodes and recompile physical roles. Equal scalar
values do not justify identifying simultaneously occupied physical slots.

For a node's source support `A`, let `U_A` span the indicator vectors `1_S`
for `S` in `A`, in the form `B=I-J/9` on `Q^50`. Its sources share a point `i`.
Each `u` in that span satisfies `sum(u)=3*u_i`, hence

$$u^TBu=\sum_{j\ne i}u_j^2.$$

Zero forces all other coordinates to vanish, then forces `u_i=0`. Thus every
source span is positive definite. The ambient form is nondegenerate (`50 != 9`),
so its orthogonal complements are nondegenerate. At an output,
`1_S^T B 1_T=|S intersect T|-1=0` for every contributing source. Support inclusion
nests the forward spans; `U_A <= U_B` becomes `U_B^perp <= U_A^perp` in reverse.
These are local premises for the retained tensor/motif transfer, not a proof
of the entire transfer.

With `C` additions and `Q` outputs, gather/fanout compilation has `2*C+Q`
outgoing uses, reuses one incoming role per addition, and has `R=C+Q=494250`
side roles. In the retained schedule, arbitrary scratch `z` contributes `J L z`
and `J L(z+Vx)` with opposite signs; their difference is `J L Vx`, followed by
scratch restoration. Here `L` is the mixer product, `V` the source copy and `J`
the output injection. This algebra alone does not certify every physical frame
transition or endpoint.

**R1:** verify the complete forward/reverse schedule, tensor frames,
first/third-stage role matching and every role's endpoint with these shared
nodes. Check arbitrary initial scratch. The negative X-source correction adds
`N` ranks and must be included. The asserted counts are

$$v=19600,\quad N=v^3,\quad m=125000,\quad L_{\rm loss}=3v^2h^2,$$
$$W=2N+2v^2(R+h)=394839648000000,$$
$$s=Wm-N+2L_{\rm loss}=49354954232864000000,$$
$$D=Wm-s=1767136000000,\qquad\eta=D/(Wm)=23/642375000.$$

## 3. Fixed-tape recurrence obligation R2

The required contract is stronger than a correct sum circuit. The bit network
must route all `W` inputs by a permutation `rho`, with a common rational
`m x m` matrix `M` assigned to every gate, and

$$M_{\rm out(\rho(w))}-M_{\rm in(w)}=I_m\quad(1\le w\le W),$$
$$s=\sum_e\operatorname{rank}_{\mathbb Q}
 (M_{\rm head(e)}-M_{\rm tail(e)})<Wm.$$

In `prop:power-interchange`, width `e=m^k` has a preceding row count divisible
by `W^k`. Cyclic splitting creates `W` streams of the same remaining shape,
each with logical volume `V_log/W` and row count divisible by `W^(k-1)`.
`lem:matrix-shear` needs exactly the rational rank of an edge matrix in recursive
pivot interchanges. All spectator ranges remain present. A fixed prime avoids
the finite table's denominators and invertible-factor diagonal numerators.

**R2:** certify exactly `s` recursive calls on logical volume `V_log/W`, with
at most `C0*V_log` further tape steps. `C0` may depend on the fixed network and
prime, but must be independent of depth, field lengths and data. The existing
proof reserves `W` role tapes, parks inactive streams, and restores them from
the stack top without traversing ancestors. Charge every current-call copy,
erasure and head movement. A fixed tape count can be an enormous constant.

The descriptor paragraph also needs review. At depth `j` of root width
`e0=m^k0`, the original chunk ranges remain present as targets or spectators.
Thus `V_j >= q^(2*e0)` and
`log(V0)=log(V_j)+j*log(W)=O(log(2*V_j))`. The child collapses consecutive
spectators into a bounded number of intervals, so descriptor processing has
fixed polynomial logarithmic cost, absorbable in `O(V_j)`, even with one-bit
payloads. Check every allowed shape and that cleanup never scans an
ancestor's largest used extent. The manuscript contains this schedule and
descriptor argument; the question is their validity, not their absence.

Under that uniform node bound, normalized time satisfies

$$F_0=O(1),\qquad F_k\le(s/W)F_{k-1}+C_0.$$

The exact bound `eta > a*log(m)` with `a=305/10^11` gives
`1-eta < exp(-a*log(m))`, hence `s/W < m^(1-a)`. The geometric recurrence gives
`O(V_log*e^(1-a))`. `lem:chunk-swap` must retain that exponent when removing
row and width restrictions, including padding and cleanup. The recurrence
solution is elementary; establishing its uniform node bound is the
implementation question. A fixed number `s` of parking operations fits in
`C0`; replacing child logical volume by total workspace loses the claimed
coefficient `s/W`.

## 4. Downstream obligation R3 and source map

Retain `a_c=1/10^11`, `beta=999/1000`, `epsilon=199/1000`, `delta=1/10000` and
`C1=2`. Set `tau=1-a`, `sigma=1-a_c`, `c=beta*a`,
`lambda=1-(1+beta)*a^2/2`, and `lambda_prime=1-beta*a^2`.
The stopped guard uses the unchanged complex motif. The Gaussian choice is
`alpha=ceil((32*d*b)^(1/4))`, with cutoff `b>=2^40`. The exact certificate
checks 30 strict inequalities and all seven margins, whose minimum is

$$G=\epsilon\beta a^2=
\frac{739738521}{400000000000000000000000000}>17\cdot2^{-63}.$$

**R3:** check that those inequalities match the actual algorithmic hypotheses
and costs. A strict margin absorbs fixed logarithmic factors only after the
retained cost, transform, precision and rounding bounds have been justified.

Paths below are relative to `upstream/build/sections/` unless stated otherwise.

| Step | Source anchor | Evidence and remaining obligation |
| --- | --- | --- |
| Finite outputs and counts | `scripts/aligned_paired_network.py`; `scripts/shared_point_circuit.py` | Full coefficient expansion independent of provenance; finite claim F. |
| Source/complement frames | Section 2; [shared-computation](shared-computation.md); [complement refinement](cross-point-sharing.md) | Local proof and compiled inclusions; review tensor transfer and physical roles. |
| Scratch, endpoints, rank | `03-motifs.tex`: `eq:motif-schedule`, `eq:common-frame-identity`, `prop:bit-motif-interface`; aligned patch | Small complete dirty-input tests and general retained argument; R1. |
| Rank to child calls | `04-swap.tex`: `lem:matrix-shear`, `eq:finite-shear-contract` | Finite factorization; check specialization and all-role contract. |
| Uniform node cost and general widths | `04-swap.tex`: `prop:power-interchange`, `eq:swap-recurrence`, `lem:chunk-swap`; `02-streams.tex`: `lem:elementary-streams`, `lem:ordered-affine-streams` | Written parking/descriptor proof; R2, not established by finite tests. |
| Layers, guard, resampling | `05-layers.tex`: `prop:simultaneous-layer`; [paired guard/Gaussian audit](paired-network.md); `07-resampling.tex`: `lem:no-sort-resampling`, `lem:tensor-resampling` | Retained algorithmic and analytic interfaces; R3. |
| Assembly | `08-assembly.tex`: `eq:sizes`, `eq:final-error`, `tab:costs`, `eq:margin-list`; aligned patch | Strict arithmetic margins; retained costs, transforms, precision and rounding remain assumptions. |

## 5. Reproduce the finite evidence

From the repository root, with Python 3 and Git:

```sh
python -m unittest discover -s tests -p test_aligned_paired_network.py -v
python scripts/aligned_paired_network.py
git diff --exit-code -- certificates/aligned-paired-network.json
git apply --check --directory=upstream patches/h50-aligned-paired.patch
```

The six tests include every coefficient of the actual full-size DAG, expanded
in 1,024-input chunks without `support_in` or compressed provenance; both
frame directions; small complete forward/reverse dirty-input basis vectors;
and three-stage bank exchange. The certificate separately checks production
provenance, symbolic inclusions, counts and rational parameters. Do not use
Python's `-O`; several mathematical checks use assertions.

Run `make verify` for all regressions and historical patch checks. Compile the
printable packet with `tectonic --outdir artifacts notes/aligned-paired-review.tex`.
These commands do not prove the uniform machine costs or complete theorem.

## 6. Requested assessment

Report on R1, R2 and R3 separately: reviewed commit, source anchor, argument or
counterexample, and unreviewed prerequisites. A bounded obligation may be
accepted with justification, rejected with a concrete failure/repair, or left
unresolved with a named prerequisite. An expert uninvolved in the original
construction or audit would provide valuable independent scrutiny of R2.

An empty code-review finding list, a successful certificate, or approval of
the finite graph alone does not close the recurrence or downstream obligations.
