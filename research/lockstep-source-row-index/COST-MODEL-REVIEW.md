# Independent computational-model review of the source index

Reviewer: `/root/tape_dispatch`, with OpenAI assistance for @CubeJerry's
research run. Date: 2026-11-11. Scientific base:
`e54523517d0f03e58352e647c403a5af3e525a57`.

## Scope and snapshot

This is a source-reading and mathematical cost review of section 5, not a
runtime replay or a replacement for checking the indexing identities. The
author's files were not modified. Reviewed SHA256 pins, relative to
`work/compiler_source_index/package/`:

| File | SHA256 |
| --- | --- |
| `PROOF.md` | `5571b0e6329f620c4bf58e90fb03ce4dfefae95708435739f8fac5e78aa52c9b` |
| `source_index.py` | `b45f671eeac3d5dead19285cf5f455b705596e9f3679a2eddbdd225e4fbf3718` |
| `inputs/pascal_codec.py` | `cec2c8b5e153a264127e8301ed59591fe97c9a46078ff2343b3784d177c6984d` |

**Outcome: a repairable computational-model gap.** The current Python already
replaces growing state dictionaries/sets with `sorted_unique` and
`SortedStateTable`. That resolves the earlier hash-table objection for these
tables. Binary-search accesses and indexed value writes nevertheless have not
been lowered to a tape algorithm with paid seeks and returns. Calling the
displayed time formula bit work, or saying it is not unit-cost RAM, does not
alone establish those costs.

This does not refute the state aggregation or rank/unrank theorem. It also
does not show that no other implementation attains the sharper formula. A
specific memory-access argument is missing; the following conservative one
preserves the claimed polynomiality.

## Deterministic sequential alternative

Keep the author's definitions

\[
R=1+q\binom{G+q-1}{q},\quad M=\binom{G+d}{d},
\]

\[
B=S+\ell(N)+(G+1)\ell(A+W+P+G+2)+1,
\quad \ell(x)=\lceil\log_2(x+1)\rceil,
\quad L=(S+R+dM)B.
\]

Serialize input, profiles, state keys and local/total counts as delimited
binary records on a constant number of tapes. Scalar fields need O(B) bits;
a profile needs O(dB) bits. Padded count fields avoid variable-size shifts.
Group state records by depth and profiles in their specified lexicographic
order. The query path/output also fits O(L), since M is at least G+1 when
d is positive and individual indices fit O(B).

Generate one candidate next state from one current state and one distinct
paid rank. Scan the next-depth records to test membership; append only if
absent. There are at most qR candidate operations, and candidates are never
materialized simultaneously. Profile generation uses explicit bounded
counters/stack, with O(dB) work storage. Bottom-up recurrence evaluation and
rank/unrank find every count by a complete table scan. Role and paid-position
lookup uses the same convention. Return every work head to a marked origin
after each operation, or store and restore an explicit binary cursor. Charge
both choices.

A conservative O(L^2) moves per record/arithmetic operation suffices: there
are O(L) stored symbols and at most O(L) key comparisons per scan; charging
O(L) for each comparison and all candidate-key rewinds is already quadratic.
Origin returns, insertion, updates, explicit copies and output emission fit
that bound as well. Schoolbook O(B^2) scalar arithmetic is bounded by O(L^2).
The representation and a fixed number of scratch records occupy O(L) cells,
including historical blank backing. No paid-path tree or source list is
materialized.

Let the scalar/record-operation envelopes be

\[
K_{\rm setup}=(S+1)^2
[M(G+d+1)+R(M(d+1)+q+1)],
\]

\[
K_{\rm query}=(S+1)^2
[M(d+1)+GP+G+d+1].
\]

The profile loops, qR streamed candidate operations, state/profile recurrence
loops and chronological query loops fit these envelopes. Consequently an
explicit deterministic sequential alternative satisfies

\[
T_{\rm setup}=O(K_{\rm setup}L^2),\qquad
T_{\rm query}=O(K_{\rm query}L^2),\qquad
S_{\rm work}=O(L).
\]

This is an existence proof for the described sequential realization, not a
transition-count certification of the Python runtime. It is polynomial in
G and log N for each fixed native rule because q and d are fixed. A tighter
scan protocol could improve the deliberately loose exponent; no such claim
is necessary for this logical indexing advance.

## Suggested author change and retained limitations

Either use the conservative deterministic bounds above, labelling Python as
the reference mathematical implementation, or specify another deterministic
bit model and prove access, deduplication and cursor costs before retaining
the sharper formula. If both are shown, name their different models.

No native row lookup, gather, copy, erase, owner transfer, or payload
permutation follows. The actual selected role/owner manifest and native
routing tariffs remain obligations. The five selected assumptions remain.
**No new kappa; no unconditional multiplication theorem.**

## Resolution after the author's revision


The author revised section 5 and the table implementation while this review
was in progress. The reviewed repair snapshot is:

| File | SHA256 |
| --- | --- |
| `PROOF.md` | `1631e28072e1ad39c3833ec83ff7d59e35c4d8fd1ad45ebce6b777aed4125bdb` |
| `source_index.py` | `e978025591b06770026b9879f1e5b10827424f410794fb2b1e1f10a720f49176` |

The final proof pin adds a numeric-hash source reference and CPython wording
to the initially reviewed repair; the serialized-table argument was re-read
and is unchanged. The revised proof explicitly separates indexed metadata arithmetic/comparison
work from a deterministic serialized-table realization. It uses
L=(S+R+dM+1)B and the conservative O(K_setup L^2), O(K_query L^2), O(L)
time/space bounds, with candidate insertion, key access, copying, cursor
return, arithmetic and retirement charged. Its O(L) extra spare representation
keeps workspace within O(L). Streaming at most qR candidates prevents storing
qR states simultaneously. Valid query lengths and oversized malformed queries
are distinguished.

The revised code deduplicates current dilations before generating children;
at fixed paid rank the next-state map is injective. This also makes the total
sorted candidate count at most R, supporting the stated O(R log(R+1)) key
comparison tally. This reviewer accepts the computational-model repair for
this snapshot. The earlier finding is retained above as review history. The
separate collision-family audit and its asymptotic lower bound are outside
this review's assigned scope and were not independently verified here.
