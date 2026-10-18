# With freely chosen source ports, two root connectors need four transfers

Adding a second arbitrary-dirty connector and a paid one-way XOR transfer does
not repair the universal five-source obstruction with only two transfers.
Each B_j may target either root connector. At exactly two calls per source and
two per output, **at least four transfers** are necessary. Four transfers are
sufficient for a mixed two-source output;
this does not assert sufficiency for all 31 five-source masks.

The exact five-source census checks 1,995,840 canonical placements and agrees
with the proof below. This is a restriction on a genuinely enlarged alphabet,
not another census in the original single-connector alphabet.

## Changed interface and complete bill

Keep Ross Richardson's [universal connector contract](../universal-connector-boundary/README.md):
arbitrary F2-linear, possibly noncommuting maps A_i and B_j, read-only source
rows x_j, distinct output rows y_i and exact additive complete calls. Replace
the single dirty connector by two distinct dirty rows z0,z1. B_j may target
either connector; A_i may read either connector. Add only C: z0 += z1, charged
as a complete full-row XOR including access, head return, scratch and dispatch.
All rows restore except y_i, which receives the requested sum of A_i B_j x_j.
No connector reset, copy, free routing, reverse-direction transfer or output
observation before completion is allowed.

Every B_j and every A_i occurs exactly twice in the investigated family. This
is the minimum operator incidence for generic active sources/outputs. Extra
calls are outside the theorem; in this enlarged alphabet odd incidence can be
legal, so the old general even-incidence argument must not be imported.

Let complete fixed-port prices be c_Bj, c_Ai and c_C; use the largest port price
when giving an upper bound. The proposed incidence-minimal family costs

    I_two_rows + preparation + dispatch + 2 sum_j c_Bj + 2 sum_i c_Ai + t c_C.

I_two_rows includes admission/reservation of both full rows and all frames.
The theorem rules out t=0,1,2,3 for the universal five-source target. Hence
even before construction this route needs at least 4 c_C plus the extra-row
charge. Compare that with the predecessor's achieved extra 2 min(c_Bj,c_Ai).
Only a favorable fully charged comparison can justify a larger search.
C is not declared rank-free: on length L independent bits it has rank L and
requires L scalar XOR updates in a direct backend. No instantiated supplier,
new contraction, kappa or multiplication runtime is claimed.

## Proof

Track each connector as a formal linear combination of independent symbols
z0_initial, z1_initial, b_j=B_j x_j. Generic scalar specialization to independent
input bits suffices for necessity, and symbolic linearity proves sufficiency.

The two initial dirty columns force an even number of C calls. Consider zero
or two C calls. In the final map a B call on port0 contributes e0 b_j. A B call
on port1 contributes either e1 b_j or (e0+e1)b_j according to the parity of
remaining C calls. Since each source occurs twice and must cancel, its two
contribution columns must agree. Thus both calls use the same port; a port1
source also occurs at equal C parity. Partition the source labels as J0,J1.

With two transfers at cuts s<t, let q_r denote the sum of B increments made
directly on port r. Final restoration implies q_1(s)=q_1(t): every J1 source
has even incidence between the cuts. Outside (s,t), z0 has dirty coefficient
e0 and source part q0. Inside, its dirty coefficient is e0+e1 and source part
q0+q1(s). The row z1 always has dirty coefficient e1 and source part q1.

Two readouts of one output must have identical dirty coefficient. Therefore
they either both read z1, both read z0 outside the interval, or both read z0
inside it. Their differences are supported entirely in J1, J0 and J0,
respectively: the constant q1(s) cancels in the last case. **No output mask
can meet both source groups.** The zero-transfer case is immediate.

If both groups are nonempty, the all-mask target demands such a mixed mask
and fails. If all five sources use one port, every possible readout difference
is among differences of prefixes of a five-label twice-occurring source word.
The predecessor's exhaustive 945-pairing result has maximum 31 of 32 masks;
the local checker independently reproduces that census. Thus zero or two C
cannot realize the universal five-source target. Odd C cannot restore dirt,
so at least four C are required.

The mixed-support statement is sharp. With two sources, the source/transfer
word C B1(port1) C B0(port0) B0(port0) C B1(port1) C restores both connectors.
Read z0 once at entry and once after the first B0. Both reads have dirty part
e0 and their difference is b0+b1. This realizes y += A(B0 x0+B1 x1) with two
calls each to B0,B1,A and four paid C calls. Arbitrary output dirt is retained.

## Evidence and reproduction

`verify.py` uses independent dirty/source columns and a second direct-pair
readout oracle. It exhausts source pairings, per-source port assignments and
both transfer positions for n=1,...,5. Completeness of fixed-port assignments
follows from the final-column argument above. A separate 945-word control
recovers the predecessor histogram. The four-transfer positive fixture is
replayed forward and backward on all 32 scalar dirty inputs. Three mutations
detect omitted transfer, wrong readout port and omitted source restoration;
a separate dirty-column control rejects the false clean-input shortcut.

Run from the repository root with Python 3.12+ and no dependencies:

```sh
python -O -B research/two-connector-transfer-boundary/verify.py
python scripts/research_package.py --package research/two-connector-transfer-boundary
```

The exact receipt is [EXPECTED.json](EXPECTED.json); exact committed source
Git blobs and SHA256 hashes are in [SOURCES.json](SOURCES.json). Finite replay
supports the explicit symbolic proof; it is not a formal proof assistant run.

The final overlap refresh completely paginated 791 open PRs and 148 Discussion,
comment and reply records at 2026-10-14 00:43 UTC. It found Cinna Davis's
concurrent [Discussion 1412](https://github.com/CrocSwap/integer-mult-bounds/discussions/1412):
the same second-dirty-root mechanism with every B_j restricted to z0, a paid
transfer z1 += z0, and arbitrary A readout ports. That claim seeks a sharp
eight-transfer bound and construction in its restricted-source-port alphabet.
The present lower bound is weaker (four) but covers the larger alphabet in
which B_j may target either connector. Relabelling roots changes the transfer
direction, not this difference in allowed source ports. Neither the announced
restricted-port result nor this package settles the other's quantified claim.
We claim no priority for adding a second connector or a paid connector XOR.
The four-transfer fixture here mixes only two sources; it is not a universal
five-source construction.

The prior forty contributions were checked. Port borrowing changes descendant
scratch, and Discussion 1403 changes source toggles to combined DUO calls;
neither is this freely chosen-source-port contract. The overlap scan reads
open PR bodies and Discussion records, not PR comments, code diffs or all closed
work, and is not a novelty certificate. No frozen predecessor or selected
record is modified.

## Open next questions

Can four or more one-way transfers actually cover all five-source masks at
minimum B/A incidence? First solve the finite restored two-row source-path
problem, retaining the dirty-frame pairing rule. Proceed only when the priced
four-transfer and extra-row lower bound beats the inherited two-query repair;
the current package supplies no such concrete supplier cost evidence.

## Credit

Prepared by woklerx with substantial OpenAI Codex assistance, Apache-2.0.
Ross Richardson's universal connector theorem and PR934 supply the exact
query model and five-source obstruction; his NOTICE retains the common-factor
fanout and dirty-commutator lineage including @shhxera and Chafik Boukhalfa.
Cinna Davis's concurrent Discussion 1412 is credited for the closely related
restricted-source-port investigation found in the final overlap refresh.
No predecessor implementation is imported. No independent human review is
asserted. The selected community frontier and its attribution are unchanged.
