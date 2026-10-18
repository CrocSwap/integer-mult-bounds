# Independent review of the one-buffer packet interface

The proposed one-buffer outer adapter is correct under the conditional
ownership and route contract below. It has **1,232 route calls, 626 packet
exchanges, and 2,191 packet-XOR units** for the pinned 303 ordinary events
and ten snapshot taps. These are complete outer-operation counts, not a
complete machine-work bound or an optimality result.

This review was derived separately from the package implementation. The
reviewer read PR2481's retained `README.md`, `PROOF.md`, and `verify.py` at
commit `d3ec95362a071e2726c5ff4ce587de80c7d4f984`, and the retained PR2448
contract and route implementation. The new verifier was inspected only after
the algebra and independent small witness were developed. PR2481's proof
SHA256 is `c1e62d864fdb9f2374a09eb487c07790f1ddcf610995400cc734f20d810cbfe4`.
The scientific checkout base is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.

## Precise contract and boundary proof

Let payloads belong to any F2-module, with arbitrary correlations between
all initial records. Each packet consists of P ordered records, P >= 1.
The target, ordinary source, snapshot, and one dirty bank occupy disjoint
storage. Target and source may belong to one family if their *complete*
owned packets are disjoint. PR2448's stronger complete-packet separation,
complete spectator volume, and common data-gauge premises remain required.

Each R_i is an exact coordinate permutation from the ordered owned packet i
to common order. This is a linear permutation of positions, not an arbitrary
nonlinear bijection of payload states. Every route and literal inverse acts
only on the active bank, preserves every parked original value and the
snapshot throughout its call, closes its private workspace, and returns its
heads. Arbitrary dirt temporarily parked in an original packet is included
in that exclusion. Headers and layout/controller descriptions are additional
known control state, not part of the arbitrary-dirty payload claim.

One new caller operation must be admitted: a synchronized scan that XORs a
bank in target-owner order into precisely those ordered target records, with
head restoration and no write to another packet. This is not supplied merely
by naming a relative chart; its scan and control costs must be paid.

Write U = R_i^-1 R_j, with the rightmost factor applied first. For an ordinary
event the exact state of `(target, source, bank)` is

```
(t, s, d)
  -> (t, d, s)             exchange source and bank
  -> (t, d, U s)           R_j, then R_i^-1, on bank
  -> (t + U s, d, U s)     direct target scan
  -> (t + U s, d, s)       R_i, then R_j^-1, on bank
  -> (t + U s, s, d).      exchange source and bank
```

The bank's route layouts are successively j, common, i, common, j. The
source is temporarily exchanged; continuous immutability of that source is
not satisfied. Each exchange is exactly three local XORs and needs no blank
payload. No second outer bank or target copy occurs. Every unowned record is
unchanged because exchange and update scans write only their owned indices,
and each route excludes the original family streams entirely.

For a snapshot tap, exchange target and bank, apply R_i, XOR the immutable
common snapshot s, apply R_i^-1, and exchange back. Linearity gives the exact
boundary `(t, d) -> (t + R_i^-1 s, d)` with s unchanged throughout. This
requires no relation between the snapshot value and another original source;
the external COPY contract supplies that relation when it is needed.

Both event maps are involutions in characteristic two, and their displayed
circuits equal their literal inverses with reversed primitive order. All
protected payload and bank invariants close after each event. Consequently
arbitrary chronological composition is valid, including later use of an
earlier target as a source; the reversed event list implements the inverse.
Neither this argument nor inventory equality allows a tap to move across an
intervening dependent shear.

## Costs in named resources

Let N_i be the full family length scanned to select packet i. Use PR2481's
tariff: an exchange traverses its family and bank forward once and returns
both heads, while performing all three XORs locally at each selected pair.
It costs `2 N_i + 2 P` record-head steps and three packet-XOR units. Thus a
packet-XOR unit measures P record XORs, not a separate physical head pass.

The new direct target scan costs `2 N_i + 2 P` head steps and one packet-XOR
unit. A bank/snapshot update costs `4 P` head steps, including both returns.
This gives:

| Per-event resource | One-buffer ordinary i <- j | PR2481 ordinary | Either snapshot tap |
| --- | ---: | ---: | ---: |
| Routes | 4 | 4 | 2 |
| Exchanges | 2 | 4 | 2 |
| Packet-XOR units | 7 | 13 | 7 |
| Outer record-head steps | 2N_i + 4N_j + 6P | 4N_i + 4N_j + 12P | 4N_i + 8P |

The ordinary route multiset is exactly `{R_i, R_i^-1, R_j, R_j^-1}` in both
adapters. Equal weighted route work follows when each route's tariff depends
only on its role, direction, and volume under the shared protected-storage
contract. A count alone would not prove that equality for context-dependent
implementations. The actual order and active-bank layout differ.

