# Literal canonical padded-rotation switch queries

A fixed14-tape program computes the exact canonical Beneš row-j bit at the
current wire address for a padded modular rotation. It implements the first
physical-predicate open question in Nick Petalas's #7504, exact head
4eece58f5cebdb70a92d65447974f1c02383f60b. The predecessor's arithmetic
formulas and child theorem remain credited dependencies.

For every legal h,s,a,j,x on the explicit ABI, the2096-location program uses
at most1024(h+3)^2 local transitions and16(h+4) additional historical cells.
All five borrowed descriptors remain unchanged; all14 heads and eight private
bodies/guards return. One bit remains in its original separate owned output.

PROOF.md gives the all-height induction, ABI, complete bounds, failure
boundary and ROM-reuse comparison. switch.py emits the fixed graph;
hardware.py is verifier hardware only. SOURCE-PINS.json authenticates exact
original sources. NOTICE.md and LICENSE retain attribution.

## Reproduction

From this directory:

```sh
python3 -I -W error -B verify.py
python3 -I -W error -B -O verify.py
```

Expected marker: `PASS_LITERAL_CANONICAL_ROTATION_SWITCH`. Default replay
is read-only; `--receipt /absolute/output.json` saves a generated receipt.
For the installed package:

```sh
python3 -B scripts/research_package.py --package research/literal-canonical-rotation-switch
```

Normal/optimized primary receipts agree. They cover1566 entries of49 complete
networks through h3, all544 h5,s17,j6 queries,13 malformed/domain rejections,
three detected child/parity graph mutants, one alias rejection and full-depth
half-turns through h129. Each checks every original buffer, private capacity,
head, guard, opaque exterior and observed historical span. The544 separate
query executions total1473152 transitions,max2969; host fixture serialization
is excluded, so this is not an uninterrupted caller or a ROM speedup.

## Remaining interfaces

Height is positive canonical LSB binary; s,a,j,x each use exactlyh+1 LSB bits.
Actual current CRT offset production, serialization, source transport and
consecutive current-wire payload updates remain caller work. Input owners and
blank working windows must be genuinely disjoint, with unique LEFT framing.
Guard corruption and infinite streams are outside the recovery promise.

Repeated point queries pay their full quadratic bill. ROM reuse can win
after amortization; no global workload improvement is asserted. The selected
conditional kappa remains0.00363005817 and all five assumptions remain.

## Open next questions

1. Bind the literal query to an actual current CRT source and numerical offset lease, including descriptor conversion, current-wire update and output retirement.
2. Compare complete repeated-query workloads with a retained ROM, paying construction, transport, disposal and actual reuse.

REVIEW.md and INDEPENDENT-RESULT.json record separate universal proof, sparse-interpreter and canonical-network checks. All five assumptions and the selected kappa remain unchanged.
