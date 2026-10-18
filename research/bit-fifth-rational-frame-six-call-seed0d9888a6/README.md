# One added rational frame does not give a six-call word

**Scoped exact negative result in a favorable four-role paid-call model.** Adding the rank-one address (R=(1,1/2)^T(1,1/2)) lowers the first-order floor for the Cycle 21 target from eight to six. An exact search of every word allowed by that new floor checks 388,800 candidates and finds no six-call identity. The direct eight-call word still works. This rules out the first possible two-call saving and proves a lower bound of seven calls; it does not determine whether seven calls are attainable.

## Model and changed premise

Work in the formal group algebra

\[
\mathbb F_2[\Lambda],\qquad \Lambda=\mathbb Z A+\mathbb Z P+\mathbb Z R.
\]

The five paid addresses are the explicit rational rank-one matrices

\[
A=\begin{pmatrix}1&0\\0&0\end{pmatrix},\quad
B=\begin{pmatrix}0&0\\0&1\end{pmatrix},\quad
P=\tfrac12\begin{pmatrix}1&1\\1&1\end{pmatrix},\quad
Q=\tfrac12\begin{pmatrix}1&-1\\-1&1\end{pmatrix},\quad
R=\begin{pmatrix}1&1/2\\1/2&1/4\end{pmatrix}.
\]

Each is supplied with an exact rational outer-product factorization in the verifier. They satisfy

\[
Q=A+B-P,\qquad 4R=2A-B+4P.
\]

The old lattice \(\mathbb ZA+\mathbb ZB+\mathbb ZP\) has index four in the new lattice. In the new integral basis \((A,P,R)\),

\[
B=2A+4P-4R,\qquad Q=3A+3P-4R.
\]

There are four binary roles. A paid factor chooses one address \(F\in\{A,B,P,Q,R\}\) and one of the 120 rank-one idempotents \(N\in M_4(\mathbb F_2)\), and applies

\[
D_N(F)=I_4+([F]-1)N.
\]

Binary mixing between roles is free in this formal model. The unchanged target is

\[
T=\operatorname{diag}([A+P],[A+Q],[B+P],[B+Q]).
\]

