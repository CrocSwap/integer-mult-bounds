# Exact subsequence counts for XOR layouts

Scoped all-size combinatorial proof, with finite corroboration. No new kappa.
This contribution is produced by Nick Petalas.

For the ordered permutation `p_m(x) = x xor m`, `0 <= x < 2^n`, the
number of longest strictly decreasing index subsequences is exactly

\[
 A(n,m)=2^{E(n,m)},\qquad
 E(n,m)=\sum_{\substack{0\le i<n\\m_i=0}}
           2^{\sum_{j=i+1}^{n-1}m_j}.                 \tag{1}
\]

Here `n >= 0`, `0 <= m < 2^n`, bit zero is the least significant bit,
and leading zero bits are part of the specified width. A subsequence is an
increasing list of indices with strictly decreasing permutation values.
Different index lists are counted separately. The empty subsequence is
counted once in the polynomial below. For `n=0` there is one address, so
`A(0,0)=1` and the longest subsequence has length one.

Mark (Matarener)'s [PR #3825](https://github.com/CrocSwap/integer-mult-bounds/pull/3825)
supplies the XOR split/merge pass-model context and the existing maximum
length `2^wt(m)`. James Reed's
[PR #3831](https://github.com/CrocSwap/integer-mult-bounds/pull/3831)
supplies finite length/composition evidence. The new quantity here is the
multiplicity, together with the complete length enumerator. Neither
predecessor's computations are replayed or claimed as a new result.

For example, at `n=2`, mask `01` gives `[1,0,3,2]` and exactly two
longest decreasing subsequences. Mask `10` gives `[2,3,0,1]` and exactly
four. Their common maximum length cannot distinguish these counts.

## Polynomial theorem and proof

Let `F_(n,m)(t)` count all decreasing index subsequences by length,
including the empty one. Define

\[
 H_0(f)=2f-1,\qquad H_1(f)=f^2.
\]

Then the exact polynomial is

\[
 F_{n,m}(t)=H_{m_{n-1}}\circ\cdots\circ H_{m_0}(1+t).       \tag{2}
\]

In particular, the maps are applied from the least significant bit to the
most significant bit. This order matters. The two examples above have
polynomials `1+4t+2t^2` and `1+4t+4t^2`.

To prove (2), remove the highest address bit and put `h=2^(n-1)`.
Let `q` be the XOR permutation on the lower `n-1` bits. If the highest
mask bit is zero, the full sequence is the concatenation `[q,q+h]`.
Every first-half value is smaller than every second-half value. A
nonempty decreasing subsequence lies in exactly one half. Therefore its
polynomial is `1+2(F_q-1)=2F_q-1`.

If the highest mask bit is one, the sequence is `[q+h,q]`. Every
first-half value is larger than every second-half value. Every decreasing
subsequence is uniquely the concatenation of one decreasing subsequence
from each half, either of which may be empty. The length adds and the
polynomial is `F_q^2`. The base sequence at `n=0` is `[0]`, with polynomial
`1+t`. Induction proves (2) for every width and mask.

For completeness, take the degree `L` and leading coefficient `A` in
this recurrence. The zero-bit step sends `(L,A)` to `(L,2A)`; the one-bit
step sends it to `(2L,A^2)`. Starting from `(1,1)` gives the inherited
length `L=2^wt(m)`. Write `A=2^E`. A zero bit adds one to `E`, and a one
bit doubles `E`. Thus the unit contributed by zero bit `i` is doubled
once for each higher one bit. Summing these contributions proves (1).
This also proves that the leading coefficient is always a power of two.

The proof counts actual index subsequences through disjoint choices. It
does not identify different choices merely because they have the same
length or mask weight. The formulas are unbounded mathematical claims;
the finite checks below are corroboration, not an induction substitute.
No literature-priority claim is made for the elementary decomposition.

## Evidence and reproduction

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/xor-subsequence-enumerator
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/xor-subsequence-enumerator --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/xor-subsequence-enumerator/verify.py
```

A portable equivalent uses any CPython 3.12 interpreter in place of the
absolute path. The registered commands run both normal and optimized
warning-strict checks. The direct checker needs only this package and
also works in an exported directory without Git.

`verify.py` computes (2) by integer polynomial arithmetic and (1) by its
explicit higher-bit sum. `oracle.py` imports neither formula. It counts
subsequences by endpoint and length in the literal permutation, enumerates
all index subsets in the smaller domain, and uses a separate Fenwick
maximum-length/count dynamic program for a larger domain.

The generated [RECEIPT.json](RECEIPT.json) binds all six source/metadata
files by SHA256 and records the deterministic result stream. The checker
regenerates the entire receipt and compares canonical bytes; booleans and
integers remain distinct JSON values. `--emit` prints a newly computed
receipt without comparing it or changing any file. No receipt is written
by hand.

The exhaustive domains include all masks and width zero. Polynomial
comparison uses widths `0..7`; subset enumeration uses widths `0..4`;
longest-count comparison uses widths `0..10`. These enumerate 255 complete
polynomials, 1,050,698 index subsets and 2,047 longest-count cases. Invalid widths, out-of-range
masks and Boolean/noninteger arguments reject. Semantic controls distinguish
bit order, a weight-only multiplicity rule, and an ignored-order binomial
enumerator. No acceptance check relies on Python `assert`.

Resource limits are separate from theorem scope. The polynomial API accepts
at most ten bits. The leading-parameter API accepts at most 4096 bits and
returns the multiplicity exponent instead of allocating the full count.
The oracle limits are explicit above. All loops have bounds from these
limits, with Fenwick traversals capped at `n+1` iterations. Python integer
and collection allocation is a managed-runtime deviation from fixed-memory
rules; live storage is bounded by those input limits. The only dynamic
module load has one fixed sibling path. Functions are below 60 lines.
Warning-strict normal/optimized replay supplies the available diagnostics;
no project-wide analysis configuration is changed.

## Scope, sources and overlap

Base canonical main is `624de9dc66858af0945e5f8a0942488d62280d43`,
priority revision 7. [TASK.json](TASK.json) records a changed
`formal-interface-lemma` scope, from proof-assistant binding to an exact
layout-counting side result. No formal proof assistant or independent human
review is claimed. The old card's baseline command fails with `KeyError:
'bit_lower'` against the current selected schema; the current
`research_selected_baseline.py` source-binding control passes. Neither is
scientific verification of this result.

[SOURCES.json](SOURCES.json) pins the catalogue, selected record and both
predecessor READMEs as historical provenance. They are not runtime inputs.
The new proof and code are self-contained and do not import predecessor
scripts or change their evidence. The selected frontier is untouched.

Entry overlap checks used live open PRs, recent handoffs, this account's
recent PRs, merged searches for XOR/decreasing/subsequence/polynomial terms,
and all-main README searches for the quantity and object. The broader card
cache reports 379 open PRs and 3,852 Discussion records with complete remote
pagination, but only 90 local records against 6,319 at HEAD. Sparse local
coverage, unpublished work and arbitrary code diffs are outside that scan.
Search absence is not a novelty certificate. The canonical
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133705)
precedes the new proof and finite checks.

The result refines the information available about XOR layouts. Multiplicity
alone strengthens no split/merge pass lower bound. There is no implemented
routing schedule, native cost reduction, new multitape lower bound, supplier
admission or complete multiplication theorem. Physical realization, stock,
restoration, precision, recursive costs and outer admission are unrun and
unpriced here. The first proved enumerative result is the stopping point.

## Open next questions

Can these exact subsequence choices be used to count or construct minimum
monotone-run partitions for one fixed XOR layout? Such a connection would
relate the new enumerator to a concrete split/merge schedule rather than
only a longest-subsequence statistic. Start with all masks at `n=3` and a
fully specified assignment of indices to ordered tapes. A precise partition
and pass contract is the blocker; neither the multiplicity nor the existing
length theorem supplies its physical cost. The structured question is in
[TASK.json](TASK.json).

## Credit

This contribution is produced by Nick Petalas. Credit Mark (Matarener) for
PR #3825's pass-model context and length lemma, James Reed for PR #3831's
finite length/composition certificate, and their retained Walsh, adapter,
layout and manuscript contributors. Their original credit is unchanged.
Independent human and formal proof-kernel review are unclaimed.
New material is Apache-2.0.
