# Return lengths four and six coexist at exactly two revisits

This contribution is produced by Nick Petalas. Apache-2.0.

**Claim type: two exact finite attainers and a scoped counting argument.**
At length 22, return lengths 4 and 6 can coexist with exactly two revisits,
at both parity splits `(11,9)` and `(10,10)`. Five labels suffice for each
split and are necessary at two revisits. The new witnesses answer the first
bounded case in unpaidmoon's [PR #4120](https://github.com/CrocSwap/integer-mult-bounds/pull/4120),
`research/revisit-one-return-gap/README.md`, Open next questions.

The predecessor's one-revisit exclusion is a cited input, not a result
rechecked here. Combining it with these new attainers makes the least
revisit count exactly two. No new kappa or value of `f(7)` is claimed.

## Contract and witnesses

A word `a[0],...,a[21]` has labels in `{0,1,2,3,4}`. Start at `q[0]=0`
and set `q[t+1]=q[t] XOR 2^a[t]`. A restored word has `q[22]=q[0]`.
The distinct-prefix set is `P={q[0],...,q[21]}`. Its revisit count is
`22-|P|`; the final mandatory return is excluded from this count.
The parity split is the unordered pair of even- and odd-weight counts in P.
A linear prefix return of length k is a pair `0<=i<j<=22` with
`q[i]=q[j]` and `j-i=k`. Intervals are not wrapped around the end.

The certificate [WITNESSES.json](WITNESSES.json) contains these two words:

```text
(11,9):  0 1 0 1 2 0 1 2 3 0 1 0 2 0 1 0 4 0 1 2 3 4
(10,10): 0 1 0 1 2 4 0 3 0 4 3 0 1 0 3 0 1 2 1 0 1 3
```

Their full prefix lists are:

```text
(11,9):  0,1,3,2,0,4,5,7,3,11,10,8,9,13,12,14,15,31,30,28,24,16,0
(10,10): 0,1,3,2,0,4,20,21,29,28,12,4,5,7,6,14,15,13,9,11,10,8,0
```

In the first word the repeated nonzero state is `q[2]=q[8]=3`.
In the second it is `q[5]=q[11]=4`. Both have the origin at positions
0, 4 and 22. Every other listed state occurs once. Thus each has exactly
20 distinct states, and all equal-position distances are exactly
`{4,6,18,22}`. Counting the weights of those 20 distinct states gives
the displayed parity splits. These statements can be checked directly
from the two lists; the generated [RESULT.json](RESULT.json) also records
every equal-position pair.

## Sharpness and consequence

At zero revisits the first 22 prefixes are distinct, so the only return
is the mandatory length 22. PR #4120 excludes simultaneous lengths 4 and
6 at one revisit, over any alphabet, by classifying the possible repeated
position patterns. We use that exclusion at its stated strength and do
not replay its 231 patterns. The two new witnesses therefore attain its
next possible revisit count.

At exactly two revisits, every length-22 word has 20 distinct prefix
states. A four-label cube has only `2^4=16` states, so four labels cannot
suffice. Both words use all five labels and lie in the 32-state five-label
cube. Five is therefore the exact minimum alphabet size at this revisit
count, separately for each of the two parity splits.

The witnesses embed in a seven-label alphabet by leaving two coordinates
unused. This is a feasibility statement about return constraints. It does
not make either word universal over seven labels. In particular, a proposed
length-22 prune cannot exclude either two-revisit split merely by declaring
return lengths 4 and 6 incompatible. A valid stronger prune needs additional
conditions that these words fail.

## Reproduction and evidence

From the repository root, CPython 3.12 and its standard library suffice:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/revisit-two-return-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/revisit-two-return-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/revisit-two-return-threshold
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/revisit-two-return-threshold --check-source-history
```

Any CPython 3.12 path can replace the displayed interpreter. The standalone
verifier is read-only and needs neither Git nor predecessor files. It computes
prefix XOR states, then independently reconstructs coordinate tuples and
tests every interval by counting each label modulo two. Both engines compare
the full observations. They check the two new words, all 120 label bijections
per word, reversal, and every one of the 32 starting vertices. The 306
transformed cases are implementation corroboration, not additional research
targets. Seven controls reject a changed endpoint, deleted step, boolean
label, out-of-range label, false split, boolean split, and a restored word
with the wrong return and revisit counts.

`--emit` computes a receipt on standard output. Ordinary verification recomputes
it and compares every field and type with RESULT.json. The receipt binds the
six other package files by SHA256. SOURCES.json pins the cited predecessor
README and orientation metadata as provenance only. No predecessor code,
counts or scientific receipt is imported or checked by this verifier.

## Limits and implementation discipline

This is not a word census, a classification of all pairs of return lengths,
or an exclusion of any universal-word split. It supplies no physical caller,
paid-profile improvement, supplier admission, selected-frontier change or
complete multiplication theorem. The least-revisit conclusion uses the
cited predecessor exclusion. The five-label minimum at two revisits follows
from the state count and the new witnesses alone. Independent human and
formal proof-kernel review are unclaimed. The five selected framework
assumptions remain separate. Lean, Docker and the selected full replay are
outside the verification scope.

The verifier has no recursion, subprocesses, dynamic code loading or external
runtime inputs. Fixed limits are two 22-step words on five coordinates,
253 intervals per word, 120 label permutations and 32 starting states per
word, and 256 KiB per file read. All functions are under 60 physical lines.
Explicit exceptions keep every check active under optimized Python.
Warning-strict normal and optimized runs are the recurring diagnostics;
no separate Python static analyzer is configured for this package.

Power-of-ten rule 3 deviation: CPython and its standard library allocate
managed objects during exact checking. This is confined to the stated fixed
domains; each state list has 23 entries, and the transformation list has
121 words of length 22. Receipt hashing reads one bounded file at a time.
Both registered modes exercise the complete domains. A fixed-capacity port
would be required before claiming allocation-free execution or expanding
these limits. Interpreter allocation has not been independently instrumented.

## Open next questions

- Which other pairs of even lengths in `{4,6,...,18}` coexist at exactly two
  revisits? This matters for any joint-return pruning rule. Start with the
  repeated-position patterns at 20 distinct prefixes, then provide cube
  embeddings for surviving patterns. Position feasibility alone does not
  prove a hypercube embedding; the full pair spectrum is not supplied here.
- Does a source-bound universal-word search gain a sound prune after adding
  its actual pairwise-XOR coverage condition? First state that stronger
  condition and test it against both new attainers. These words establish
  only that the two return lengths and parity split alone are insufficient.
  A complete universal-word census requires a separate resource budget.

## Credit and provenance

The new two-revisit attainers, five-label sharpness application and standalone
checker are produced by Nick Petalas. Credit unpaidmoon / PR #4120 for the
one-revisit exclusion and the explicit next question; James Reed / PR #3730
for the separate even-length existence cover, PR #3726 for the earlier
length-two witnesses, Nick Petalas / PR #3708 for the split/revisit convention,
Ross Richardson / PR #943 for the prefix-walk model, and Nicholas Stone /
PR #2973 for the corrected parity framework. Those results are cited, not
revalidated or replaced. The pigeonhole argument is classical.

Scientific base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8, selected #6030. The card's audit premise is explicitly
changed to constructive return feasibility. Live PR bodies, recent handoff
claims, local reservations, merged searches and all-main README searches
were inspected before the advance claim. The generic overlap cache covers
745 open PRs but has no Discussion snapshot and omits most sparse local
notes; the relevant Discussion was read live and main READMEs separately.
These are bounded overlap checks, not a proof of novelty. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19441338)
records the reserved pair and stops at the first verified improvement.
