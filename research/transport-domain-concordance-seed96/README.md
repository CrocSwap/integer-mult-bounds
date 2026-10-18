# Transport exclusions: the first-position quotient needs a continuation argument

**Research consolidation with an exact synthetic counterexample; no new kappa.**

PR1392 asks whether its two-transport domain corresponds to PR933's earlier
search. A first-position quotient prevents a direct identification. PR933's
unmodified enumerator retains 101 interacting two-move paths on the five-gate
fixture below; none improves its baseline under **any** permitted frame
assignment. Enumerating the literal positions gives 194 paths, including an
improvement that the quotient omits. This remains a counterexample when every
gate is globally reframed, as in PR933, rather than only the moved gate.

On the actual PR589 word, we also exhibit equivalent first positions with
different continuations. That example has **unchanged cost**. This package does
not refute PR933's reported PR589 optimum, reproduce its complete exclusion, or
establish equivalence of the two published search domains. It identifies the
specific continuation argument that cannot be supplied by the first-position
equivalence alone.

## Sources and the discrepancy

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The selected record at this base
is the maintainer-reviewed conditional PR1094 witness,
`kappa = 836330098538459/500000000000000000`. Its complex side binds.
The source-binding baseline passes; the full selected cold replay was not run.

| Source | Exact head | Relevant boundary |
| --- | --- | --- |
| Ian Libânio, [PR933](https://github.com/CrocSwap/integer-mult-bounds/pull/933) | `b9348c6907516e55dc07e135ad4d7a480d4f9840` | Grouped summand/whole-gate and cross-scatter moves; all closed frames reoptimized. `slots()` keeps one position per own-register contact pattern; `pairs.py` reuses these first representatives. |
| Brian Ross, [PR1392](https://github.com/CrocSwap/integer-mult-bounds/pull/1392) | `bedd71af790bb151590be45599cb5bafe89d9723` | Elementary same-section moves, original 636-frame catalogue plus each slot's lower-span closure, legal intermediates. Its pair projection retains first positions that can affect the other mover. |

Their counts measure different objects. PR1392 already explains why an
own-touch quotient is unsafe for continuation and supplies a synthetic
fixed-frame control. The new five-gate fixture tests **PR933's actual code with
global reframing**, including cleanup. The actual-word fixture supplies the
missing source-specific contact example. Both add evidence to that earlier
warning; no priority for the general warning is claimed.

[SOURCES.json](SOURCES.json) records Git blob and SHA256 identities. The small
source snapshots in `vendor/` are byte-identical, including their credits and
AI disclosures. Neither predecessor is modified. Their README/proof snapshots
are historical source statements, not additional findings of this package.

## Five-gate counterexample

Let `L = span(e1,e2)` and `H = Q^8`, with the eight coordinate lines as the
frame geometry. Every subset is a closed frame. Use dirty helpers `a=16`,
`b=17`, `c=18`, and targets `d1=8`, `d2=9`, `d3=10` in a 19-register word.
The entry frames are `a:e1`, `b:H`, `c:e2`, and `di:0`. Exit frames are `H`
for the helpers and `L` for the targets; unused registers stay at frame zero.
There are no D gates, retained COPY rows or scatter operations.

The B word is:

```text
y: a ^= c @ L
x: b ^= a @ H
z1: d1 ^= c @ L
z2: d2 ^= c @ L
z3: d3 ^= c @ L
```

C is the literal reverse of the helper-destination gates, `x` then `y`, both
at H. The completed scalar map adds the original dirty `c` to all three targets
and restores all helpers. The checker verifies all 19 independent input columns.
These are specified abstract entry/exit contracts, not a physically admitted
P111 supplier or an implementation of the full H1–H5 interface.

Moving x right across all three z gates changes no register's own gate order.
Its original position is therefore the sole first representative of that
class, and the identity representative is omitted by `candidates()`. However,
the literal move is legal: x commutes with every zi. After it, y can move right
across all three zi to just before x. That second move is also legal, whereas
y cannot cross x in the original word.

The resulting word `z1,z2,z3,y,x` admits frames `L,L,L,H,H`. All frame changes,
the two cleanup gates and the final boundaries are charged:

| Register | Baseline charged ranks | Attaining charged ranks |
| --- | --- | --- |
| a | 1, 6 | 7 |
| b | none | none |
| c | 1, 6 | 1, 6 |
| d1, d2, d3 | 2 each | 2 each |

Thus the complete local profiles are
`{1:2, 2:3, 6:2}` and `{1:1, 2:3, 6:1, 7:1}`: equal rank mass 20, seven
versus six calls. For every `0 < p < 1`, strict subadditivity gives
`7^p < 6^p + 1`. The second profile therefore costs strictly less for every
rank-power cost in this range. A nonnegative uniform surcharge per child also
cannot reverse the comparison. This is a local profile comparison, not a new
certified supplier root or outer bound.

The separate integer oracle enumerates **all** closed coordinate-frame
assignments. Across the 101 retained pairs, the only profiles are the baseline
and the profiles obtained by splitting one or two rank-two calls into pairs
of rank-one calls. Concavity makes each split more expensive. This proves the
baseline bound without relying on floating-point optimization.

The unmodified PR933 source separately chooses the baseline in all 101 cases
at exponent 1/2. That is an observed source result; the independent exhaustive
frame enumeration and integer majorization checks certify the all-exponent
statement. Including baseline and one-move states, the quotient census has
30 distinct orders and 48 legal frame assignments; the literal census has
51 orders and 333 assignments. These are counts for this fixture only.
We do not claim that the exhibited literal improvement is the global optimum.

A positive boundary control deletes the third reader. The representative
search then includes a cheaper two-move path by moving both remaining readers
before y. The failure therefore does not follow merely from testing two moves
or from a checker that always rejects improvements.

## Actual PR589 contact witness

Indices below refer to elementary A occurrences in the pinned PR589 word;
these particular occurrences also have the same grouped indices.

* `x = A[250]: 243 ^= 9`, at frame mask 512 (original frame ID 11).
* `y = A[18]: 240 ^= 9`, at the same frame.
* `A[244]: 482 ^= 240` is a noncommuting blocker for y.

Remove x and reinsert it at full-list slot 243, before original A[243]. Every
register's complete labeled contact itinerary is unchanged. PR933's `slots()`
keeps original slot 250 and omits slot 243. From the omitted position, remove
y and reinsert it at current full-list slot 243, immediately after x.

The resulting source-9 order puts x before y. From the original representative,
a y-only continuation cannot reach that order: the blocker occurs before x.
This proves that the first equivalence is not an equivalence of these fixed
second-operation continuations. Another pair of moves might reach the same
final word or cost; that possibility is not excluded.

Three full words—baseline, after x, and after y—pass a separately implemented
661-column dirty scalar replay and exact integer-rank invoices. All nine COPY
frames and the complete local profile remain identical:
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`. The independent invoices
also agree with PR1392's unmodified frame checker. This is a contact-coverage
example, **not a PR589 improvement or a counterexample to its reported optimum**.

## Reproduce and verification boundary

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/transport-domain-concordance-seed96
```

Expected: `PASS_TRANSPORT_CONCORDANCE quotient_pairs=101 literal_pairs=194
dirty_columns=19+661 controls=9 kappa=unchanged`, passing integrity tests, then
`PASS_REGISTERED_RESEARCH_PACKAGE`.

The [certificate](CERTIFICATE.json) is regenerated in memory and compared in
full. The nine semantic controls cover false cost exclusions, omitted cleanup
charges, noncommuting moves, unrestored dirt, wrong geometry, an actual frame
descent, and the two-reader positive case. Subprocess tests separately reject
source, fixture and certificate corruption and check a relocated source-only
export under optimized Python. No test relies on an `assert` being enabled in
the new verifier.

This is a finite computer-assisted result with a short exact cost argument,
not a proof-assistant formalization. Neither large predecessor pair census,
native multistage/hosted admission, numerical precision, the selected cold
replay nor the multiplication theorem is verified here. Their inherited
compiler, realization, hosting, precision/tape and analytic assumptions remain.

The seed-96 selection, bounded exploratory search, overlap coverage and one
evidence-driven scope refinement are recorded in [TASK.json](TASK.json).
The exploratory prefix found no missing paid profile in its stated domain;
it is not an impossibility theorem or a completed PR589 correspondence proof.

## Open next questions

Can PR933's particular PR589 pair exclusion be justified by a stronger
word-specific dominance argument, or by retaining additional first positions?
This matters because contact equivalence alone does not establish continuation
coverage. A bounded first step is to compare all first positions for a named
pair, retaining its union of touched registers while preserving grouped gates
and global frame constraints. The unresolved blocker is a valid reduction for
that globally reframed domain; PR1392's smaller fixed-catalogue reduction cannot
simply be substituted. This package neither accepts nor rejects that full
PR589 exclusion.

## Credit and license

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in investigation, implementation, verification and writing. No independent
human review is claimed. The new oracle is implementation-independent of the
retained enumerators; both were run by the same assisted contributor.

Credit Ian Libânio / PR933 for the search, quotient and global frame model;
Brian Ross / PR1392 for the explicit correspondence question, continuation
warning, prior synthetic control and fixed-catalogue checker; flemhhh / PR1048
and woklerx / PR1182 for the adjacent search/pricing lineage; DreamingOfClouds /
PR589, eumemic and their retained predecessors for the actual word; and
SethBurkart123 / PR886 for the frame-optimization lineage. Existing source
notices are preserved. New material is Apache-2.0.
