# Four-register rational-frame target has exact eight-call minimum

**Exact local minimum in a fixed torsion-free additive-address model. No selected supplier or new κ is claimed.**

This result tests whether free mixing across four roles can share paid work for
four distinct rank-two targets built from a dependent set of rational
rank-one addresses. In the stated alphabet, the exact minimum is eight calls,
equal to the direct schedule. The lower bound applies to words of every
length, so no full-word enumeration is needed.

## Model and target

Work over the formal group algebra \(R=\mathbb F_2[\Lambda]\), where
\(\Lambda=\mathbb ZA+\mathbb ZB+\mathbb ZP\cong\mathbb Z^3\). The three
rational matrices \(A,B,P\) below are linearly independent over \(\mathbb Q\).
Add the fourth paid address \(Q=A+B-P\):

\[
A=\begin{pmatrix}1&0\\0&0\end{pmatrix},\quad
B=\begin{pmatrix}0&0\\0&1\end{pmatrix},\quad
P=\tfrac12\begin{pmatrix}1&1\\1&1\end{pmatrix},\quad
Q=\tfrac12\begin{pmatrix}1&-1\\-1&1\end{pmatrix}.
\]

Each is an explicit rank-one product of rational linear forms. A paid factor
chooses \(F\in\{A,B,P,Q\}\) and any rank-one idempotent
\(N\in M_4(\mathbb F_2)\), and applies

\[
D_N(F)=I_4+([F]-1)N.
\]

There are 120 such idempotents and 480 paid factor types. Free binary role
mixing is allowed, which is favorable to a proposed saving.

The target is

\[
T=\operatorname{diag}([A+P],[A+Q],[B+P],[B+Q]).
\]

The four target frames are respectively

\[
\begin{pmatrix}3/2&1/2\\1/2&1/2\end{pmatrix},\quad
\begin{pmatrix}3/2&-1/2\\-1/2&1/2\end{pmatrix},\quad
\begin{pmatrix}1/2&1/2\\1/2&3/2\end{pmatrix},\quad
\begin{pmatrix}1/2&-1/2\\-1/2&3/2\end{pmatrix}.
\]

Each has determinant \(1/2\) and rank two. The direct word uses two calls per
role with coordinate projector \(E_{ii}\): labels `(A,P)`, `(A,Q)`, `(B,P)`,
and `(B,Q)` on roles 0 through 3. Since
\(D_{E_{ii}}(F)D_{E_{ii}}(G)\) places \([F+G]\) on role \(i\) and identity
elsewhere, this reaches \(T\) in eight calls. At augmentation every factor is
\(I_4\), so arbitrary dirty role values return unchanged.

## Eight-call lower bound

Let \(J\) be the augmentation ideal of \(R\), and put
\(t_A=[A]-1\), \(t_B=[B]-1\), \(t_P=[P]-1\). Modulo \(J^2\), the four label
directions are

\[
A:(1,0,0),\quad B:(0,1,0),\quad P:(0,0,1),\quad
Q=(A+B-P):(1,1,1)\pmod 2.
\]

The target's three first-order diagonal coefficient masks are

\[
P_A=\operatorname{diag}(1,0,0,1),\quad
P_B=\operatorname{diag}(0,1,1,0),\quad
P_P=I_4.
\]

For a word, let \(S_F\) be the sum over \(\mathbb F_2\) of all idempotents
on calls labelled by \(F\). Equality with the target forces

\[
S_A+S_Q=P_A,\qquad S_B+S_Q=P_B,\qquad S_P+S_Q=P_P.
\]

If \(m\) rank-one idempotents sum to \(S\), then
\(\operatorname{rank}(S)\le m\) and
\(\operatorname{tr}(S)=m\pmod2\), because each rank-one idempotent has trace
one. Thus every such sum requires at least

\[
f(S)=\operatorname{rank}(S)+
\bigl(\operatorname{rank}(S)-\operatorname{tr}(S)\bmod2\bigr)
\]

calls. Setting \(S=S_Q\), any word therefore costs at least

\[
f(S)+f(S+P_A)+f(S+P_B)+f(S+P_P).
\]

The verifier evaluates this integer bound for every one of the 65,536 binary
4-by-4 matrices \(S\). Its exact minimum is eight, attained at 64 masks,
including \(S=0\). This is a small exact minimization of the necessary
first-order cost, not an enumeration of full words. The direct word attains
eight, proving the exact minimum in the stated model for arbitrary word
length and order.