Each target address is a direct pair of legal alphabet elements on its role, so the diagonal coordinate projectors give a valid direct word with two calls per role, eight calls total. The exact target matrices all have determinant \(1/2\). This scope directly follows the open question in Cycle 21 [PR #2085](https://github.com/CrocSwap/integer-mult-bounds/pull/2085); its canonical follow-up claim is [Discussion #2091](https://github.com/CrocSwap/integer-mult-bounds/discussions/2091#discussioncomment-18932519).

The closest new handoff is [PR #2110](https://github.com/CrocSwap/integer-mult-bounds/pull/2110), which proves a general \(k\ge mW\) floor for an odd frame-clearing denominator and invertible cleared data targets. Its stated next question proposes a dyadic example. The address lattice here needs denominator four, while the target matrices clear at denominator two and each \(2C_i\bmod2\) has rank one, so neither odd-denominator hypothesis applies. This package answers one specific dyadic four-role instance with an exact full-word six-call obstruction; it proves no general even-denominator floor. See [PREDECESSORS.json](PREDECESSORS.json) for the exact head and scope comparison.

## First-order floor and exact six-call candidate set

Modulo the square of the augmentation ideal, the label directions in basis \((A,P,R)\) are

\[
A=(1,0,0),\quad P=(0,1,0),\quad R=(0,0,1),\quad B=(0,0,0),\quad Q=(1,1,0).
\]

The target diagonal masks in those three directions are

\[
P_A=\operatorname{diag}(1,0,0,1),\qquad
P_P=I_4,\qquad P_R=0.
\]

For a word, let \(S_F\) be the sum over \(\mathbb F_2\) of its idempotents on calls labelled \(F\). Necessarily

\[
S_A+S_Q=P_A,\qquad S_P+S_Q=I_4,\qquad S_R=0.
\]

If \(m\) rank-one idempotents sum to \(S\), then \(\operatorname{rank}(S)\le m\) and \(m\equiv\operatorname{tr}(S)\pmod 2\). Thus at least

\[
f(S)=\operatorname{rank}(S)+\bigl((\operatorname{rank}(S)-\operatorname{tr}(S))\bmod 2\bigr)
\]

calls are needed for that sum. Exact minimization over all 65,536 possible \(S_Q\) gives

\[
\min_S\bigl(f(S)+f(S+P_A)+f(S+I_4)\bigr)=4,
\]

with the unique minimizer \(S_Q=P_A\). It forces \(S_A=0\) and \(S_P=\operatorname{diag}(0,1,1,0)\). Since \(S_R=0\), any word using \(R\) has an even, positive number of \(R\) calls, hence at least two. The other labels cost at least four calls by the visible floor, so the new alphabet has a global first-order floor of six. If no \(R\) call is used, the old \(\{A,B,P,Q\}\) first-order floor remains eight.

Equality at six calls leaves no calls for \(A\) or \(B\): a candidate must use exactly two \(Q\) projectors with XOR \(P_A\), two \(P\) projectors with XOR \(\operatorname{diag}(0,1,1,0)\), and two equal \(R\) projectors. The exact pair counts are 3, 3, and 120. For each choice, there are 360 distinct orderings after identifying the repeated \(R\) factor. This gives exactly

\[
3\cdot3\cdot120\cdot360=388{,}800
\]

candidate words.

## Exact result and limits

The verifier multiplies every candidate as a sparse matrix over the full torsion-free group algebra. It checks all 388,800 words; none equals \(T\). Together with the global first-order floor, this proves that the five-address model needs at least seven calls. The direct eight-call word gives the interval \(7\le m_{\min}\le8\). Seven-call words were not searched.

The replay includes exact \(\mathbb Q\) checks for the frames, lattice relation, target coordinates, and determinants; it verifies that denominator four clears the full address lattice, denominator two clears the targets, and every \(2C_i\bmod2\) has rank one. It generates and validates the complete 120-projector alphabet, exhausts the mask relaxation, checks the direct eight-call word, and confirms that a target with one output removed fails that positive control. The finite search is complete for six-call words because every word achieving that count must meet the unique first-order pattern above. This is not a universal lower bound for other address families or role counts.

All frame setup, additions, precision, and supplier/interface costs are outside this paid-call model. The extra address has a rational outer-product implementation, but this result neither prices its full native use nor constructs a cheaper supplier. The pinned selected baseline still has the complex primitive binding, so no selected \(\kappa\) change is claimed.

## Provenance, overlap, and reproduction

Cycle 22 used seed `0d9888a62e4721895567ab6fd3af5262`, task `bit-new-register-model`, priority revision 4, scope key `7f5f4426ef796683c485`, and exact base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The task-catalogue SHA-256 is `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`; the selected-record SHA-256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. `TASK.json`, `SOURCES.json`, and `PREDECESSORS.json` retain exact provenance. The [overlap snapshot](OVERLAP.json) records complete live pagination of 376 open PRs and 755 Discussions. It found no literal match, but manual inspection found the closely adjacent odd-denominator result in [PR #2110](https://github.com/CrocSwap/integer-mult-bounds/pull/2110); its hypotheses exclude this denominator-four, mod-two-singular target, and its open question proposes a dyadic example. The helper does not search arbitrary code diffs or every nested package file, so the scan is not a novelty certificate.

Run from the repository root:

```sh
python3 scripts/research_package.py --package research/bit-fifth-rational-frame-six-call-seed0d9888a6 --check-only
python3.12 scripts/research_package.py --package research/bit-fifth-rational-frame-six-call-seed0d9888a6
```

The local exact replay prints:

```text
PASS_FIFTH_RATIONAL_FRAME_NO_SIX_CALL_WORD visible_floor=4 global_floor=6 no_R_floor=8 projectors=120 candidates=388800 checked=388800 direct_calls=8 no_six=>calls_at_least_7
```

The expected generic replay uses Python 3.12. Local testing environment and any unavailable interpreter are recorded in the handoff. The selected baseline command was separately run and returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it is not a full cold replay of the selected multiplication construction.

## Open next questions

The first open question is whether a seven-call word exists in this same five-address alphabet. A bounded next step is to derive every first-order profile with two \(R\) calls and at most five visible calls, then estimate the exact search size before enumeration. Any resulting one-call saving would still require a complete native frame and addition invoice.

## Credit

Prepared by Cinna Davis (1337isnot1337), with substantial OpenAI Codex assistance in scope selection, mathematical derivation, exact search implementation, overlap review, verification, and package writing. The closest predecessor remains [Cycle 21 PR #2085](https://github.com/CrocSwap/integer-mult-bounds/pull/2085), which established the exact eight-call result on the four-address alphabet. New work is Apache-2.0.
