# Borrow the external source at a fixed dirty-row cap

**Scoped recursive-interface construction; no new kappa.** Allowing descendants
to borrow the external source, with exact restoration on return, fits the known
four-way additive echo into **three extra dirty rows**. The source, output and
three helpers occupy five rows in total. The source must be exclusively owned
and unobserved until the call returns.

At this same cap, the unit leaf bill falls **1,040 to 928** for 51 factors,
and **1,248 to 1,088** for the predecessor's 56-factor count. Both counts include
every inverse and restoration leaf. The comparison uses a stronger protected
baseline than PR1057's binary/ternary allocator: it also admits four-way nodes
where the protected source is an immediate port. Both optima are restricted
to the stated ordered arity-2/3/4 templates and unit leaf prices.

The fixed-factor interface matters. Opening the dense toy factors and
precomputing their product gives a different algorithm. No arbitrary-circuit
optimum or practical runtime gain is claimed. No compatible selected-supplier
call has been identified.

## Reproduce

From the repository root, using Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/mutable-source-port-borrowing
```

Expected:

```text
PASS_MUTABLE_SOURCE_PORT_BORROWING seed=51 rows=5 n51=1040->928 n56=1248->1088 controls=11 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/mutable-source-port-borrowing outcome=completed
```

The standalone `python3.12 -B research/mutable-source-port-borrowing/verify.py`
also works in a source export without Git. It authenticates copied predecessor
bytes and recomputes the certificate without writing files. The registered
runner additionally authenticates the base catalogue and selected context
from Git. Normal verification does not regenerate frozen evidence.

## Changed contract and strongest same-cap comparator

[PR1057](https://github.com/CrocSwap/integer-mult-bounds/pull/1057), by Gareth
Davidson (@bitplane), permits exact additive children to borrow ancestor ports
but protects the external source at every prefix. Its binary/ternary allocator
uses three extra dirty rows. [PR1164](https://github.com/CrocSwap/integer-mult-bounds/pull/1164),
by woklerx, combines that interface with the known four-way echo, using four
extra dirty rows. Neither predecessor claims a universal scratch lower bound.

Here the external source joins the pool. Every complete child still restores
all rows except its target; its source can change inside descendants. This is
a changed caller contract. The new [proof](PROOF.md) gives the restoration
induction and three exact recurrences. Type T has both ports in the mutable
pool and arity at most three. Type R starts at protected row zero: its first
child is R and its other children T, with root arity at most four. Type M can
borrow all five rows, so every node permits arity four.

| Factors | PR1057 type T | Stronger protected R | Mutable M |
|---:|---:|---:|---:|
| 51 | 1,328 | 1,040 | 928 |
| 56 | 1,568 | 1,248 | 1,088 |

The complete T table and tie-broken trees agree with frozen PR1057 code.
The 1,088 count corroborates PR1164's known four-way count; achieving it with
one fewer dirty row is the changed interface. Echo identities, higher-arity
optimization, ancestor borrowing and the modular backend retain predecessor
credit. Exact source heads/bytes are in [PREDECESSORS.json](PREDECESSORS.json).

## Complete finite invoice

The backend follows Gareth Davidson's
[PR1159](https://github.com/CrocSwap/integer-mult-bounds/pull/1159): exact matrix
shears modulo 2^w, paying every multiply, add, reduction, source/coefficient
read, target write, private clear and data-head return. Source and initial
output bounds of seven give w=55 at n=51 and w=60 at n=56. Helpers may contain
arbitrary w-bit dirt. The two comparators use the same width and five rows.

| Quantity | n=51 R | n=51 M | n=56 R | n=56 M |
|---|---:|---:|---:|---:|
| Complete leaves | 1,040 | 928 | 1,248 | 1,088 |
| Scalar/access commands, including startup | 39,524 | 35,268 | 47,428 | 41,348 |
| Counted data-head moves in bits | 51,240,320 | 48,673,408 | 75,610,368 | 68,448,768 |
| Program storage/read bits | 13,520 | 12,064 | 16,224 | 14,144 |
| Data bits, including source/output | 550 | 550 | 600 | 600 |
| Private scalar bits | 278 | 278 | 303 | 303 |

These are exact macro/address counts, not measured runtimes. Planning,
coefficient preparation, input encoding, final decoding, program construction,
control, scalar bit arithmetic and physical adapters have explicit paid terms
in [PROOF.md](PROOF.md). A common planner may produce both plans, assigning the
same planning charge to both; planning is not free or assumed cached. A host
needing a protective source copy must add that full row and its work, losing
the advertised same-cap comparison.

## Verification scope

[CERTIFICATE.json](CERTIFICATE.json) contains exact plans, matrices, dirty
states, word hashes, invoices and coverage. The code-disjoint oracle checks:

- All 1,099 ordered trees through seven factors, including 1,013 protected
  trees; both signs and inverse: 4,224 word checks, 670,800 formal leaf events.
- All 20 immediate-port pairs for every tree through five factors: 2,400
  signed word checks, 133,200 formal leaf events.
- All T/R/M values through 56 with a separate min-plus path algorithm
  (423,447 transitions), alongside primary composition enumeration.
- 2,376 literal modular basis/dirty cases across dimensions 1–3, three widths,
  six factor counts and both policies/signs: 5,218,512 scalar/access commands.
  An additional 1,024 cases cover every scalar dirty state over Z/4Z for one
  11-factor word.
- Six 51/56-factor fixtures, noncommutative free-module identities, both
  orientations, dense integer/residue replay and exact signed recovery.

Eleven controls cover missing work, wrong signs/order, omitted source writes,
protected-port exhaustion, aliases, duplicated factors, invalid signs,
mid-call observation, nonlinear restoration and undersized recovery. The
nonlinear control changes a helper from 6 to 4 modulo 16 although the literal
inverse reverses the whole program. Reversibility alone is insufficient.

These exact finite word identities support the written all-tree induction;
finite enumeration is not formal verification of that induction or the full
multiplication theorem. Both implementations were written in the same
AI-assisted session; there is no independent human review.

## Provenance and limitations

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The selected conditional
result is PR1094, kappa `836330098538459/500000000000000000`; its source bindings,
actual assembly and review were inspected. The complex supplier binds.
The selected cold replay is `make frontier1094-verify`; it is not claimed for
this additive package. Selected certificates, suppliers, historical evidence,
review ledger and `upstream/` are unchanged.

OS assignment seed 51 selected recursive interfaces and the 51-factor fixture.
There is no randomized optimizer: the stated template and bounded tree domains
are exhausted deterministically. Seeded matrix/dirt cases are supplementary
fixtures, not a universal matrix census. [TASK.json](TASK.json) records the
scope change from a consecutive-call pilot, the 60-minute cap and stop rule.

[Discussion1505](https://github.com/CrocSwap/integer-mult-bounds/discussions/1505)
records the claim. Initial overlap coverage included 750 open PRs and complete
paginated discussion records, followed by a fresh latest-claim check.
Source/reader mutation (Discussion1489/PR1439) and shared multi-output source
tours (Discussion1493) were rejected as overlapping alternatives. PR1488
changes output frames; this package changes source ownership inside recursion.
Final refresh coverage is in OVERLAP.json. No literature-priority claim is made.

The inherited direct all-role adapter remains noncontracting at saving zero:
N>=4n-4 for n>=2 gives `3N/(2n) >= 3`; this M51 fixture gives `464/17 > 1`.
No new kappa follows. Source ownership, physical hosting/frames, all-size
compilation, nonmodular precision and analytic transfer remain uninstantiated
for an actual supplier.

## Open next questions

The structured questions are in [TASK.json](TASK.json). First identify one real
supplier call without source observers or aliases at the emitted write cuts.
No such interval or owner map is established here. Only then would its actual
child ranks, adapters and complete moment merit pricing. Repeating the closed
direct all-role adapter search is not justified by this result.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in derivation, both implementations, verification and prose. New work is
Apache-2.0. [NOTICE.md](NOTICE.md) retains predecessor credit and disclosures.
