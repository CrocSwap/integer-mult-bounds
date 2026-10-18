# P104 support audit: an omitted chronological path and a reversed cycle

**Independent audit of PR #3182, with two confirmed findings.** Its subspace
memory routine stops after recording the first eligible source at each output;
it consequently omits a literal nested-frame path `X1 -> H201 -> Y98` in the
pinned PR3019 matching. Separately, its second PR3124 cycle is reversed and
contains three incompatible endpoint pairs.

This is a scoped audit, not a correction supplier. It does not overturn
PR3032's different obstruction to PR3019, certify the repaired missing-pair
counts as lower bounds, or change the selected exponent. The separately tested
pooled missing pair `(Y71, X102)` survives the read-first control below.

The audited source is dcharb78's [PR3182](https://github.com/CrocSwap/integer-mult-bounds/pull/3182),
head `ad848966cd62e13de5ad8d4b5169c221d74d2fcd`, archived on base main
`463113d675af7410ac91d53a4fed51ec6494eb9a`. Its ledger status is
`partially_reviewed`: the archive intake did not independently run its science.
The claim is in [Discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-19001775).
Exact live bytes and historical task provenance are in [SOURCES.json](SOURCES.json).

## 1. The output loop drops sources

In `propagate_with_subspace_memory_bitmap`, the following branch is inside
`for s, subs in state[h].items()`:

```python
if any((S & f_y) == S for S in subs):
    outputs[t] |= 1 << s
    break
```

The `break` exits the **source loop**. Recording one eligible source does not
exhaust the source support. It must instead record every eligible source.

A one-helper, one-frame fixture with two independent inputs `X0,X1` illustrates
this without geometry or a search. The legacy routine returns only `{X0}`;
reversing enumeration returns only `{X1}`. Deleting that one `break` returns
`{X0,X1}` in both orders and both memory modes. This is a realizable dependency:
with arbitrary initial helper `H` and target `Y`, the six same-frame additions

```text
Y -= H; H += X0; H += X1; Y += H; H -= X1; H -= X0
```

give `Y_final = Y_initial + X0 + X1` and restore `H` exactly. The checker verifies
all four symbolic input columns, including arbitrary helper and target dirt.
This fixture is a local support/cleanup identity, not the P104 supplier.

### A path in the actual P104 inputs

For PR3019's exact pairing, helper slot **201** is assigned arrival slot **197**.
Its dimension-one line is `span(483)`, departure plane is `span(8,483)`, and
arrival hyperplane is `span(3,5,8,16,64,160,256)`. Choose its intermediate
frames as follows (binary vectors are decimal integers in `F_2^9`):

| Dimension | Basis |
| --- | --- |
| 3 | `3,8,480` |
| 4 | `3,8,64,416` |
| 5 | `3,5,8,64,416` |
| 6 | `3,5,8,16,64,416` |
| 8 | `3,5,8,16,33,64,129,256` |

Together with the prescribed dimensions 1, 2 and 7, zero at dimension 0, and
the whole space at dimension 9, these are one nested full flag. Literal point
sets check every inclusion. Its endpoints are reconstructed directly from the
raw endpoint certificate and native word, separately from the interval parser.

A cut counts already-executed native-word events, starting at zero. After the
first **594** events, `X1` has exactly the dimension-four frame above. Transport
the new helper to that frame before this cut and perform `H201 -= X1/2` there.
Then transport it along the rest of the displayed flag to dimension eight;
after the original **4,058** events, `Y98` has that exact frame, so perform
`Y98 += H201`. Finish the helper's flag to dimension nine if required.
These insertions are chronologically ordered and use equal frames at both
ADDs; the original X value is immutable under the retained logical word.

The added response has coefficient `-1/2` from `X1` to `Y98`, which is the
required entry `C[98,1]`. The scaled E8 root rows are
`(0,0,0,0,0,2,0,2)` and `(2,0,0,0,0,0,0,2)`; their dot product is 4 and the
source formula gives `-4/8`. The legacy full-memory output omits this pair;
the single-break deletion includes it.

**Exact scope:** this two-ADD path retains arbitrary helper dirt in the output
and does not restore the helper. It is a counterexample to the reported
absence of a support path in a relaxation that already forgives restoration.
It is not a counterexample to an impossibility theorem requiring a complete
restored correction. Physical native compilation and owner hosting of the
inserted path are not supplied.

### Effect of deleting only the output break

The verifier imports the pinned predecessor unchanged. A checked AST transform
removes exactly the single `break` immediately following `outputs[t] |= 1 << s`;
all other propagation operations are retained. No frozen file is edited.

| Retained input | Legacy missing, either mode | Write-all only, one-step memory | Write-all only, full memory |
| --- | ---: | ---: | ---: |
| PR2981 | 4,781 | 4,395 | 4,397 |
| PR3013 | 4,783 | 4,253 | 4,257 |
| PR3019 | 4,783 | 4,247 | 4,251 |
| PR3124 cycle A | 4,783 | 4,248 | 4,252 |
| PR3182 cycle B **as encoded, incompatible** | 4,783 | 4,264 | 4,268 |

