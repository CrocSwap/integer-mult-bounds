# Cut certificates for nonlinear framed circuits

We extend the common-flag rank obstruction from XOR circuits to arbitrary
deterministic pointwise gates. Nonlinear gates cannot create a positive rank
deficit when the rational frame matrices preserve a common complete flag,
even if the flag exists only over a characteristic-zero extension field.

The conclusion is `s >= Wm`, with every physical edge and arbitrary input
role counted. We prove it by outgoing-message counting, without linearizing
the gates or representing them by `W`-by-`W` scalar matrices. This closes the
nonlinear-gate exception stated in Navinor's
[PR825 common-flag result](../common-flag-frame-obstruction/README.md).
It supplies no new supplier or exponent.

## Circuit model

Use a finite acyclic pointwise circuit with `W` source roles and `W` sink
roles over one alphabet of size `q>=2`. Each physical wire segment carries
one alphabet symbol. The `W` inputs vary independently. At completion,
output `rho(w)` must equal input `w`, for a fixed role permutation `rho`,
on every input assignment. Include arbitrary scratch roles among those inputs.

The topology and local functions are fixed. Each gate uses one common rational
`m`-by-`m` matrix on all its ports. Every source and sink also has a matrix.
For an edge `e=(u,v)`, charge `rank_Q(M_v-M_u)`, including terminal edges
and untouched wires. Require

`M_out(rho(w)) - M_in(w) = I_m` for each role `w`.

These are the finite conditions of the retained
[upstream shear contract](../../upstream/build/sections/04-swap.tex).
The executable repository scorer currently specializes scalar semantics to
XOR; we leave it unchanged and use full truth tables here.

We assume no uncharged external observation, input-dependent topology,
postselection or message-bearing side channel. The counting proof needs only
determinism and the complete permutation endpoint. In a fixed-width circuit,
that endpoint also forces intermediate state maps to be injective; allowing
arbitrary deterministic gate syntax does not produce a valid lossy circuit.

## The cut lemma

Assign any label `ell(v)` to each circuit vertex. For a label `a`, let `D_a`
be the input roles whose source has label `a` and whose required sink has
a different label. Let `E_a` be the edges leaving label class `a`.
Then

`|E_a| >= |D_a|`.

**Proof.** Fix all input values except those in `D_a`. Record the symbols
on `E_a` in their fixed chronological order. Given this transcript and the
fixed inputs, simulate the vertices outside class `a` in topological order.
Each outside gate receives either an already computed outside value or a
value from the transcript. Therefore the transcript determines the outside
outputs, including the distinct sinks that must reproduce the `|D_a|`
independent unknown symbols.

Two assignments to `D_a` cannot produce the same transcript. There are
`q^|D_a|` such assignments and at most `q^|E_a|` transcripts. Hence
`q^|D_a| <= q^|E_a|`, giving the inequality. This argument permits edges
to leave and re-enter the class; it does not assume a time-slice cut,
edge-disjoint routes or linear gates.

Summing over label classes counts each crossing edge once and each separated
source/sink demand once:

`# {e=(u,v): ell(u) != ell(v)}
 >= # {w: ell(in(w)) != ell(out(rho(w)))}`.                 (1)

This is elementary finite-alphabet cut-set counting. We claim the application
to the framed-circuit obstruction, not priority for the counting principle.

## Weighted partition certificates

Take finitely many vertex labelings `ell_j` and nonnegative weights `c_j`.
If, for each edge `e=(u,v)`,

`sum_j c_j * 1[ell_j(u) != ell_j(v)] <= rank_Q(M_v-M_u)`,

then (1), multiplied by `c_j` and summed, gives the lower bound

`s >= sum_w sum_j c_j * 1[ell_j(in(w)) != ell_j(out(rho(w)))]`.

This implication does not require a common flag. A researcher must supply
and check the edge-budget inequalities for the proposed labelings. We do not
assert that arbitrary matrix rank metrics admit such a certificate with
right-hand side `Wm`. The verifier below instantiates the unit-weight
partitions used in the common-flag corollary; the weighted statement is a
written consequence of (1).

## Common-flag corollary and proof

Suppose that for one common matrix `A` and an invertible `B` over a
characteristic-zero field extension `K` of `Q`, every

`T_v = B^-1 (M_v-A) B`

is upper triangular. Label vertex `v` by the `i`-th diagonal entry of `T_v`,
for each `i=1,...,m`. The endpoint condition shifts each of these labels by
one. Thus every input/sink demand is separated in each labeling, and (1)
forces at least `W` crossing edges per diagonal position.

For each edge, `T_v-T_u` is upper triangular. Its principal submatrix on the
nonzero diagonal entries has nonzero determinant. Therefore

`rank_Q(M_v-M_u) = rank_K(T_v-T_u)
 >= # {i: (T_v-T_u)[i,i] != 0}`.

The unit-weight partition certificate applies, so `s>=Wm`. The common
additive gauge `A` cancels from edge differences. Field extension does not
change the rank of a rational matrix. This covers nonsplit eigenvalues,
Jordan blocks and noncommuting upper-triangular frames. The predecessor's
common-eigenvector induction gives a common flag for any finite commuting
family over an algebraic closure, so the corollary includes that family too.