Summing the stated window gives `4*303 + 2*10 = 1232` routes,
`2*(303+10) = 626` exchanges, and `7*(303+10) = 2191` packet-XOR units.
PR2481 uses 1,232 exchanges and 4,009 such units. The new outer reservation
is one P-record dirty bank plus the existing P-record snapshot; headers,
control, and route-private workspace remain additional.

For the finite N_i = 3,888, P = 81 fixture, outer record-head steps are
7,377,642 versus PR2481's 9,881,028, a difference of 2,503,386. Record XORs
are 177,471 versus 324,729. The retained finite route programs have the same
11,752,454 declared route-head steps in either schedule. These record-level
tariffs do not meter controller computation, internal payload-bit scans,
parking, or a uniform recursive implementation.

## Independent finite witness and reviewed implementation

`independent.py` imports no package or predecessor implementation. It uses
all 216 triples of S3 coordinate permutations, including noncommuting pairs,
and three disjoint packets interleaved in one 11-record physical family.
Two family guard records, the three-record snapshot, and the three-record
dirty bank are included among 17 distinct formal input atoms. The route
interpreter uses in-place cycle transpositions lowered to three XORs; the
oracle instead reads the direct index `R_j^-1(R_i(k))`. It checks every family
record and all protected boundary values after each event.

A six-event chronological word and its reverse give 2,592 checked event
boundaries over the 216 chart triples. Formal linear expressions establish
all bit assignments and correlations on this finite domain by substitution.
Seven controls detect dirty-copy substitution, omitted exchange-back,
reversed relative-factor order, reversed return-factor order, unowned writes,
transient snapshot borrowing despite final snapshot restoration, and a
count-preserving tap moved across the wrong cut. In particular, the factor
controls test semantic failure even when an erroneous layout label is ignored.

The independent witness passed under both ordinary and optimized Python:

```sh
python3 -I -B research/r439-one-buffer-packet/independent.py
python3 -I -O -B research/r439-one-buffer-packet/independent.py
```

It does not independently replay the source-bound 313-event GL2(Z/9) window.
That larger replay deliberately reuses the credited PR2448 constructor and
route compiler through PR2481. Inspection of the new `verify.py` confirms
that it uses one mutable outer payload bank, checks event targets via direct
full-ring multiplication, checks source/bank restoration after each event,
and compares all family cells at the final boundary. Its stored observer
tuples are verification data, not algorithm workspace. `current_low` is a
layout annotation; it cannot be counted as restored arbitrary-dirty header
storage. An implementation that stores such headers must separately provide
their reversible maintenance and cost.

At 2026-10-15 13:18 UTC the reviewer separately replayed the stable primary
verifier with `/opt/homebrew/opt/python@3.14/bin/python3.14` (Python 3.14.6,
Clang 21.0.0). The exact command, from this checkout, was:

```sh
/opt/homebrew/opt/python@3.14/bin/python3.14 -I -B research/r439-one-buffer-packet/verify.py
```

The result was `PASS_R439_ONE_BUFFER_PACKET`, with 313 events, 1,232 routes,
626 exchanges, 2,191 packet-XOR units, one dirty bank, and eight controls.
SHA256 before and after the completed replay was exactly
`3b5d1737a0a78a2b95b6717241a0b80d400ffa4048d6209910a7bda7be620d09`.
The replay includes separate forward/reverse receipt equality and comparison
of six route counters against the pinned PR2481 receipts in each direction.
This is a separate execution and inspection of the shared primary finite
engine, not an independent implementation of its source constructor, route
compiler, or complete GL2(Z/9) endpoint. The independently written test above
has its explicitly smaller S3 domain. These reviewer executions used Python
3.14.6; they are not claims of reviewer execution under Python 3.12.

## Remaining implications and credit

This is an all-size written conditional payload proof plus a separate exact
finite witness, not a formal-kernel proof. No blocker was found for the stated
outer adapter. The route contract, synchronized owned-record predicates and
direct update, reversible controls, private scratch, complete spectators,
source parking, and snapshot COPY/ERASE transports remain caller/backend
obligations. A uniform GL64 route implementation, rounded or integer
implementation, full supplier recurrence, optimality, and a larger kappa do
not follow. Historical output-borrowing results do not admit parked original
packets as descendant scratch; that exclusion is retained here.

PR2481 (ywz65) supplies the restored two-buffer comparator and ownership
contract; PR2448 supplies the credited finite packet compiler and the
fresh/dirty boundary; PR2407 supplies the literal interleaving. PR2195 supplies
the earlier packet/owner routing foundation. The standard XOR exchange is
not claimed as new mathematics. Prepared by Ross Richardson with substantial
OpenAI Codex assistance in a separate recursive-interface review agent. This
is independent AI-assisted derivation and implementation, not independent
human review. New review text and witness are Apache-2.0.
