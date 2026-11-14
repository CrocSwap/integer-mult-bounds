# Exact finite quotient-flow proof

## Claim and exact scope

Let

\[
H=\begin{pmatrix}
1&1&1&1\\1&-1&1&-1\\1&1&-1&-1\\1&-1&-1&1
\end{pmatrix},\qquad U=H/2.
\]

For each of (R=6,7,9,11), form the finite bipartite graph whose left side is

\[
S_R=\{x\in\mathbb Z^4:\|x\|_2\le R\},
\]

and whose right side is the union of integer (y) for which
\(\|y-Ux\|_2\le1\) for some (x\in S_R\). Join (x) to each such (y).
Give an edge the exact outward gap
\(\|y\|_2-\|x\|_2=\sqrt{m}-\sqrt{n}\), where (m=\|y\|_2^2\) and
\(n=\|x\|_2^2\).

The exact optimum is \(\sqrt{31}-\sqrt{28}\) at (R=6,7), and
\(\sqrt{78}-\sqrt{73}\) at (R=9,11). At each reported optimum the
inclusive edge graph has a matching saturating all inputs, while the strict
edge graph has the Hall cut listed in `RESULT.json`, with deficiencies
32, 32, 64, 64 respectively. Therefore no smaller maximum edge gap is
possible in these four finite domains. At the separately tested thresholds,
\(\sqrt{21}-\sqrt{19}\) for (R=6), \(\sqrt{43}-\sqrt{39}\) for (R=7),
\(\sqrt{73}-\sqrt{67}\) for (R=9), and \(\sqrt{111}-\sqrt{103}\) for
\(R=11), the first graph is infeasible and the remaining three are
feasible.

## The paired (W(D_4)) action

Let (A) be a signed permutation of four coordinates with an even number
of sign changes. Set

\[
B=HAH^T/4.
\]

The complete finite group check in `sweep.py` examines all 384 signed
permutation matrices (A). Exactly 192 induce integral signed-permutation
matrices (B); both projections are the 192-element group
\(W(D_4)\), the signed permutations with sign product (+1). For every
paired element, (BH=HA), so (BU=UA). Since (A,B) are orthogonal, the
action \((x,y)\mapsto(Ax,By)\) preserves both norms and the error
\(\|y-Ux\|_2\). This is the group action used below; no claim about
non-signed-permutation graph automorphisms is needed.

## Orbit construction and capacities

An orbit is encoded by the sorted tuple of absolute coordinates. If no
coordinate is zero, the product of coordinate signs is also part of its
key; the two product-sign classes are distinct. If a zero is present, its
sign absorbs parity and the pattern is one orbit. For a pattern with
multiplicities (m_r) and zero multiplicity (m_0), its exact capacity is

\[
\frac{4!}{m_0!\prod_{r>0}m_r!}\,2^{4-m_0}
\quad(m_0>0),
\qquad
\frac{4!}{\prod_{r>0}m_r!}\,2^3
\quad(m_0=0,\text{ for each sign-product class}).
\]

The generator visits nonnegative sorted-coordinate patterns of squared norm
at most (R^2), then makes one orbit key per zero-containing pattern or two
keys per nonzero pattern. It checks the capacity sum for the input and
candidate-output universes. The JSON receipt preserves every representative
and capacity, so each cut's orbit predicate is the listed union of keys.

For a representative (x), each coordinate of (Hx) has parity
\(\sum_i x_i\pmod2\). If the sum is even, (Ux\in\mathbb Z^4), and the
complete set of integer outputs within distance one consists of the center
and its eight signed unit displacements: 9 candidates. If the sum is odd,
all four coordinates of (Ux) are half-integers; the complete set consists
of all 16 nearest-integer corners, each at squared error one. The group
action transports this complete neighbor set over the orbit. Thus the
enumeration at representatives constructs the full candidate graph.

## Quotient graph, matching lift, and Hall cuts

For any input orbit (I) and output orbit (O), adjacency is the invariant
relation “some point of (I) is joined to some point of (O).” The paired
group is transitive on each orbit, so each adjacent orbit pair is biregular:
every input point has the same number of neighbors in (O), and every
output point has the same number of neighbors in (I). The implementation
checks the exact double-count identity
\(|I|d_I=|O|d_O\) by requiring divisibility of the computed left degree by
\(|O|). Norms are constant on orbits, so every edge in an orbit pair has
the same exact gap.

