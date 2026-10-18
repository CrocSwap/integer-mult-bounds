# A 144-call connector for every seven-source mask of weight at most three

**Finite construction with an all-dimension linear identity; no new κ.**
The following closed source word supports all 63 nonzero seven-bit masks of
Hamming weight one, two or three:

```text
0 1 2 3 1 0 4 2 0 5 1 4 1 6 5 0 3 6
```

Its 18 source calls and 126 output calls give **144 complete calls**. This
attains the lower boundary left open by Cinna Davis's
[PR #2236](https://github.com/CrocSwap/integer-mult-bounds/pull/2236), following
[PR #2229](https://github.com/CrocSwap/integer-mult-bounds/pull/2229).
Their smaller-path exclusions are credited, not claimed as new. The full
predecessor checker was rerun successfully at its pinned head during this
contribution; the short new replay checks the attaining construction.

The independent per-output stars use 434 complete calls for this same full
batch. The new schedule saves 290 source calls, while keeping every output
call paid. No selected-supplier caller, physical runtime gain or multiplication
exponent change is established.

## Exact interface and literal certificate

Use the [fixed connector contract](../universal-connector-boundary/README.md):
seven distinct immutable source rows `x_j`, 63 distinct target rows `y_m`, and
one connector `z`, all arbitrarily dirty over F2. For each nonzero mask `m`
of weight at most three, the required update is

```text
y_m += A_m(sum_{j: m_j=1} B_j x_j),   with every x_j and z preserved.
```

The maps `B_j` and `A_m` are arbitrary fixed compatible F2-linear maps. They
need not commute or be invertible. The only root operations are complete
additive calls `B_j: z += B_j x_j` and `A_m: y_m += A_m z`. Each call preserves
all other data rows, restores its private scratch, returns its heads, and is
independent of old target contents. Data rows and `z` cannot be child scratch.
Targets are observed only after the batch. There are no combined queries,
extra root connectors, free frame changes, copies or overwrites.

[CERTIFICATE.json](CERTIFICATE.json) contains the word, all 63 boundary pairs,
and the full 144-event chronological stream. Source bit `j` has value `2^j`.
Target identifiers `0..62` refer to masks in increasing numerical order.
A boundary counts completed source calls; boundary zero precedes the word.
The prefix parities are

```text
0 1 3 7 15 13 12 28 24 25 57 59 43 41 105 73 72 64 0
```

Every required mask is the XOR of two listed prefixes. For example, mask 44
has a pair in the certificate even though it is missing from #2236's best
16-event word. The exact pairs are verified both by prefix XOR and by direct
XOR of the intervening singleton source events.

## Why the construction works for arbitrary maps and dirty inputs

Let `q_t` be the parity after the first `t` source calls. Induction gives

```text
z_t = z_initial + sum_j q_t[j] B_j x_j.
```

For the pair `(s,t)` assigned to mask `m`, linearity and characteristic two
give

```text
A_m z_s + A_m z_t = A_m(sum_j (q_s[j]+q_t[j]) B_j x_j)
                  = A_m(sum_{j: m_j=1} B_j x_j).
```

Thus connector dirt cancels from the increment; the target's original dirty
value is retained. Calls for different targets commute because they change
distinct targets and leave `z` unchanged. Every source count is even:
`(4,4,2,2,2,2,2)`. Therefore the connector is restored. This proves the
identity at every compatible vector dimension. Finite matrix checks below
are controls, not a replacement for this argument.

The statement does not extend to nonlinear readouts or ordinary positive
addition in odd characteristic. The test file supplies counterexamples to
both extensions. Specialized maps or inputs may permit cheaper schedules;
the optimality statement concerns one schedule valid for arbitrary maps.

## Why this reaches the unit-call minimum

The parity argument from #943 forces every active source map and every
required target map to occur a positive even number of times. Hence the first
possible total is `14+126=140`. Cinna Davis's #2229 census proves that a
14-source-call path supports at most 56 of the 63 masks by paired readouts.
The #2236 census proves that a 16-source-call path supports at most 60.

At 142 calls there are only two splits: `16+126`, excluded by the 60-mask
bound, and `14+128`. In the second split, only one target can receive four
readouts; at least six of the seven masks missing a pair remain unsupported.
The same argument excludes 140, and odd totals cannot restore arbitrary dirt.
Our 144-call upper witness therefore meets their lower bound in this exact
alphabet. It is not a minimum over other alphabets, extra connectors or
arbitrary weighted prices.

The unmodified #2236 checker at head
`be03870d764e7875ea9a9f6cc69933c9b1a2456a` was run with Python 3.12.3 and `-I -O -B`.
It completed 135,135 old paths (maximum 56), 18,918,900 new paths (maximum 60,
eight maximizers), and its four controls. The exact predecessor hashes are in
[SOURCES.json](SOURCES.json). This is a replay of their implementation, not a
new independent implementation of the lower census. Its existing command is
`python3 -I -O -B research/seven-source-16event-connector-seeda7de5e/verify.py`
on that pinned PR head. It is not imported by the new package.

## Complete invoice in the declared interface

Each source belongs to `1+6+15=22` requested masks. Separate closed stars
therefore use 44 calls to every `B_j` and two to every `A_m`.

| Charge | Shared word | Separate stars |
|---|---:|---:|
| Complete source calls | 18 | 308 |
| Complete output calls | 126 | 126 |
| Total complete calls / root dispatches | 144 | 434 |
| Root descriptor bits | 954 | 2114 |

A descriptor uses one opcode bit plus a three-bit source or six-bit target
identifier. Event order supplies chronology, so no runtime boundary-search
oracle is used. The mask family and target numbering are fixed, and common
operator metadata is admitted in both programs. The certificate's JSON byte
size is not this binary instruction-storage bill.

Let `c(B_j)` and `c(A_m)` be complete fixed-port call prices, `lambda>=0` the
cost per stored descriptor bit, `delta>=0` the root-dispatch price, `I` common
admission and `P` common one-time coefficient preparation. Then

```text
C_shared = I+P + 4(c(B0)+c(B1)) + 2 sum_{j=2..6} c(Bj)
           + 2 sum_m c(Am) + 954 lambda + 144 delta.
C_stars  = I+P + 44 sum_j c(Bj) + 2 sum_m c(Am)
           + 2114 lambda + 434 delta.
C_shared-C_stars = -40(c(B0)+c(B1)) -42 sum_{j=2..6} c(Bj)
                   -1160 lambda -290 delta.
```

Each complete price includes source/coefficient access, arithmetic, target
updates, private-scratch restoration, hosting, required frames and head return.
No root copy or frame operation is added. A physical caller requiring other
conversions must pay those separately before using this comparison. The new
schedule is componentwise cheaper than these stars under the stated common
admission/complete-call premises. This is not a global weighted optimum.

For a concrete composed-map fixture, source factor lengths are `(1,2,3,4,1,2,3)`
and target factor length is its mask weight. A balanced dirty echo compiles
each product into primitive additive calls, with
`ell(1)=1`, `ell(d)=2ell(floor(d/2))+2ell(ceil(d/2))`.
The shared and star programs use **984 and 2906 primitive leaf calls**,
respectively. Two private dirty rows suffice in this fixture, in addition to
the root connector; all 70 source/target rows stay reserved. The verifier checks
every one of the 144 child return boundaries, not just final scratch cleanup.
This fixture does not provide an implementation of a selected supplier.

## Replay and evidence

Python 3.12 standard library; default replay is read-only and requires no Git
or network. The metadata wrapper additionally checks historical Git provenance.

```sh
python3 -I -O -B research/seven-source-18event-connector/verify.py
python3 -I -O -B research/seven-source-18event-connector/test_verify.py
python3 scripts/research_package.py --package research/seven-source-18event-connector
```

Expected primary marker:

```text
PASS_SEVEN_SOURCE_18EVENT masks=63 source_calls=18 target_calls=126 total=144 controls=10
```

The checker compares the entire [RESULT.json](RESULT.json). It verifies the
literal root stream over free noncommuting operator words, the fully expanded
leaf stream, their inverses, the independent-star baseline, and all 73 arbitrary
input rows. A separate dense GF2 interpreter checks 438 forward and 438 inverse
basis cases in dimensions 1, 2, 3, including dirty private rows.

Ten in-package controls reject omitted source restoration, omitted readout,
wrong source/target maps, reversed noncommuting factors, omitted primitive
cleanup, invalid boundary, missing mask, wrong chronology and scratch alias.
The six tests also check all 36 cyclic/reversal variants, nonuniform invoices,
the two scope counterexamples, strict JSON types, Git-free relocation, and
four on-disk failure cases (receipt, certificate, source, occupied output).
`--out NEW.json` regenerates a receipt only at an unoccupied path.

Discovery used a bounded heuristic search with random seed 2236. It found a
full cover after 89,042 candidate swaps; cyclic rotation, reversal and source
renaming give the displayed word. Heuristic completeness is neither needed
nor claimed: the explicit witness and exact replay establish the upper bound.
The other 18-event multiplicity profile remains unresolved here.

## Open next questions

1. **Does `(6,2,2,2,2,2,2)` also attain all 63 masks?** A witness could improve
   weighted cost when one source is particularly cheap. Start with a bounded
   search on that exact profile, then an exact certificate or a complete census
   if practical. The blocker is full coverage; the present two-four-use witness
   does not answer it. No weighted optimality follows from the unit-call result.
2. **Which concrete caller has this 63-mask demand and complete-call contract?**
   Pin one caller's source/target ports, inspect observation cuts and scratch
   exclusions, then compare fully charged physical words. The blocker is an
   actual interface binding; no selected supplier is known to instantiate it.

## Scope, source pins and credit

The claim is in [Discussion #2221](https://github.com/CrocSwap/integer-mult-bounds/discussions/2221#discussioncomment-18942820), taking its released handoff.
Task `connector-alphabet-change` has explicitly **changed** scope: the original
alphabet is retained, and the contribution is attainment of its first open
seven-source sparse-batch call boundary. This is a side result for the recursive
interface, not completion of the catalogue's changed-operation construction
gate. Base main is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
No selected word, frontier, predecessor package or shared tool is changed.

Credit Cinna Davis (#2229/#2236) for the seven-source weight123 question, both
smaller-path exclusions, complete-call pricing and the explicit 144-call handoff;
Ross Richardson (#934/#943) and the retained dirty-commutator lineage for the
connector contract, prefix criterion and recursive echo. PR2282's 127-mask,
multiple-root minimum and PR2146's six-source TRIO question are distinct.
The new work supplies the 18-event attaining word, its readout assignment,
expanded executable check and complete invoice.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Codex performed discovery, proof, implementation, checking and writing. Evidence
is author-checked; no independent human review or proof-assistant verification
is claimed. New work is Apache-2.0. The retained lineage includes @shhxera/@CubeJerry (#889) and Chafik Boukhalfa (#628); their attribution is preserved.
Native supplier integration, global moment/owner pricing, precision/tape/all-size
admission, selected cold replay and a full multiplication theorem are not checked.
