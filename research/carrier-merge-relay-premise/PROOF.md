# A source-normal premise for relay-enabled carrier merges

## Result and classification

At the exact source head of CrocSwap/integer-mult-bounds#6315, the application of
the merge lemmas to public-relay walks needs an additional argument. Common-frame
merging does not, by itself, retain every source normal in the merge dual. The
Lean theorem statements retain the required hypotheses explicitly. This audit
identifies a missing application implication, not a false Lean theorem and not
a physical counterexample to the pair cost floor 14 or the owned cost floor 56.

The exact countermodels below satisfy the declared **abstract dual-frame walk**
rules, source origins, common merge, and coverage of every required receiver.
They do not supply scalar decoding coefficients, a pure-carrier public relay,
or restoration of arbitrary public dirt. Those obligations can obstruct these
walks and might support a corrected physical theorem.

The repaired invariant is

\[
 \operatorname{total}+(k-1)\tau\ \ge\ 7k+\sum_{c=1}^k\eta_c,
 \qquad \eta_c\in\{0,1\}.
\]

Here \(\eta_c\) records whether the carrier's pre-merge and tail union escapes
its eight-dimensional receiver hyperplane. An explicit source-normal retention
condition recovers the predecessor's \(8k\) right-hand side. **No new κ.**

## 1. Exact source and missing implication

The audited head is `3667554dab1bf08bb9ce6c267b6047fdc9978498`, by Matarener.
The five relevant source files are retained verbatim under `inputs/`, with
original repository/head/path, SHA-256 and Git-blob pins in `PREDECESSOR.json`.
The metadata manifest is itself pinned by the verifier. The original Git bytes
were compared before publication; portable replay needs no pending Git history.
All line numbers below refer to those unchanged files.

| Source | Hypothesis or application |
|---|---|
| `pr6315-PROOF.md`, lines 13–20 | Public ascents may shrink duals freely; information walks permit such steps. |
| `pr6315-PROOF.md`, lines 43–50 | Uses the other carrier's normal to conclude \(Z_c+T=\mathbb F_2^9\). |
| `pr6315-Walk.lean`, lines 152–153 | `sup_top_of_cover` requires the supplied subspace `G` to lie in `Z`. |
| `pr6315-Walk.lean`, lines 173–175 | `merge_count` assumes `htop`: every \(Z_c+T\) is the full space. |
| `pr6315-Walk.lean`, lines 205–207 | `pair_merge` additionally assumes `hG : G ≤ W`. |
| `pr6315-Walk.lean`, line 217 | `hG` supplies the common source subspace to the finite no-cover predicate. |

The finite fact \(\langle g_a,g_c\rangle+\operatorname{span}R_c=V\) is not the
missing implication. To use it, the application must place \(g_a\) in the
relevant union, or prove an equivalent full-span condition. A common merge
frame only places its own dual \(W\) in each path union; it does not prove
\(g_a\in W\), or even \(g_a\in Z_c+T\), after arbitrary shrinking steps.

For two carriers, the formal sufficient condition is
\(\langle g_a,g_b\rangle\subseteq W\). A weaker repair might suffice for the
application, but it must also establish the source-subspace inclusions used by
the finite no-cover check. This audit does not re-audit that finite search or
the separate decoder coefficient argument.

## 2. Concrete selected geometry

Work in \(V=\mathbb F_2^9\), with the standard binary dot product. The selected
#6030 word supplies its 104 port vectors \(P\). The #6315 receipt supplies these
paired delivery lines and source normals:

| c | \(\ell_c\) | \(g_c\) |
|---|---:|---:|
| 0 | 7 | 104 |
| 1 | 25 | 162 |
| 2 | 52 | 266 |
| 3 | 67 | 97 |
| 4 | 82 | 289 |
| 5 | 137 | 127 |
| 6 | 448 | 42 |
| 7 | 491 | 76 |

Integers encode nine binary coordinates. For
\(R_c=\{p\in P:p\cdot\ell_c=0\}\) and \(H_c=\ell_c^\perp\), the independent
checker verifies directly from these inputs that

\[
 |R_c|=52,\quad
 H_c=\langle g_c\rangle+\operatorname{span}R_c,\quad
 \dim H_c=8,\quad
 g_a\cdot\ell_c=[a\ne c].
\]

It does not import the predecessor interpreter. The identity of the source
receipt's eight carriers with the complete scalar program is inherited; the
specific geometric facts used here are independently checked against the
selected port list. No full selected word or decoder replay is claimed.

## 3. Receiver-covering walk countermodels

For any subset \(U\subseteq\{0,\ldots,7\}\) with \(k=|U|\ge2\), take the
following pre-merge dual walk for every \(c\in U\):

\[
 \langle g_c\rangle\ \longrightarrow\ H_c\ \longrightarrow\ \{0\}.
\]

The first step is growth from dimension one to eight, paid at seven. The
second is a free shrink under the declared information-walk rules. All 52
receivers lie in the visited node \(H_c\). Set the common merge dual and the
tail union to \(W=T=\{0\}\), with tail cost \(\tau=0\). The path union is
exactly \(Z_c=H_c\), and the total frame-walk price is \(7k\).

Thus all source roots, nested steps, receiver coverage, common-merge conditions
and walk-union price inequalities hold, while