The quotient network has source-to-input capacity \(|I|\), output-to-sink
capacity \(|O|\), and one input-to-output edge for each active adjacent orbit
pair, with capacity greater than the sum of all finite node capacities. A
maximum flow of value \(|S_R|\) is a complete positive certificate when its
per-orbit-pair amounts conserve at each orbit and respect all sink
capacities. Those integer certificates are recorded in `RESULT.json` and
checked by `verify.py`.

To lift such a quotient flow (f_{I,O}), put the constant weight
\(f_{I,O}/|E(I,O)|\) on each individual edge in that orbit pair. If
\(E(I,O)\) is its edge set, biregularity gives each input vertex total
fractional degree

\[
\sum_O\frac{f_{I,O}}{|I|}=1,
\]

because the source orbit is saturated. Each output vertex has degree
\(\sum_I f_{I,O}/|O|\le1\), because its sink capacity is (|O|). This is a
fractional matching saturating the left side. For any set (T) of input
points, the total edge weight leaving (T) is (|T|), and it is at most the
total weight incident to its neighbors, which is at most (|N(T)|). Thus
Hall's condition holds, and Hall's theorem gives an actual injection
saturating every input. Conversely any injection induces a quotient flow,
so flow saturation is an exact feasibility test.

For each recorded lower-bound cut, let (T) be its selected input orbits.
The result checker enumerates every active quotient adjacency out of (T)
and verifies that the stored output-orbit set is exactly (N(T)); this checks
the complete lifted neighborhood directly, without relying on min-cut
optimality. If the input and neighbor capacities are (t) and (n), the
corresponding Hall deficiency is (t-n). Every reported infeasible result
has (t-n>0), so this explicit union of input orbits proves that no injection
can exist.

## Exact gaps and finite optimum

All squared norms in an edge are nonnegative integers, so every gap is an
exact expression \(\sqrt m-\sqrt n\). The comparator reduces comparisons
to inequalities between sums of two square roots and decides them using
integer additions, products, and squares. In particular, for
\(\sqrt a+\sqrt b\le\sqrt c+\sqrt d\), set
\(k=c+d-a-b\), (P=ab), and (Q=cd). Squaring the nonnegative sides once
reduces the question to \(2(\sqrt P-\sqrt Q)\le k\). When (k\ge0),
\(P\le Q\) suffices; if (P>Q), put
\(e=4(P-Q)-k^2\): the inequality holds if (e\le0\), otherwise exactly
when \(e^2\le16k^2Q\). When (k<0), put (r=-k); the inequality holds
exactly when \(e=4(Q-P)-r^2\ge0\) and \(e^2\ge16r^2P\). This avoids
floating-point threshold decisions.

The script sorts the finite set of attainable edge gaps by this comparator
and binary-searches the first gap whose inclusive quotient flow saturates
all inputs. At that gap it records a positive flow certificate. The strict
predecessor graph has an exact Hall cut with positive deficiency. Every
smaller threshold graph is a subgraph of that strict predecessor graph, so
the pair of receipts proves the stated exact finite optimum.

## Reproduction, controls, and limits

Run `python3 -I -B sweep.py > /tmp/finite-radii-result.json` and compare
that file with the frozen RESULT.json. Run `python3 -I -B verify.py` and
`python3 -I -O -B verify.py` to check all four radii and deliberately reject
(i) an incremented positive orbit-pair flow and (ii) a cut with one neighbor
orbit removed. Both sweep modes produce identical bytes; both verifier modes
produce identical summaries. The checker loads the local sweep source bytes
with compile/exec, independent of ambient import paths or cached bytecode.

This is finite evidence restricted to the four named radii, (U=H_4/2),
and error cap one. It establishes no general radius pattern, global
construction, multiplication bound, or new kappa claim. The R5 source and
compact (W(D_4)) proof that motivated this extension are pinned to the
published R5 workstream commit
9c75d0b4b6e1cfe74694edf52f2f238a741bbaf5. Its local review copy is
../sharp-finite-gaussian-outward-slack/compact-hall/PROOF.md; the
canonical analysis base for this sweep is CrocSwap commit
e54523517d0f03e58352e647c403a5af3e525a57.