The bound is sharp: assign zero to every source and gate and `I_m` to every
sink. Only terminal edges contribute, with total rank `Wm`, for any valid
pointwise permutation circuit.

For `0<alpha<1`, each edge rank lies between zero and `m`, and

`(1/W) sum_e (rank(Delta_e)/m)^alpha
 >= s/(Wm) >= 1`.

Thus even an optimistic bill with zero additional overhead cannot contract
within this class. Nonnegative source, restoration, routing or precision
charges cannot change that conclusion. This is a circuit-class obstruction,
not a lower bound for integer multiplication.

## Why full nonlinear semantics matter

For arbitrary dirty bits `(a,b,t)`, execute

```text
t ^= a*b
b ^= a
t ^= a*b
b ^= a
```

The result is `(a,b,t^a)` because `ab+a(b+a)=a^2=a` on Boolean inputs.
The CNOT-only subword is the identity. Discarding nonlinear terms or applying
the old linear-column checker to that subword therefore loses the actual
operation. Our fixtures use this gadget inside a nonidentity wire swap and
replay every input.

A complementary failure control uses one Toffoli gate and falsely declares
an identity endpoint. Zero and every one-hot input pass; the full truth table
rejects it. This distinguishes arbitrary-dirty correctness from basis-only
testing for nonlinear circuits.

## Reproduce and evidence

Use Python 3.12 with the standard library:

```sh
python3.12 scripts/research_package.py --package research/nonlinear-frame-cut-bound
python3 -I -O -B research/nonlinear-frame-cut-bound/verify.py
```

The verifier checks source hashes, constructs the complete physical graph,
replays all scalar assignments and then simulates the outside of each label
class using only its permitted messages and fixed inputs. It imports no
repository implementation and writes no files. It checks exact rational
frame differences and a supplied flag; it is not a general flag-finding tool.

The twelve finite cases cover 428 full input assignments and 3,830 outside
simulations. Eight cases use binary nonlinear circuits on three through six
roles at dimensions two and three. Two cases use a three-symbol alphabet.
One sharp case attains rank mass 18 on six roles at dimension three.
One rational family `aI+bJ`, `J^2=-I`, uses the exact labels `a+bi` and
`a-bi`, testing a flag that does not split over `Q`.

Eleven controls cover wrong endpoints/permutations, omitted terminals,
per-port frames, malformed truth tables, singular or invalid supplied flags,
the basis-only trap, an omitted outgoing message, nonlinear cancellation
and the non-common-flag boundary. Checks remain active under `-O`.
Finite examples corroborate the proof and test its implementation. They do
not prove its universal statement by enumeration or constitute Lean review.

The registered replay passed on macOS arm64 with CPython 3.12.13. Optimized
CPython 3.14.6 produced identical JSON bytes. The predecessor's fourteen
finite examples and thirteen tests, package source pins and selected-record
integrity also passed. We report hosted CI separately in the PR.

## Scope, overlap and attribution

Base main: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`, priority revision 3.
[TASK.json](TASK.json) records the changed task and stopping rule.
[SOURCES.json](SOURCES.json) pins the source statement and predecessor.
We coordinated in [Discussion1753](https://github.com/CrocSwap/integer-mult-bounds/discussions/1753).
The entry overlap snapshot covered 426 open PRs and 384 Discussion records
with complete pagination at 08:35–08:36 UTC on 2026-10-14. The search does
not cover arbitrary code diffs and does not establish literature novelty.
The final refresh at 08:49–08:50 UTC covered 431 open PRs and 389 Discussion
records with complete pagination. We found the credited common-flag and
distinct message/cleanup bounds, with no matching nonlinear extension.

We credit Navinor's PR825 for the rational-frame common-flag theorem and its
linear XOR proof, and OpenAI's retained source for the finite shear contract.
The routing audit and the nonlinear cleanup bound concern different
restrictions: topology for the former, a fixed prefix and monotone subspace
restoration for the latter. We preserve their conclusions and source files.
Gaussian/Hurwitz nonlinear-message bounds use separate message-price models;
we do not import those prices into this all-role edge-rank contract.

Earlier exploration in this session found valid local shared-source scalar
identities but no admitted global gain. The joint 96-helper argument matched
PR1517 and was set aside as overlap. Neither is presented as a new result here.

Prepared for Jose Manuel (@jmbarrancoml) with substantial OpenAI Codex
assistance in research, proof, code and prose. Read-only subagents derived
the cut argument and nonlinear semantic controls. New work follows
Apache-2.0; the retained source licenses and attribution remain intact.
We claim no independent human review, selected-construction cold replay,
new compiler/hosting theorem, changed frontier or new kappa.

## Open next questions

A nonlinear candidate must also leave the common-flag geometry. The next
bounded experiment is a five-role mixed-gate topology: verify the exact
nonidentity wire permutation on all 32 inputs, reject a routable endpoint,
then search explicit rational two-by-two frames for total rank at most nine,
including terminal edges. The matrices
`J=[[0,1],[-1,0]]` and `B=[[0,0],[-1,1]]` have commutator determinant `-2`,
so they cannot share a complete flag over a characteristic-zero extension.
They are a possible frame-alphabet seed, not a successful circuit.
We have no nonroutable nonlinear endpoint with a verified deficit. That
construction is the blocker; a bounded search failure would not resolve it.