\[
 \langle g_a:a\in U\rangle\not\subseteq W,
 \qquad Z_c+T=H_c\ne V.
\]

For example, \(g_1=162\notin H_0=7^\perp\), because \(162\cdot7=1\).
The common merge therefore does not force carrier 0's union to contain the
other source normal. The countermodel exists already for the pair \(\{0,1\}\)
and the triple \(\{0,1,2\}\). The verifier checks all 247 subsets of sizes two
through eight, including all 28 pairs and all 56 triples.

In primal frames the walk is
\(g_c^\perp\to\langle\ell_c\rangle\to V\): an owned descent followed by the
frame pattern of a public ascent. This is a countermodel to the proposed
**frame-only implication**. Reading into an arbitrary public helper can add
its dirt. No pure scalar relay, its dirty restoration, or the resulting full
physical invoice is constructed here. In particular the pair example costs
14, so it is not even an abstract witness below the pair floor 14.

The gap does not require a zero-dimensional merge dual. For the pair
\(\{0,1\}\) and triple \(\{0,1,2\}\), the selected port \(p=11\) lies in every
required \(H_c\). Replace the final zero by \(W=T=\langle11\rangle\).
All unions and paid costs remain unchanged, and both missing hypotheses still
fail. The common primal chart is the actual final chart 128 of selected
register Y112, whose basis is `(3,4,9,16,32,64,128,256)`; the checker verifies
that this is exactly \(11^\perp\). There are 22 common selected receiver ports
for this pair and seven for this triple. These fixtures establish availability
of an actual endpoint chart; they still do not install multiple pure carriers
and arbitrary dirty relays into a complete scalar program.

## 4. Repaired invariant

Choose \(1\le k\le8\) distinct carriers from the fixed selected code. For each
chosen carrier \(c\), assume:

1. Its pre-merge union \(Z_c\) contains \(g_c\), and its paid cost \(p_c\)
   satisfies \(\dim Z_c\le p_c+1\).
2. Every required receiver lies in \(Z_c\cup T\).
3. The merge dual obeys \(W\subseteq Z_c\cap T\), and tail cost satisfies
   \(\dim T\le\tau+\dim W\).

Since \(H_c=\langle g_c\rangle+\operatorname{span}R_c\), the first two
conditions give \(H_c\subseteq Z_c+T\). Define

\[
 \eta_c=\begin{cases}0,&Z_c+T\subseteq H_c,\\1,&\text{otherwise.}\end{cases}
\]

The hyperplane has dimension eight, hence \(\dim(Z_c+T)=8+\eta_c\).
The subspace dimension identity and \(W\subseteq Z_c\cap T\) give

\[
 8+\eta_c+\dim W
 \le \dim Z_c+\dim T
 \le p_c+1+\tau+\dim W.
\]

Therefore \(p_c+\tau\ge7+\eta_c\). Sum over \(c\), and put
\(\operatorname{total}=\sum_c p_c+\tau\), to obtain

\[
 \operatorname{total}+(k-1)\tau\ge7k+\sum_c\eta_c.
\]

This proof is a dimension argument for arbitrary walks of those chosen
carriers in the stated relaxation, not an inference from the finite checks. The countermodels attain
equality with every \(\eta_c=0\), so replacing \(7k\) universally by \(8k\)
under just these hypotheses is impossible.

If \(k\ge2\) and every source normal is retained in \(W\), choose \(a\ne c\).
Then \(g_a\in W\subseteq Z_c+T\) and \(g_a\cdot\ell_c=1\), forcing
\(\eta_c=1\). The predecessor's \(8k\) inequality follows. In particular,
pre-merge walks consisting only of owned descents preserve their root normals;
more generally it suffices that every pre-merge step retains its own normal.
Arbitrary public-relay shrinking is the boundary that still needs a proof.

## 5. Consequence and remaining obligation

The repaired inequality also exposes the finite pair check's scope. If a
hypothetical pair has `total <= 13`, then
\(p_b+\tau\ge7+\eta_b\) implies
\(\dim Z_a\le p_a+1\le7-\eta_b\), and symmetrically
\(\dim Z_b\le7-\eta_a\). The predecessor's six-dimensional no-cover
domain is recovered when both indicators are one. Without full-span it can
instead require dimension-seven coverage, which that finite certificate does
not establish. This consequence was identified independently by reviewer D;
it is a scope diagnosis, not evidence of a cheaper physical pair.

The predecessor's Lean statements can remain unchanged. Its general walk and
single-carrier statements are not contradicted. To apply the stronger merge
floor to relay-enabled physical programs, supply a source-bound theorem that
either retains the required normals, establishes the necessary full-span and
no-cover hypotheses another way, or charges the extra work needed to erase and
restore those directions. An explicit purity/restoration theorem could resolve
this gap; its absence is not a physical counterexample.

Until then, an extension to three-carrier merges cannot simply inherit the
stronger \(8k\) premise from a common merge frame. No triple-merger exclusion,
native implementation, complete signed supplier invoice, or improvement to the
multiplication bound is established here. All five selected assumptions remain.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Credit
Matarener for #6315 and #6267; DreamingOfClouds for the selected #6030 word;
the carrier uniqueness, fragmentation and owned-boundary predecessors cited in
the retained source; and the classical subspace dimension identity.