The direct word also provides a first-order witness: its per-label idempotent
sums are diagonal rank-two matrices for A, B, P, and Q. A parity-mask mutant
that drops the last P-target bit changes the relaxation floor from eight to
six; this control catches an omitted role in the target signature.

## Scope and relation to predecessors

This changes the selected three-register abelian setup to four roles and four
explicit rational rank-one addresses with three independent additive
directions. The six/eight-address finite alphabets in merged PRs [#1974](https://github.com/CrocSwap/integer-mult-bounds/pull/1974)
and [#2027](https://github.com/CrocSwap/integer-mult-bounds/pull/2027) are not
used. The arbitrary-register one-frame-relation lemma does not cover this
word budget: eight paid frames have span at most three, below its `k-1`
condition. The earlier Cycle 20 four-register Klein-four result uses a finite
torsion address group and a different target; its exact source is commit
`aeb154f1f15e5dbc9f6ccc87151244741050a9fe`, README SHA-256
`983650ba8a05542c3ce6963c16b2b796cc631c84df4fa981b33a3574e8829577`.
The closest adjacent result is the completed four-role S3 target in
[Discussion #2023](https://github.com/CrocSwap/integer-mult-bounds/discussions/2023):
it also has an exact eight-call minimum, but uses two transposition labels in
finite \(\mathbb F_2[S_3]\) and a complete word-ball join. This package uses a
torsion-free rational address group and proves its bound from the first
augmentation quotient. Active [Discussion #2073](https://github.com/CrocSwap/integer-mult-bounds/discussions/2073)
studies clean ancillas in a two-register \(m=3\) model, a different role count,
target and dirty-state contract. These checks motivate changing the next
question beyond another four-role finite-group target.
Exact source and predecessor pins are in [SOURCES.json](SOURCES.json) and
[PREDECESSORS.json](PREDECESSORS.json); the complete overlap snapshot and its
coverage limits are in [OVERLAP.json](OVERLAP.json).

The selector record is seed `3573e12e06106f693177ed189d2a8b8e`, track
`bit-mechanisms`, task `bit-new-register-model`, priority revision 4, scope key
`7084092dd726e7ba1f2f`, catalogue SHA-256
`d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`, and
base commit `7c1e7811c730b17fe0eeef6c82ef011318b0465e`. The selected-record
SHA-256 is
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Before submission, canonical main was fetched and pinned at
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (2026-10-14 19:00 UTC). Priority
revision 4, task catalogue, selected record and scientific predecessor inputs
were unchanged; the new guidance affected checkpoint and discussion handling
only and is recorded in `TASK.json`.
The selected baseline replay passed and confirms the complex primitive still
binds. This result is only a scoped bit-side cost floor; no supplier mapping
or selected κ change follows.

The canonical investigation and handoff is [Discussion #2091](https://github.com/CrocSwap/integer-mult-bounds/discussions/2091).
The focused package is submitted in [PR #2085](https://github.com/CrocSwap/integer-mult-bounds/pull/2085).
The hub pointer is [#1167 comment 18932269](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18932269).
The earlier #1167 claim at [comment 18931816](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931816)
was corrected because its proposed first target did not have the stated direct
bill; the correction remains at [comment 18931944](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931944).

## Reproduce

From the repository root:

```sh
python3 -I -B research/bit-four-register-rational-frame-floor-seed3573e12e/verify.py
python3 scripts/research_package.py --package research/bit-four-register-rational-frame-floor-seed3573e12e --check-only
```

Expected verifier line:

```text
PASS_FOUR_REGISTER_RATIONAL_FRAME_EXACT_MINIMUM_8 projectors=120 paid_factors=480 relaxation_states=65536 min_floor=8 minimizers=64 direct_calls=8 mutated_floor=6
```

Python 3.12 is the registered package runtime. The local environment's
available interpreter is recorded in the handoff; a formal native supplier,
all-address extension, and any κ transfer remain open.

## Open next questions

Add one additional rational rank-one frame inside the symmetric span of
\(A,B,P\), first choosing a bounded rational slope family, and recompute the
exact torsion-free address lattice and first-order floor for this same target.
The key question is whether the extra frame introduces a new integral
first-order direction that can lower eight; stop before full-word search if
the necessary floor remains eight. Any resulting word would still need its
complete physical frame and addition invoice before supplier use.

## Credit

Prepared by Cinna Davis (1337isnot1337), with substantial OpenAI Codex
assistance in scope selection, exact cost screening, derivation, verification,
overlap review, and package writing. The prior research retains its original
attribution. New work is Apache-2.0.