Counts refer to the 4,992 required correction entries. The last row is retained
only to reproduce the audited input, not as an admissible matching. Complete
write-all outputs are invariant under reversed enumeration in these five cases.
Legacy outputs happen also to be unchanged by that reversal on these inputs;
the tiny fixture, not this table, witnesses their general order dependence.
**The new counts are sensitivity measurements, not certified obstructions:**
this audit does not prove the remaining memory recurrence sound or complete.

## 2. The secondary cycle is reversed

PR3124's retained receipt records `[39,134,139,154]`. PR3182 applies
`[39,154,139,134]` instead. For the convention
`new_M[cycle[i]] = old_M[cycle[(i+1) % 4]]`, these are different matchings.
The actual PR3124 cycle is compatible. The reversed cycle has these failures:

| Departure slot | Arrival slot | Vector in departure, absent from arrival |
| ---: | ---: | ---: |
| 39 | 186 | 148 |
| 139 | 23 | 113 |
| 154 | 7 | 314 |

Both the inherited compatibility checker and literal subspace containment
reject those three pairs. Thus a census claiming valid nested flags on all four
reversed-cycle helpers is not a census of the actual PR3124 candidate. PR3124
already reports that its genuine secondary candidate fails helper 91's screen;
this input-binding correction supplies no surviving matching.

## 3. Fresh-read control and its limit

A generic two-helper layer with a read only at helper 0, an edge `0--1`, and
a write only at helper 1 loses a read-then-relay path in the legacy one-hop
routine. A separately written set recurrence, `read -> hop -> write`, retains
it. This tiny relation is **not a counterexample to the P104 interval model**.
There, reads include every untimed compatible source frame: if a fresh source
can be read and relayed at one actual frame, the receiving helper can itself
read that source in the optimistic model. That direct read already includes
the dependency. Hence delaying fresh reads across a relay is not by itself an
established defect of this frame-complete relaxation.

As a source-bound control, the complete one-hop output matrices are unchanged
by reading first on all five encoded cases and the pooled 2,309 edges. The
pooled result still misses exactly `(Y71,X102)`. The independent set recurrence
also agrees with a separate graph traversal on all **16,384** two-layer,
two-helper, two-source abstract fixtures with equal-frame partitions. These
controls do not independently reprove the entire pooled obstruction theorem.

## Reproduce and evidence

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/p104-support-propagation-audit
```

Expected verifier line:

```text
PASS_P104_SUPPORT_PROPAGATION_AUDIT tiny=2 matchings=5 path=X1-H201-Y98 pooled_missing=1 no_new_kappa
```

The registered command also runs eight behavioral test groups. Tests reject a
wrong source cut, wrong endpoint pairing, flipped required coefficient, missing
output support, reversed incompatible cycle and source-byte drift. The replay
checks [RESULT.json](RESULT.json) without modifying it; `verify.py --emit`
emits a candidate receipt to stdout. Direct `-I -O -B` replay keeps explicit
acceptance checks enabled. Source and control evidence is internally checked
with substantial AI assistance; no independent human or formal-kernel review
is claimed. Shared geometry and interval routines retain their original scope.

## Open next questions

1. Repair and prove the memory recurrence as a necessary support relaxation,
   then recompute its exclusions. First specify acquisition, same-layer
   propagation, carried subspace constraints and **all-source** output union;
   retain this literal path and the two-source fixture as required controls.
   This matters before a missing-pair number can reject a realization. Joint
   flags, coefficients and restoration remain separate obligations.
2. Correct the secondary-cycle binding before using PR3182's moved-slot census
   as evidence about PR3124. Start from PR3124's actual cycle receipt and reject
   incompatible endpoint pairs before enumerating flags. Its already reported
   helper-91 failure remains the relevant starting evidence.

The family decision is **narrow to the audit and stop**. No cheaper complete
physical bill has been established; no dependent search is justified here.
Coefficient synthesis, global simultaneous flags, arbitrary-dirty restoration
for the actual P104 path, native phases, precision, recursive hosting, full
consumer costs and selected cold replay are unchecked. The consumer invoices
and other single-helper exclusions in PR3182 are not recertified by this audit.
Structured scope and follow-ups are in [TASK.json](TASK.json).

## Credit and license

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0. OpenAI Codex performed this audit, implementation, checking and writing.

Credit dcharb78 / PR3182 for the audited routines and recorded comparisons;
Nick Petalas / PR2981, PR2996, PR3013 and PR3019 for endpoint covers, interval
contacts and matching witnesses; Ross Richardson / PR3032 for fixed-matching
flag consistency; and Cinna Davis / PR3124 for the short-cycle census and
retained cycle receipt, prepared with OpenAI Codex assistance. Credit Arham Tahir's independent
fixed-flag work and the retained Rohan Arun / PR1972, Chafik Boukhalfa / PR1991,
Adam Gall, Josie Elliston, Ali Romman and geometry/native/compiler lineage.
This account's earlier P104 lifetime, native, error and fusion contributions
are distinct; none is reconstructed or claimed anew here.
